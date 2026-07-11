"""
Stripe Service: High-level Stripe API interactions and business logic.
Handles customer creation, subscriptions, webhooks, etc.
"""
import os
import io
import smtplib
import stripe
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

from app.auth.mailer import mailer
from app.core.stripe_config import (
    STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY, PricingTier, TIER_CONFIG,
    get_tier_by_price_id, get_tier_limits, DEFAULT_CURRENCY,
    CHECKOUT_SUCCESS_URL, CHECKOUT_CANCEL_URL, StripeErrorCode,
)
from app.models.stripe_billing import (
    StripeCustomer, StripeSubscription, UsageMetrics, Invoice,
    InvoiceLineItem, InvoicePayment, PaymentIntent, InvoiceStatus,
)
from app.models.organization import Organization
from app.models.branding import OrgBranding

# Configure Stripe
stripe.api_key = STRIPE_SECRET_KEY

logger = logging.getLogger(__name__)


# ── Customer Management ───────────────────────────────────────────────────────

class StripeCustomerService:
    """Handle Stripe customer creation and management."""
    
    @staticmethod
    def create_or_get_customer(
        db: Session,
        org_id: str,
        email: str,
    ) -> StripeCustomer:
        """
        Create or retrieve Stripe customer for organization.
        Returns StripeCustomer model instance.
        """
        # Check if customer already exists
        existing = db.query(StripeCustomer).filter(
            StripeCustomer.org_id == org_id
        ).first()
        
        if existing:
            logger.info(f"Stripe customer already exists for org {org_id}")
            return existing
        
        try:
            # Create in Stripe
            stripe_customer = stripe.Customer.create(
                email=email,
                metadata={"org_id": org_id},
            )
            
            logger.info(f"Created Stripe customer {stripe_customer.id} for org {org_id}")
            
            # Save to DB
            db_customer = StripeCustomer(
                org_id=org_id,
                stripe_customer_id=stripe_customer.id,
                email=email,
            )
            db.add(db_customer)
            db.commit()
            db.refresh(db_customer)
            
            return db_customer
            
        except stripe.error.StripeAPIError as e:
            logger.error(f"Stripe API error creating customer: {e}")
            raise


# ── Subscription Management ───────────────────────────────────────────────────

