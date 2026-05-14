"""
Stripe Billing Models for SaaS subscription management.
Handles StripeCustomer, StripeSubscription, UsageMetrics, and Invoice records.
"""
import uuid
from sqlalchemy import (
    Column, String, Integer, DateTime, ForeignKey,
    JSON, Boolean, Float, UniqueConstraint, Enum as SAEnum, Text
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base


# ── Enums ─────────────────────────────────────────────────────────────────────

class StripeCustomerStatus(str, enum.Enum):
    active   = "active"
    inactive = "inactive"
    deleted  = "deleted"


class StripeSubscriptionStatus(str, enum.Enum):
    trialing         = "trialing"
    active           = "active"
    incomplete       = "incomplete"
    incomplete_expired = "incomplete_expired"
    past_due         = "past_due"
    canceled         = "canceled"
    unpaid           = "unpaid"


class StripePriceTier(str, enum.Enum):
    """Pricing tiers — maps to Stripe products"""
    free       = "free"
    starter    = "starter"
    pro        = "pro"
    teams      = "teams"
    enterprise = "enterprise"


class InvoiceStatus(str, enum.Enum):
    draft      = "draft"
    open       = "open"
    paid       = "paid"
    void       = "void"
    uncollectible = "uncollectible"


# ── Helper: UUID primary key ──────────────────────────────────────────────────

def _uuid_pk():
    """Returns a String(36) column that works for SQLite (dev) and PostgreSQL (prod)."""
    return Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )


# ── StripeCustomer ────────────────────────────────────────────────────────────

class StripeCustomer(Base):
    """
    Maps organization to Stripe customer.
    One-to-one relationship with Organization.
    """
    __tablename__ = "stripe_customers"

    id                   = _uuid_pk()
    org_id               = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"),
                                  nullable=False, unique=True, index=True)
    stripe_customer_id   = Column(String(255), nullable=False, unique=True, index=True)
    email                = Column(String(255), nullable=False)
    status               = Column(
        SAEnum(StripeCustomerStatus, name="stripe_customer_status", create_constraint=True),
        default=StripeCustomerStatus.active,
        nullable=False,
    )
    created_at           = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at           = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Metadata from Stripe (subscription counts, etc.)
    stripe_metadata      = Column(JSON, nullable=True, default=dict)

    # ── Relationships ─────────────────────────────────────────────────────────
    organization         = relationship("Organization", foreign_keys=[org_id])
    subscriptions        = relationship("StripeSubscription", back_populates="customer",
                                       cascade="all, delete-orphan")
    invoices             = relationship("Invoice", back_populates="customer",
                                       cascade="all, delete-orphan")

    __table_args__       = (
        UniqueConstraint("org_id", name="uq_stripe_customer_org"),
    )


# ── StripeSubscription ────────────────────────────────────────────────────────

class StripeSubscription(Base):
    """
    Stripe subscription record for an organization.
    Tracks active subscription, billing cycle, and status.
    """
    __tablename__ = "stripe_subscriptions"

    id                      = _uuid_pk()
    customer_id             = Column(String(36), ForeignKey("stripe_customers.id", ondelete="CASCADE"),
                                     nullable=False, index=True)
    org_id                  = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"),
                                     nullable=False, index=True)
    stripe_subscription_id  = Column(String(255), nullable=False, unique=True, index=True)
    stripe_product_id       = Column(String(255), nullable=False)
    stripe_price_id         = Column(String(255), nullable=False)
    
    # Pricing tier (for quick reference)
    tier                    = Column(
        SAEnum(StripePriceTier, name="stripe_tier", create_constraint=True),
        default=StripePriceTier.free,
        nullable=False,
        index=True,
    )
    
    status                  = Column(
        SAEnum(StripeSubscriptionStatus, name="stripe_sub_status", create_constraint=True),
        default=StripeSubscriptionStatus.active,
        nullable=False,
    )

    # Billing cycle dates
    current_period_start    = Column(DateTime, nullable=False)
    current_period_end      = Column(DateTime, nullable=False)
    cancel_at_period_end    = Column(Boolean, default=False)
    canceled_at             = Column(DateTime, nullable=True)
    
    # Trial tracking
    trial_start             = Column(DateTime, nullable=True)
    trial_end               = Column(DateTime, nullable=True)
    
    created_at              = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at              = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Metadata from Stripe
    stripe_metadata         = Column(JSON, nullable=True, default=dict)

    # ── Relationships ─────────────────────────────────────────────────────────
    customer                = relationship("StripeCustomer", back_populates="subscriptions")
    organization            = relationship("Organization", foreign_keys=[org_id])

    __table_args__          = (
        UniqueConstraint("customer_id", "stripe_subscription_id", name="uq_stripe_sub"),
    )


