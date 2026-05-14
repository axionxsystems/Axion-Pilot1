"""
Stripe Webhook Handler - Process Stripe events securely.
Validates webhook signature and handles subscription/payment events.
"""
import stripe
import json
from fastapi import APIRouter, Request, HTTPException, status, Depends
from sqlalchemy.orm import Session
import logging
from typing import Dict, Any

from app.core.stripe_config import STRIPE_WEBHOOK_SECRET, WebhookEventType
from app.database import get_db
from app.services.stripe_service import (
    StripeCustomerService, StripeSubscriptionService, StripeInvoiceService,
)
from app.models.stripe_billing import StripeCustomer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


# ── Webhook Signature Verification ────────────────────────────────────────────

def verify_webhook_signature(request_body: bytes, signature: str) -> Dict[str, Any]:
    """
    Verify Stripe webhook signature and return event data.
    
    This is CRITICAL for security: ensures events actually come from Stripe.
    """
    try:
        event = stripe.Webhook.construct_event(
            request_body, signature, STRIPE_WEBHOOK_SECRET
        )
        return event
    except ValueError:
        logger.warning("Invalid webhook signature")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature",
        )
    except stripe.error.SignatureVerificationError:
        logger.warning("Signature verification failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Signature verification failed",
        )


# ── Webhook Endpoint ──────────────────────────────────────────────────────────