class StripeSubscriptionService:
    """Handle Stripe subscription creation, updates, and cancellation."""
    
    @staticmethod
    def create_checkout_session(
        db: Session,
        org_id: str,
        tier: PricingTier,
        customer_email: str,
        quantity: int = 1,
    ) -> str:
        """
        Create a Stripe Checkout session for subscription.
        Returns checkout session URL.
        
        Args:
            db: Database session
            org_id: Organization ID
            tier: Pricing tier (PricingTier enum)
            customer_email: Customer email
            quantity: Number of seats/units (for Teams tier)
        
        Returns:
            Checkout session URL
        """
        if tier not in TIER_CONFIG:
            raise ValueError(f"Invalid tier: {tier}")
        
        config = TIER_CONFIG[tier]
        
        if not config.get("stripe_price_id"):
            raise ValueError(f"Cannot create checkout for {tier} tier (custom pricing)")
        
        # Ensure customer exists
        customer = StripeCustomerService.create_or_get_customer(
            db, org_id, customer_email
        )
        
        try:
            # Build line items
            line_items = [
                {
                    "price": config["stripe_price_id"],
                    "quantity": quantity,
                }
            ]
            
            # Create Checkout session
            session = stripe.checkout.Session.create(
                customer=customer.stripe_customer_id,
                payment_method_types=["card"],
                line_items=line_items,
                mode="subscription",
                success_url=f"{CHECKOUT_SUCCESS_URL}?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=CHECKOUT_CANCEL_URL,
                metadata={
                    "org_id": org_id,
                    "tier": tier.value,
                },
                subscription_data={
                    "metadata": {
                        "org_id": org_id,
                        "tier": tier.value,
                    }
                },
                # Allow trial if configured
                trial_end=None if config.get("trial_days", 0) == 0 
                    else int((datetime.utcnow() + timedelta(days=config["trial_days"])).timestamp()),
            )
            
            logger.info(f"Created checkout session {session.id} for org {org_id}, tier {tier}")
            return session.url
            
        except stripe.error.StripeAPIError as e:
            logger.error(f"Stripe API error creating checkout: {e}")
            raise
    
    
    @staticmethod
    def save_subscription(
        db: Session,
        org_id: str,
        stripe_subscription: Dict[str, Any],
    ) -> StripeSubscription:
        """
        Save or update subscription in database.
        Called after successful checkout or from webhook.
        """
        customer_id = stripe_subscription.get("customer")
        product_id = stripe_subscription.get("items", {}).get("data", [{}])[0].get("plan", {}).get("product")
        price_id = stripe_subscription.get("items", {}).get("data", [{}])[0].get("plan", {}).get("id")
        
        # Get customer from DB
        customer = db.query(StripeCustomer).filter(
            StripeCustomer.stripe_customer_id == customer_id
        ).first()
        
        if not customer:
            raise ValueError(f"Stripe customer {customer_id} not found in DB")
        
        # Determine tier from price ID
        try:
            tier = get_tier_by_price_id(price_id)
        except ValueError:
            tier = PricingTier.FREE
        
        # Check if subscription already exists
        existing = db.query(StripeSubscription).filter(
            StripeSubscription.stripe_subscription_id == stripe_subscription.get("id")
        ).first()
        
        current_period_start = datetime.fromtimestamp(
            stripe_subscription.get("current_period_start", 0)
        )
        current_period_end = datetime.fromtimestamp(
            stripe_subscription.get("current_period_end", 0)
        )
        
        if existing:
            # Update existing
            existing.status = stripe_subscription.get("status", "active")
            existing.current_period_start = current_period_start
            existing.current_period_end = current_period_end
            existing.cancel_at_period_end = stripe_subscription.get("cancel_at_period_end", False)
            existing.canceled_at = (
                datetime.fromtimestamp(stripe_subscription.get("canceled_at"))
                if stripe_subscription.get("canceled_at") else None
            )
            existing.tier = tier
            existing.stripe_metadata = stripe_subscription.get("metadata", {})
            existing.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(existing)
            
            logger.info(f"Updated subscription {existing.id} for org {org_id}")
            return existing
        
        else:
            # Create new
            subscription = StripeSubscription(
                customer_id=customer.id,
                org_id=org_id,
                stripe_subscription_id=stripe_subscription.get("id"),
                stripe_product_id=product_id,
                stripe_price_id=price_id,
                tier=tier,
                status=stripe_subscription.get("status", "active"),
                current_period_start=current_period_start,
                current_period_end=current_period_end,
                cancel_at_period_end=stripe_subscription.get("cancel_at_period_end", False),
                canceled_at=None,
                trial_start=(
                    datetime.fromtimestamp(stripe_subscription.get("trial_start"))
                    if stripe_subscription.get("trial_start") else None
                ),
                trial_end=(
                    datetime.fromtimestamp(stripe_subscription.get("trial_end"))
                    if stripe_subscription.get("trial_end") else None
                ),
                stripe_metadata=stripe_subscription.get("metadata", {}),
            )
            db.add(subscription)
            db.commit()
            db.refresh(subscription)
            
            logger.info(f"Created subscription {subscription.id} for org {org_id}, tier {tier}")
            
            # Initialize usage metrics
            UsageMetricsService.create_usage_metrics(
                db, org_id, current_period_start, current_period_end
            )
            
            return subscription
    
    
    @staticmethod
    def get_active_subscription(db: Session, org_id: str) -> Optional[StripeSubscription]:
        """Get active subscription for organization."""
        return db.query(StripeSubscription).filter(
            StripeSubscription.org_id == org_id,
            StripeSubscription.status.in_(["active", "trialing"])
        ).first()
    
    
    @staticmethod
    def change_plan(
        db: Session,
        org_id: str,
        new_tier: PricingTier,
    ) -> StripeSubscription:
        """
        Upgrade or downgrade subscription to new tier.
        """
        config = TIER_CONFIG.get(new_tier)
        if not config or not config.get("stripe_price_id"):
            raise ValueError(f"Cannot change to {new_tier} tier")
        
        subscription = StripeSubscriptionService.get_active_subscription(db, org_id)
        if not subscription:
            raise ValueError(f"No active subscription for org {org_id}")
        
        try:
            # Update subscription in Stripe
            stripe_subscription = stripe.Subscription.modify(
                subscription.stripe_subscription_id,
                items=[
                    {
                        "id": stripe.Subscription.retrieve(
                            subscription.stripe_subscription_id
                        ).items.data[0].id,
                        "plan": config["stripe_price_id"],
                    }
                ],
                # Immediately apply change (not at end of period)
                proration_behavior="create_prorations",
                metadata={"tier": new_tier.value},
            )
            
            logger.info(f"Changed subscription {subscription.id} to tier {new_tier}")
            
            # Save updated subscription
            return StripeSubscriptionService.save_subscription(db, org_id, stripe_subscription)
            
        except stripe.error.StripeAPIError as e:
            logger.error(f"Stripe API error changing plan: {e}")
            raise
    
    
    @staticmethod
    def cancel_subscription(
        db: Session,
        org_id: str,
        immediate: bool = False,
    ) -> StripeSubscription:
        """
        Cancel subscription for organization.
        
        Args:
            db: Database session
            org_id: Organization ID
            immediate: If True, cancel immediately. If False, cancel at end of period.
        """
        subscription = StripeSubscriptionService.get_active_subscription(db, org_id)
        if not subscription:
            raise ValueError(f"No active subscription for org {org_id}")
        
        try:
            if immediate:
                # Cancel immediately
                stripe_subscription = stripe.Subscription.delete(
                    subscription.stripe_subscription_id
                )
            else:
                # Cancel at end of period
                stripe_subscription = stripe.Subscription.modify(
                    subscription.stripe_subscription_id,
                    cancel_at_period_end=True,
                )
            
            logger.info(f"Cancelled subscription {subscription.id} for org {org_id}")
            
            # Save updated subscription
            return StripeSubscriptionService.save_subscription(db, org_id, stripe_subscription)
            
        except stripe.error.StripeAPIError as e:
            logger.error(f"Stripe API error canceling subscription: {e}")
            raise


