"""
Stripe Service: High-level Stripe API interactions and business logic.
Handles customer creation, subscriptions, webhooks, etc.
"""
import stripe
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import logging

from app.core.stripe_config import (
    STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY, PricingTier, TIER_CONFIG,
    get_tier_by_price_id, get_tier_limits, DEFAULT_CURRENCY,
    CHECKOUT_SUCCESS_URL, CHECKOUT_CANCEL_URL, StripeErrorCode,
)
from app.models.stripe_billing import (
    StripeCustomer, StripeSubscription, UsageMetrics, Invoice, PaymentIntent
)
from app.models.organization import Organization

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
            
            # Check if invoice already exists
            existing = db.query(Invoice).filter(
                Invoice.stripe_invoice_id == stripe_invoice_id
            ).first()
            
            if existing:
                # Update status
                existing.status = stripe_invoice.get("status", "open")
                existing.paid_at = (
                    datetime.fromtimestamp(stripe_invoice.get("paid_at"))
                    if stripe_invoice.get("paid_at") else None
                )
                existing.updated_at = datetime.utcnow()
                db.commit()
                db.refresh(existing)
                return existing
            
            # Create new invoice
            invoice = Invoice(
                customer_id=customer.id,
                org_id=customer.org_id,
                stripe_invoice_id=stripe_invoice_id,
                amount=stripe_invoice.get("amount_paid", stripe_invoice.get("total", 0)),
                currency=stripe_invoice.get("currency", DEFAULT_CURRENCY),
                status=stripe_invoice.get("status", "open"),
                paid_at=(
                    datetime.fromtimestamp(stripe_invoice.get("paid_at"))
                    if stripe_invoice.get("paid_at") else None
                ),
                payment_intent_id=stripe_invoice.get("payment_intent"),
                invoice_date=datetime.fromtimestamp(stripe_invoice.get("created", 0)),
                due_date=(
                    datetime.fromtimestamp(stripe_invoice.get("due_date"))
                    if stripe_invoice.get("due_date") else None
                ),
                line_items=[
                    {
                        "description": item.get("description", ""),
                        "amount": item.get("amount", 0),
                        "quantity": item.get("quantity", 1),
                    }
                    for item in stripe_invoice.get("lines", {}).get("data", [])
                ],
            )
            
            db.add(invoice)
            db.commit()
            db.refresh(invoice)
            
            logger.info(f"Saved invoice {invoice.id} for org {customer.org_id}")
            return invoice
            
        except Exception as e:
            logger.error(f"Error saving invoice: {e}")
            return None