@router.post("/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Main Stripe webhook endpoint.
    
    Handles:
    - customer.created, customer.updated, customer.deleted
    - customer.subscription.created, customer.subscription.updated, customer.subscription.deleted
    - invoice.created, invoice.payment_succeeded, invoice.payment_failed, invoice.paid
    - payment_intent.succeeded, payment_intent.payment_failed
    
    All operations are idempotent to handle retries safely.
    """
    
    # Get raw body and signature
    body = await request.body()
    signature = request.headers.get("stripe-signature")
    
    if not signature:
        logger.warning("Webhook missing Stripe signature header")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Stripe signature",
        )
    
    # Verify signature
    event = verify_webhook_signature(body, signature)
    event_type = event.get("type")
    event_data = event.get("data", {}).get("object", {})
    
    logger.info(f"Received Stripe webhook: {event_type}")
    
    try:
        # ── Customer Events ───────────────────────────────────────────────────
        if event_type == WebhookEventType.CUSTOMER_CREATED.value:
            await handle_customer_created(db, event_data)
        
        elif event_type == WebhookEventType.CUSTOMER_UPDATED.value:
            await handle_customer_updated(db, event_data)
        
        elif event_type == WebhookEventType.CUSTOMER_DELETED.value:
            await handle_customer_deleted(db, event_data)
        
        # ── Subscription Events ───────────────────────────────────────────────
        elif event_type == WebhookEventType.SUBSCRIPTION_CREATED.value:
            await handle_subscription_created(db, event_data)
        
        elif event_type == WebhookEventType.SUBSCRIPTION_UPDATED.value:
            await handle_subscription_updated(db, event_data)
        
        elif event_type == WebhookEventType.SUBSCRIPTION_DELETED.value:
            await handle_subscription_deleted(db, event_data)
        
        # ── Invoice Events ────────────────────────────────────────────────────
        elif event_type == WebhookEventType.INVOICE_CREATED.value:
            await handle_invoice_created(db, event_data)
        
        elif event_type == WebhookEventType.INVOICE_PAYMENT_SUCCEEDED.value:
            await handle_invoice_payment_succeeded(db, event_data)
        
        elif event_type == WebhookEventType.INVOICE_PAYMENT_FAILED.value:
            await handle_invoice_payment_failed(db, event_data)
        
        elif event_type == WebhookEventType.INVOICE_PAID.value:
            await handle_invoice_paid(db, event_data)
        
        # ── Payment Intent Events ─────────────────────────────────────────────
        elif event_type == WebhookEventType.PAYMENT_INTENT_SUCCEEDED.value:
            await handle_payment_intent_succeeded(db, event_data)
        
        elif event_type == WebhookEventType.PAYMENT_INTENT_PAYMENT_FAILED.value:
            await handle_payment_intent_failed(db, event_data)
        
        else:
            logger.info(f"Unhandled event type: {event_type}")
        
        return {"status": "success", "event_type": event_type}
        
    except Exception as e:
        logger.error(f"Error processing webhook {event_type}: {e}", exc_info=True)
        # Return 200 anyway to avoid Stripe retries for non-recoverable errors
        return {"status": "error", "message": str(e)}


# ── Customer Event Handlers ───────────────────────────────────────────────────

async def handle_customer_created(db: Session, event_data: Dict[str, Any]) -> None:
    """Handle customer.created event."""
    stripe_customer_id = event_data.get("id")
    email = event_data.get("email")
    metadata = event_data.get("metadata", {})
    org_id = metadata.get("org_id")
    
    if not org_id:
        logger.warning(f"Customer {stripe_customer_id} created without org_id in metadata")
        return
    
    # Check if already in DB
    existing = db.query(StripeCustomer).filter(
        StripeCustomer.stripe_customer_id == stripe_customer_id
    ).first()
    
    if existing:
        logger.info(f"Customer {stripe_customer_id} already in DB")
        return
    
    logger.info(f"Creating customer {stripe_customer_id} for org {org_id}")


async def handle_customer_updated(db: Session, event_data: Dict[str, Any]) -> None:
    """Handle customer.updated event."""
    stripe_customer_id = event_data.get("id")
    email = event_data.get("email")
    
    customer = db.query(StripeCustomer).filter(
        StripeCustomer.stripe_customer_id == stripe_customer_id
    ).first()
    
    if customer:
        customer.email = email
        customer.stripe_metadata = event_data.get("metadata", {})
        db.commit()
        logger.info(f"Updated customer {stripe_customer_id}")


async def handle_customer_deleted(db: Session, event_data: Dict[str, Any]) -> None:
    """Handle customer.deleted event."""
    stripe_customer_id = event_data.get("id")
    
    customer = db.query(StripeCustomer).filter(
        StripeCustomer.stripe_customer_id == stripe_customer_id
    ).first()
    
    if customer:
        # Mark as inactive rather than deleting for audit trail
        from app.models.stripe_billing import StripeCustomerStatus
        customer.status = StripeCustomerStatus.inactive
        db.commit()
        logger.info(f"Marked customer {stripe_customer_id} as inactive")


# ── Subscription Event Handlers ───────────────────────────────────────────────

async def handle_subscription_created(db: Session, event_data: Dict[str, Any]) -> None:
    """
    Handle customer.subscription.created event.
    Triggered when user completes checkout and subscription is created.
    """
    stripe_subscription_id = event_data.get("id")
    org_id = event_data.get("metadata", {}).get("org_id")
    
    if not org_id:
        logger.warning(f"Subscription {stripe_subscription_id} created without org_id")
        return
    
    logger.info(f"Creating subscription {stripe_subscription_id} for org {org_id}")
    
    try:
        StripeSubscriptionService.save_subscription(db, org_id, event_data)
    except Exception as e:
        logger.error(f"Error saving subscription: {e}")


async def handle_subscription_updated(db: Session, event_data: Dict[str, Any]) -> None:
    """
    Handle customer.subscription.updated event.
    Triggered on plan changes, payment method updates, etc.
    """
    stripe_subscription_id = event_data.get("id")
    org_id = event_data.get("metadata", {}).get("org_id")
    
    if not org_id:
        logger.warning(f"Subscription {stripe_subscription_id} updated without org_id")
        return
    
    logger.info(f"Updating subscription {stripe_subscription_id} for org {org_id}")
    
    try:
        StripeSubscriptionService.save_subscription(db, org_id, event_data)
    except Exception as e:
        logger.error(f"Error updating subscription: {e}")


async def handle_subscription_deleted(db: Session, event_data: Dict[str, Any]) -> None:
    """Handle customer.subscription.deleted event."""
    stripe_subscription_id = event_data.get("id")
    org_id = event_data.get("metadata", {}).get("org_id")
    
    if not org_id:
        logger.warning(f"Subscription {stripe_subscription_id} deleted without org_id")
        return
    
    logger.info(f"Deleting subscription {stripe_subscription_id} for org {org_id}")
    
    try:
        StripeSubscriptionService.save_subscription(db, org_id, event_data)
    except Exception as e:
        logger.error(f"Error deleting subscription: {e}")


# ── Invoice Event Handlers ────────────────────────────────────────────────────

async def handle_invoice_created(db: Session, event_data: Dict[str, Any]) -> None:
    """Handle invoice.created event."""
    stripe_invoice_id = event_data.get("id")
    logger.info(f"Invoice created: {stripe_invoice_id}")
    
    try:
        StripeInvoiceService.save_invoice(db, event_data)
    except Exception as e:
        logger.error(f"Error saving invoice: {e}")


async def handle_invoice_payment_succeeded(db: Session, event_data: Dict[str, Any]) -> None:
    """
    Handle invoice.payment_succeeded event.
    Payment has been successfully charged.
    """
    stripe_invoice_id = event_data.get("id")
    org_id = event_data.get("metadata", {}).get("org_id")
    amount = event_data.get("amount_paid", 0)
    
    logger.info(
        f"Invoice payment succeeded: {stripe_invoice_id} for org {org_id}, "
        f"amount: {amount / 100}€" if event_data.get("currency") == "eur" else f"${amount / 100}"
    )
    
    try:
        invoice = StripeInvoiceService.save_invoice(db, event_data)
        
        # TODO: Send confirmation email to customer
        # TODO: Update accounting system
        # TODO: Log to audit trail
        
    except Exception as e:
        logger.error(f"Error handling invoice payment: {e}")


async def handle_invoice_payment_failed(db: Session, event_data: Dict[str, Any]) -> None:
    """
    Handle invoice.payment_failed event.
    Payment attempt failed — customer needs to update payment method.
    """
    stripe_invoice_id = event_data.get("id")
    org_id = event_data.get("metadata", {}).get("org_id")
    
    logger.warning(f"Invoice payment failed: {stripe_invoice_id} for org {org_id}")
    
    try:
        StripeInvoiceService.save_invoice(db, event_data)
        
        # TODO: Send "payment failed" email with retry link
        # TODO: Mark subscription as past_due if retries exceeded
        
    except Exception as e:
        logger.error(f"Error handling invoice payment failure: {e}")


async def handle_invoice_paid(db: Session, event_data: Dict[str, Any]) -> None:
    """Handle invoice.paid event."""
    stripe_invoice_id = event_data.get("id")
    logger.info(f"Invoice marked as paid: {stripe_invoice_id}")
    
    try:
        StripeInvoiceService.save_invoice(db, event_data)
    except Exception as e:
        logger.error(f"Error handling invoice paid: {e}")


# ── Payment Intent Event Handlers ─────────────────────────────────────────────

async def handle_payment_intent_succeeded(db: Session, event_data: Dict[str, Any]) -> None:
    """Handle payment_intent.succeeded event."""
    payment_intent_id = event_data.get("id")
    logger.info(f"Payment intent succeeded: {payment_intent_id}")
    
    # TODO: Update PaymentIntent record in DB


async def handle_payment_intent_failed(db: Session, event_data: Dict[str, Any]) -> None:
    """Handle payment_intent.payment_failed event."""
    payment_intent_id = event_data.get("id")
    logger.warning(f"Payment intent failed: {payment_intent_id}")
    
    # TODO: Update PaymentIntent record, notify user