# ── Usage Metrics & Limits ────────────────────────────────────────────────────

class UsageMetricsService:
    """Track and enforce usage limits."""
    
    @staticmethod
    def create_usage_metrics(
        db: Session,
        org_id: str,
        period_start: datetime,
        period_end: datetime,
    ) -> UsageMetrics:
        """Initialize usage metrics for new billing period."""
        
        # Check if metrics already exist for this org
        existing = db.query(UsageMetrics).filter(
            UsageMetrics.org_id == org_id
        ).first()
        
        if existing:
            return existing
        
        metrics = UsageMetrics(
            org_id=org_id,
            projects_generated=0,
            documents_created=0,
            api_calls=0,
            billing_period_start=period_start,
            billing_period_end=period_end,
            reset_date=period_end,
        )
        db.add(metrics)
        db.commit()
        db.refresh(metrics)
        
        logger.info(f"Created usage metrics for org {org_id}")
        return metrics
    
    
    @staticmethod
    def get_or_create_metrics(db: Session, org_id: str) -> UsageMetrics:
        """Get usage metrics, creating if necessary."""
        metrics = db.query(UsageMetrics).filter(
            UsageMetrics.org_id == org_id
        ).first()
        
        if metrics:
            # Check if period needs reset
            if datetime.utcnow() >= metrics.reset_date:
                # Reset counters
                metrics.projects_generated = 0
                metrics.documents_created = 0
                metrics.api_calls = 0
                
                # Get current subscription to update period
                subscription = StripeSubscriptionService.get_active_subscription(db, org_id)
                if subscription:
                    metrics.billing_period_start = subscription.current_period_start
                    metrics.billing_period_end = subscription.current_period_end
                    metrics.reset_date = subscription.current_period_end
                
                db.commit()
                db.refresh(metrics)
                logger.info(f"Reset usage metrics for org {org_id}")
            
            return metrics
        
        # Create new metrics
        subscription = StripeSubscriptionService.get_active_subscription(db, org_id)
        if subscription:
            period_start = subscription.current_period_start
            period_end = subscription.current_period_end
        else:
            # No active subscription, use current month
            now = datetime.utcnow()
            period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            period_end = (period_start + timedelta(days=31)).replace(day=1)
        
        return UsageMetricsService.create_usage_metrics(
            db, org_id, period_start, period_end
        )
    
    
    @staticmethod
    def increment_project_count(db: Session, org_id: str, count: int = 1) -> None:
        """Increment projects generated this month."""
        metrics = UsageMetricsService.get_or_create_metrics(db, org_id)
        metrics.projects_generated += count
        db.commit()
        logger.info(f"Incremented projects for org {org_id} to {metrics.projects_generated}")
    
    
    @staticmethod
    def increment_api_calls(db: Session, org_id: str, count: int = 1) -> None:
        """Increment API calls this month."""
        metrics = UsageMetricsService.get_or_create_metrics(db, org_id)
        metrics.api_calls += count
        db.commit()
        logger.info(f"Incremented API calls for org {org_id} to {metrics.api_calls}")
    
    
    @staticmethod
    def check_project_limit(db: Session, org_id: str) -> bool:
        """
        Check if org can generate another project.
        Returns True if under limit, False if at/over limit.
        """
        subscription = StripeSubscriptionService.get_active_subscription(db, org_id)
        if not subscription:
            # No subscription = free tier
            subscription_tier = PricingTier.FREE
        else:
            subscription_tier = subscription.tier
        
        limits = get_tier_limits(subscription_tier)
        metrics = UsageMetricsService.get_or_create_metrics(db, org_id)
        
        return metrics.projects_generated < limits["max_projects_per_month"]
    
    
    @staticmethod
    def get_usage_stats(db: Session, org_id: str) -> Dict[str, Any]:
        """
        Get current usage and limits for organization.
        """
        subscription = StripeSubscriptionService.get_active_subscription(db, org_id)
        tier = subscription.tier if subscription else PricingTier.FREE
        
        limits = get_tier_limits(tier)
        metrics = UsageMetricsService.get_or_create_metrics(db, org_id)
        
        return {
            "tier": tier.value,
            "usage": {
                "projects_generated": metrics.projects_generated,
                "documents_created": metrics.documents_created,
                "api_calls": metrics.api_calls,
            },
            "limits": limits,
            "billing_period": {
                "start": metrics.billing_period_start.isoformat(),
                "end": metrics.billing_period_end.isoformat(),
                "remaining_days": (metrics.reset_date - datetime.utcnow()).days,
            },
        }