# ── UsageMetrics ──────────────────────────────────────────────────────────────

class UsageMetrics(Base):
    """
    Track org usage for the current billing period.
    Resets on billing_cycle_anchor date.
    """
    __tablename__ = "usage_metrics"

    id                   = _uuid_pk()
    org_id               = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"),
                                  nullable=False, unique=True, index=True)
    
    # Monthly usage counters
    projects_generated   = Column(Integer, default=0, nullable=False)
    documents_created    = Column(Integer, default=0, nullable=False)
    api_calls            = Column(Integer, default=0, nullable=False)
    
    # Billing period tracking
    billing_period_start = Column(DateTime, nullable=False)
    billing_period_end   = Column(DateTime, nullable=False)
    
    # Reset date (typically aligned with subscription anchor)
    reset_date           = Column(DateTime, nullable=False)
    
    created_at           = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at           = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ── Relationships ─────────────────────────────────────────────────────────
    organization         = relationship("Organization", foreign_keys=[org_id])


# ── Invoice ───────────────────────────────────────────────────────────────────

class Invoice(Base):
    """
    Stripe invoice record for audit trail and accounting.
    """
    __tablename__ = "stripe_invoices"

    id                   = _uuid_pk()
    customer_id          = Column(String(36), ForeignKey("stripe_customers.id", ondelete="SET NULL"),
                                  nullable=True, index=True)
    org_id               = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"),
                                  nullable=False, index=True)
    stripe_invoice_id    = Column(String(255), nullable=False, unique=True, index=True)
    
    # Amount in cents
    amount               = Column(Integer, nullable=False)
    currency             = Column(String(3), default="usd", nullable=False)
    
    status               = Column(
        SAEnum(InvoiceStatus, name="invoice_status", create_constraint=True),
        default=InvoiceStatus.open,
        nullable=False,
    )
    
    # Payment tracking
    paid_at              = Column(DateTime, nullable=True)
    payment_intent_id    = Column(String(255), nullable=True)
    
    # Invoice dates
    invoice_date         = Column(DateTime, nullable=False)
    due_date             = Column(DateTime, nullable=True)
    
    # Line items (JSON for flexibility)
    line_items           = Column(JSON, nullable=True, default=list)
    
    created_at           = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at           = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ── Relationships ─────────────────────────────────────────────────────────
    customer             = relationship("StripeCustomer", back_populates="invoices")
    organization         = relationship("Organization", foreign_keys=[org_id])

    __table_args__       = (
        UniqueConstraint("org_id", "stripe_invoice_id", name="uq_invoice_org_stripe_id"),
    )


# ── PaymentIntent ─────────────────────────────────────────────────────────────

class PaymentIntent(Base):
    """
    Track Stripe payment intents for checkout sessions.
    Useful for debugging failed payments and retries.
    """
    __tablename__ = "payment_intents"

    id                   = _uuid_pk()
    org_id               = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"),
                                  nullable=False, index=True)
    stripe_payment_intent_id = Column(String(255), nullable=False, unique=True, index=True)
    
    amount               = Column(Integer, nullable=False)
    currency             = Column(String(3), default="usd", nullable=False)
    status               = Column(String(50), nullable=False)  # succeeded, processing, requires_action, canceled, etc.
    
    # Reference to what triggered this payment (e.g., subscription upgrade)
    reason               = Column(String(100), nullable=True)  # "checkout", "upgrade", "retry"
    
    created_at           = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at           = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ── Relationships ─────────────────────────────────────────────────────────
    organization         = relationship("Organization", foreign_keys=[org_id])