# ── Invoice Management ────────────────────────────────────────────────────────

class StripeInvoiceService:
    """Handle invoice tracking and payment notifications."""

    @staticmethod
    def _normalize_line_items(stripe_invoice: Dict[str, Any]) -> List[Dict[str, Any]]:
        items = []
        for item in stripe_invoice.get("lines", {}).get("data", []):
            amount = int(item.get("amount", 0) or 0)
            quantity = int(item.get("quantity", 1) or 1)
            unit_price = int(amount / quantity) if quantity else amount
            tax_rate = 0.0
            tax_amount = 0

            if item.get("tax_rates"):
                rate = item["tax_rates"][0] if isinstance(item["tax_rates"], list) and item["tax_rates"] else {}
                tax_rate = float(rate.get("percentage", 0) or 0)

            if item.get("tax_amounts"):
                amount_data = item["tax_amounts"][0] if isinstance(item["tax_amounts"], list) and item["tax_amounts"] else {}
                tax_amount = int(amount_data.get("amount", 0) or 0)

            items.append(
                {
                    "description": item.get("description", ""),
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "amount": amount,
                    "tax_rate": tax_rate,
                    "tax_amount": tax_amount,
                }
            )

        return items

    @staticmethod
    def _resolve_tax_rate(stripe_invoice: Dict[str, Any]) -> float:
        if stripe_invoice.get("tax_percent") is not None:
            return float(stripe_invoice.get("tax_percent") or 0)

        for rate in stripe_invoice.get("tax_rates", []) or []:
            if isinstance(rate, dict) and rate.get("percentage") is not None:
                return float(rate.get("percentage") or 0)

        for item in stripe_invoice.get("lines", {}).get("data", []) or []:
            for rate in item.get("tax_rates", []) or []:
                if isinstance(rate, dict) and rate.get("percentage") is not None:
                    return float(rate.get("percentage") or 0)

        return 0.0

    @staticmethod
    def _format_currency(amount: int, currency: str) -> str:
        symbol = {
            "usd": "$",
            "eur": "€",
            "gbp": "£",
            "aud": "A$",
            "cad": "C$",
        }.get(currency.lower(), "")
        return f"{symbol}{amount / 100:,.2f}"

    @staticmethod
    def _get_invoice_pdf_path(invoice: Invoice) -> Path:
        invoices_dir = Path(__file__).resolve().parents[2] / "invoice_pdfs"
        path = invoices_dir / invoice.org_id / f"{invoice.id}.pdf"
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def _save_invoice_line_items(db: Session, invoice: Invoice, items: List[Dict[str, Any]]) -> None:
        db.query(InvoiceLineItem).filter(InvoiceLineItem.invoice_id == invoice.id).delete(synchronize_session=False)
        for item in items:
            line = InvoiceLineItem(
                invoice_id=invoice.id,
                description=item.get("description", ""),
                quantity=item.get("quantity", 1),
                unit_price=item.get("unit_price", 0),
                amount=item.get("amount", 0),
                tax_rate=item.get("tax_rate", 0.0),
                tax_amount=item.get("tax_amount", 0),
            )
            db.add(line)
        db.flush()

    @staticmethod
    def _save_invoice_payment(db: Session, invoice: Invoice, stripe_invoice: Dict[str, Any]) -> None:
        payment_intent_id = stripe_invoice.get("payment_intent")
        if not payment_intent_id:
            return

        amount = int(stripe_invoice.get("amount_paid", stripe_invoice.get("total", 0) or 0))
        status_value = "succeeded" if stripe_invoice.get("paid") else stripe_invoice.get("status", "pending")
        paid_at = (
            datetime.fromtimestamp(stripe_invoice.get("paid_at"))
            if stripe_invoice.get("paid_at") else None
        )

        payment = db.query(InvoicePayment).filter(
            InvoicePayment.stripe_payment_intent_id == payment_intent_id
        ).first()

        if payment:
            payment.amount = amount
            payment.currency = stripe_invoice.get("currency", DEFAULT_CURRENCY)
            payment.status = status_value
            payment.paid_at = paid_at
            payment.updated_at = datetime.utcnow()
        else:
            payment = InvoicePayment(
                invoice_id=invoice.id,
                stripe_payment_intent_id=payment_intent_id,
                amount=amount,
                currency=stripe_invoice.get("currency", DEFAULT_CURRENCY),
                status=status_value,
                paid_at=paid_at,
            )
            db.add(payment)

    @staticmethod
    def _serialize_invoice(invoice: Invoice) -> Dict[str, Any]:
        return {
            "id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "stripe_invoice_id": invoice.stripe_invoice_id,
            "org_id": invoice.org_id,
            "customer_id": invoice.customer_id,
            "customer_email": invoice.customer.email if invoice.customer else None,
            "amount": invoice.amount,
            "subtotal": invoice.subtotal,
            "tax_rate": invoice.tax_rate,
            "tax_amount": invoice.tax_amount,
            "total": invoice.total,
            "currency": invoice.currency,
            "status": invoice.status.value if hasattr(invoice.status, "value") else invoice.status,
            "invoice_date": invoice.invoice_date.isoformat() if invoice.invoice_date else None,
            "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
            "paid_at": invoice.paid_at.isoformat() if invoice.paid_at else None,
            "pdf_path": invoice.pdf_path,
            "line_items": invoice.line_items or [],
            "payments": [
                {
                    "stripe_payment_intent_id": payment.stripe_payment_intent_id,
                    "amount": payment.amount,
                    "currency": payment.currency,
                    "status": payment.status,
                    "paid_at": payment.paid_at.isoformat() if payment.paid_at else None,
                }
                for payment in invoice.payments
            ],
            "created_at": invoice.created_at.isoformat() if invoice.created_at else None,
            "updated_at": invoice.updated_at.isoformat() if invoice.updated_at else None,
        }

    @staticmethod
    def _build_invoice_email_body(
        invoice: Invoice,
        organization: Organization,
        branding: Optional[OrgBranding] = None,
    ) -> str:
        brand_name = branding.brand_name if branding and branding.brand_name else organization.name
        primary_color = branding.primary_color if branding and branding.primary_color else "#4F46E5"
        support_email = (
            branding.support_email or organization.meta.get("support_email")
            if organization.meta else None
        ) or "support@example.com"
        due_date = invoice.due_date.isoformat() if invoice.due_date else "N/A"
        paid_text = "Paid" if invoice.status == InvoiceStatus.paid else invoice.status.value if hasattr(invoice.status, "value") else invoice.status

        line_items_html = ""
        for item in invoice.line_items or []:
            line_items_html += (
                f"<tr>"
                f"<td style='padding:8px;border:1px solid #e5e7eb;'>{item.get('description', '')}</td>"
                f"<td style='padding:8px;border:1px solid #e5e7eb;text-align:center;'>{item.get('quantity', 1)}</td>"
                f"<td style='padding:8px;border:1px solid #e5e7eb;text-align:right;'>{StripeInvoiceService._format_currency(item.get('unit_price', 0), invoice.currency)}</td>"
                f"<td style='padding:8px;border:1px solid #e5e7eb;text-align:right;'>{StripeInvoiceService._format_currency(item.get('amount', 0), invoice.currency)}</td>"
                f"</tr>"
            )

        return f"""
            <html>
            <body style='font-family: Arial, sans-serif; color: #111; background: #f9fafb; margin: 0; padding: 0;'>
                <div style='max-width: 680px; margin: 20px auto; padding: 24px; background: #ffffff; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.06);'>
                    <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:24px;'>
                        <div>
                            <h1 style='margin:0; font-size:26px; color:{primary_color};'>{brand_name} Invoice</h1>
                            <p style='margin:8px 0 0 0; color:#6b7280;'>Invoice {invoice.invoice_number or invoice.stripe_invoice_id}</p>
                        </div>
                        <div style='text-align:right;'>
                            <p style='margin:0; color:#374151;'>Due date</p>
                            <p style='margin:4px 0 0 0; font-weight:bold; color:#111;'>{due_date}</p>
                        </div>
                    </div>

                    <p style='color:#374151;'>Hello,</p>
                    <p style='color:#374151;'>Please find your invoice attached. This invoice has been marked as <strong>{paid_text}</strong>.</p>

                    <table style='width:100%; border-collapse:collapse; margin-top:16px;'>
                        <thead>
                            <tr>
                                <th style='padding:12px; border:1px solid #e5e7eb; background:#f3f4f6; text-align:left;'>Description</th>
                                <th style='padding:12px; border:1px solid #e5e7eb; background:#f3f4f6; text-align:center;'>Qty</th>
                                <th style='padding:12px; border:1px solid #e5e7eb; background:#f3f4f6; text-align:right;'>Unit</th>
                                <th style='padding:12px; border:1px solid #e5e7eb; background:#f3f4f6; text-align:right;'>Amount</th>
                            </tr>
                        </thead>
                        <tbody>
                            {line_items_html}
                        </tbody>
                    </table>

                    <div style='margin-top:24px; display:flex; justify-content:flex-end;'>
                        <div style='width:320px;'>
                            <div style='display:flex; justify-content:space-between; padding:10px 0; border-bottom:1px solid #e5e7eb;'>
                                <span>Subtotal</span>
                                <strong>{StripeInvoiceService._format_currency(invoice.subtotal, invoice.currency)}</strong>
                            </div>
                            <div style='display:flex; justify-content:space-between; padding:10px 0; border-bottom:1px solid #e5e7eb;'>
                                <span>Tax ({invoice.tax_rate:.2f}%)</span>
                                <strong>{StripeInvoiceService._format_currency(invoice.tax_amount, invoice.currency)}</strong>
                            </div>
                            <div style='display:flex; justify-content:space-between; padding:10px 0; font-size:18px; font-weight:bold;'>
                                <span>Total</span>
                                <strong>{StripeInvoiceService._format_currency(invoice.total, invoice.currency)}</strong>
                            </div>
                        </div>
                    </div>

                    <p style='margin-top:24px; color:#6b7280;'>If you have questions about this invoice, contact <a href='mailto:{support_email}' style='color:{primary_color}; text-decoration:none;'>{support_email}</a>.</p>
                    <p style='margin-top:8px; color:#9ca3af; font-size:13px;'>Thank you for your business.</p>
                </div>
            </body>
            </html>
        """

    @staticmethod
    def generate_invoice_pdf(
        invoice: Invoice,
        organization: Organization,
        branding: Optional[OrgBranding] = None,
    ) -> bytes:
        pdf_path = StripeInvoiceService._get_invoice_pdf_path(invoice)
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        header_color = branding.primary_color if branding and branding.primary_color else "#0f172a"
        title = branding.brand_name if branding and branding.brand_name else organization.name
        invoice_number = invoice.invoice_number or invoice.stripe_invoice_id
        invoice_date = invoice.invoice_date.strftime("%Y-%m-%d") if invoice.invoice_date else "N/A"
        due_date = invoice.due_date.strftime("%Y-%m-%d") if invoice.due_date else "N/A"
        currency = invoice.currency

        pdf.setFont("Helvetica-Bold", 18)
        pdf.setFillColorRGB(0.07, 0.11, 0.17)
        pdf.drawString(50, height - 80, f"{title} Invoice")
        pdf.setFont("Helvetica", 10)
        pdf.setFillColorRGB(0.36, 0.39, 0.49)
        pdf.drawString(50, height - 100, f"Invoice #: {invoice_number}")
        pdf.drawString(50, height - 115, f"Issue date: {invoice_date}")
        pdf.drawString(50, height - 130, f"Due date: {due_date}")

        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(50, height - 170, "Bill To:")
        bill_to = invoice.customer.email if invoice.customer else organization.meta.get("admin_email") if organization.meta else ""
        pdf.setFont("Helvetica", 10)
        pdf.drawString(50, height - 190, bill_to)

        table_top = height - 240
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(50, table_top, "Description")
        pdf.drawRightString(width - 50, table_top, "Amount")

        y = table_top - 24
        pdf.setFont("Helvetica", 10)
        for item in invoice.line_items or []:
            pdf.drawString(50, y, item.get("description", ""))
            pdf.drawRightString(width - 50, y, StripeInvoiceService._format_currency(item.get("amount", 0), currency))
            y -= 18
            if y < 100:
                pdf.showPage()
                y = height - 80

        y -= 10
        pdf.line(50, y, width - 50, y)
        y -= 24
        pdf.drawRightString(width - 50, y, f"Subtotal: {StripeInvoiceService._format_currency(invoice.subtotal, currency)}")
        y -= 18
        pdf.drawRightString(width - 50, y, f"Tax ({invoice.tax_rate:.2f}%): {StripeInvoiceService._format_currency(invoice.tax_amount, currency)}")
        y -= 18
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawRightString(width - 50, y, f"Total: {StripeInvoiceService._format_currency(invoice.total, currency)}")

        pdf.setFont("Helvetica", 10)
        pdf.setFillColorRGB(0.35, 0.39, 0.48)
        pdf.drawString(50, 50, f"If you have questions, contact {branding.support_email if branding and branding.support_email else organization.meta.get('support_email', 'support@example.com') if organization.meta else 'support@example.com'}")
        pdf.showPage()
        pdf.save()

        pdf_bytes = buffer.getvalue()
        pdf_path.write_bytes(pdf_bytes)

        return pdf_bytes

    @staticmethod
    def get_invoice_pdf_bytes(db: Session, invoice: Invoice) -> bytes:
        if invoice.pdf_path:
            pdf_file = Path(invoice.pdf_path)
            if pdf_file.exists():
                return pdf_file.read_bytes()

        org = db.query(Organization).filter(Organization.id == invoice.org_id).first()
        branding = db.query(OrgBranding).filter(OrgBranding.org_id == invoice.org_id).first()
        pdf_bytes = StripeInvoiceService.generate_invoice_pdf(invoice, org, branding)

        if invoice.pdf_path != str(StripeInvoiceService._get_invoice_pdf_path(invoice)):
            invoice.pdf_path = str(StripeInvoiceService._get_invoice_pdf_path(invoice))
            db.commit()

        return pdf_bytes

    @staticmethod
    def send_invoice_email(
        db: Session,
        invoice: Invoice,
        recipient_email: str,
    ) -> bool:
        org = db.query(Organization).filter(Organization.id == invoice.org_id).first()
        branding = db.query(OrgBranding).filter(OrgBranding.org_id == invoice.org_id).first()

        if not org:
            logger.error(f"Organization {invoice.org_id} not found for invoice email")
            return False

        body = StripeInvoiceService._build_invoice_email_body(invoice, org, branding)
        pdf_bytes = StripeInvoiceService.get_invoice_pdf_bytes(db, invoice)

        brand_name = branding.brand_name if branding and branding.brand_name else org.name
        message = MIMEMultipart()
        message["From"] = f"{brand_name} <{mailer.email_user}>"
        message["To"] = recipient_email
        message["Subject"] = f"Invoice {invoice.invoice_number or invoice.stripe_invoice_id} from {brand_name}"
        message.attach(MIMEText(body, "html"))

        attachment = MIMEApplication(pdf_bytes, _subtype="pdf")
        attachment.add_header("Content-Disposition", "attachment", filename=f"invoice_{invoice.stripe_invoice_id}.pdf")
        message.attach(attachment)

        is_placeholder = not mailer.email_user or not mailer.email_pass or "your-email" in mailer.email_user or "your-app-password" in mailer.email_pass
        if is_placeholder:
            if mailer.is_dev:
                logger.info(f"Placeholder SMTP credentials detected. Logging invoice email for {recipient_email}.")
                logger.info(body)
                return True
            logger.error("SMTP credentials missing in production. Cannot send invoice email.")
            return False

        try:
            with smtplib.SMTP(mailer.smtp_server, mailer.smtp_port) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(mailer.email_user, mailer.email_pass)
                server.send_message(message)

            logger.info(f"Sent invoice email to {recipient_email} for invoice {invoice.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to send invoice email to {recipient_email}: {e}")
            if mailer.is_dev:
                logger.info("Falling back to console logging for dev mode.")
                logger.info(body)
                return True
            return False

    @staticmethod
    def get_financial_report(db: Session, org_id: str, start: datetime, end: datetime) -> Dict[str, Any]:
        invoices = db.query(Invoice).filter(
            Invoice.org_id == org_id,
            Invoice.invoice_date >= start,
            Invoice.invoice_date < end,
        ).all()

        status_totals = {
            "paid": 0,
            "open": 0,
            "void": 0,
            "uncollectible": 0,
            "other": 0,
        }
        monthly_summary = {}

        for inv in invoices:
            amount = inv.total or inv.amount
            status_key = inv.status.value if hasattr(inv.status, "value") else str(inv.status)
            status_key = status_key if status_key in status_totals else "other"
            status_totals[status_key] += amount

            month_key = inv.invoice_date.strftime("%Y-%m") if inv.invoice_date else "unknown"
            monthly = monthly_summary.setdefault(month_key, {
                "month": month_key,
                "invoice_count": 0,
                "revenue": 0,
                "tax": 0,
                "paid": 0,
                "open": 0,
            })
            monthly["invoice_count"] += 1
            monthly["revenue"] += amount
            monthly["tax"] += inv.tax_amount or 0
            if status_key == "paid":
                monthly["paid"] += amount
            elif status_key == "open":
                monthly["open"] += amount

        report = {
            "invoice_count": len(invoices),
            "total_revenue": sum((inv.total or inv.amount) for inv in invoices),
            "total_tax": sum(inv.tax_amount or 0 for inv in invoices),
            "paid_total": status_totals.get("paid", 0),
            "open_total": status_totals.get("open", 0),
            "past_due_total": status_totals.get("void", 0) + status_totals.get("uncollectible", 0),
            "status_breakdown": status_totals,
            "monthly_summary": sorted(monthly_summary.values(), key=lambda item: item["month"]),
        }

        return report

    @staticmethod
    def save_invoice(
        db: Session,
        stripe_invoice: Dict[str, Any],
    ) -> Optional[Invoice]:
        """
        Save invoice from Stripe webhook.
        """
        try:
            customer_id = stripe_invoice.get("customer")
            stripe_invoice_id = stripe_invoice.get("id")
            
            # Find customer in DB
            customer = db.query(StripeCustomer).filter(
                StripeCustomer.stripe_customer_id == customer_id
            ).first()
            
            if not customer:
                logger.warning(f"Customer {customer_id} not found for invoice {stripe_invoice_id}")
                return None
            
            # Normalize line items and tax calculations
            line_items = StripeInvoiceService._normalize_line_items(stripe_invoice)
            subtotal = int(stripe_invoice.get("subtotal") or sum(item["amount"] for item in line_items))
            tax_rate = StripeInvoiceService._resolve_tax_rate(stripe_invoice)
            tax_amount = int(stripe_invoice.get("tax") or round(subtotal * tax_rate / 100))
            total = int(stripe_invoice.get("total") or subtotal + tax_amount)
            amount_paid = int(stripe_invoice.get("amount_paid", total))
            invoice_date = datetime.fromtimestamp(stripe_invoice.get("created", 0))
            due_date = (
                datetime.fromtimestamp(stripe_invoice.get("due_date"))
                if stripe_invoice.get("due_date") else None
            )
            invoice_number = stripe_invoice.get("number") or f"INV-{stripe_invoice_id[-8:]}"
            
            # Check if invoice already exists
            existing = db.query(Invoice).filter(
                Invoice.stripe_invoice_id == stripe_invoice_id
            ).first()
            
            if existing:
                existing.status = stripe_invoice.get("status", "open")
                existing.paid_at = (
                    datetime.fromtimestamp(stripe_invoice.get("paid_at"))
                    if stripe_invoice.get("paid_at") else None
                )
                existing.updated_at = datetime.utcnow()
                existing.amount = amount_paid
                existing.subtotal = subtotal
                existing.tax_rate = tax_rate
                existing.tax_amount = tax_amount
                existing.total = total
                existing.invoice_date = invoice_date
                existing.due_date = due_date
                existing.payment_intent_id = stripe_invoice.get("payment_intent")
                existing.line_items = line_items
                existing.invoice_number = invoice_number
                StripeInvoiceService._save_invoice_line_items(db, existing, line_items)
                StripeInvoiceService._save_invoice_payment(db, existing, stripe_invoice)
                db.commit()
                db.refresh(existing)
                return existing
            
            # Create new invoice
            invoice = Invoice(
                customer_id=customer.id,
                org_id=customer.org_id,
                stripe_invoice_id=stripe_invoice_id,
                amount=amount_paid,
                subtotal=subtotal,
                tax_rate=tax_rate,
                tax_amount=tax_amount,
                total=total,
                currency=stripe_invoice.get("currency", DEFAULT_CURRENCY),
                status=stripe_invoice.get("status", "open"),
                paid_at=(
                    datetime.fromtimestamp(stripe_invoice.get("paid_at"))
                    if stripe_invoice.get("paid_at") else None
                ),
                payment_intent_id=stripe_invoice.get("payment_intent"),
                invoice_date=invoice_date,
                due_date=due_date,
                line_items=line_items,
                invoice_number=invoice_number,
            )
            
            db.add(invoice)
            db.commit()
            db.refresh(invoice)
            StripeInvoiceService._save_invoice_line_items(db, invoice, line_items)
            StripeInvoiceService._save_invoice_payment(db, invoice, stripe_invoice)
            db.commit()
            
            logger.info(f"Saved invoice {invoice.id} for org {customer.org_id}")
            return invoice
            
        except Exception as e:
            logger.error(f"Error saving invoice: {e}")
            return None
