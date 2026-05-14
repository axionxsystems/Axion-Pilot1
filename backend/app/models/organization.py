import uuid
from sqlalchemy import (
    Column, String, Integer, DateTime, ForeignKey,
    JSON, UniqueConstraint, Enum as SAEnum
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base


# ── Enums ─────────────────────────────────────────────────────────────────────

class OrgTier(str, enum.Enum):
    free       = "free"
    starter    = "starter"
    pro        = "pro"
    enterprise = "enterprise"


class OrgMemberRole(str, enum.Enum):
    admin  = "admin"
    member = "member"
    viewer = "viewer"


class SubscriptionStatus(str, enum.Enum):
    active            = "active"
    trialing          = "trialing"
    past_due          = "past_due"
    canceled          = "canceled"
    incomplete        = "incomplete"
    incomplete_expired = "incomplete_expired"


# ── Helper: cross-DB UUID primary key ─────────────────────────────────────────

def _uuid_pk():
    """
    Returns a String(36) column that stores UUIDs as text — works for both
    SQLite (dev) and PostgreSQL (prod).  For pure Postgres you can swap this
    for PG_UUID(as_uuid=True).
    """
    return Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )


# ── Organization ──────────────────────────────────────────────────────────────

class Organization(Base):
    """
    Top-level tenant.  Every user, project, and subscription belongs to one org.
    """
    __tablename__ = "organizations"

    id         = _uuid_pk()
    name       = Column(String(120), nullable=False)
    slug       = Column(String(80), unique=True, nullable=False, index=True)

    # Billing tier — mirrors Subscription.tier but cached here for quick quota checks
    tier       = Column(
        SAEnum(OrgTier, name="org_tier", create_constraint=True),
        default=OrgTier.free,
        nullable=False,
    )

    # Monthly API call allowance per tier (default overridable per org)
    api_quota  = Column(Integer, default=100, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Flexible metadata (custom domain, branding, feature flags …)
    meta       = Column("metadata", JSON, nullable=True, default=dict)

    # ── Relationships ─────────────────────────────────────────────────────────
    members       = relationship("User",         back_populates="organization",
                                 foreign_keys="User.org_id")
    projects      = relationship("Project",      back_populates="organization",
                                 foreign_keys="Project.org_id")
    subscriptions = relationship("Subscription", back_populates="organization",
                                 cascade="all, delete-orphan")
    audit_logs    = relationship("AuditLog",     back_populates="organization",
                                 cascade="all, delete-orphan")
    api_keys      = relationship("APIKey",       back_populates="organization",
                                 cascade="all, delete-orphan", foreign_keys="APIKey.org_id")


# ── Subscription ──────────────────────────────────────────────────────────────

class Subscription(Base):
    """
    Stripe subscription record for an organisation.
    """
    __tablename__ = "subscriptions"

    id                     = _uuid_pk()
    org_id                 = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"),
                                    nullable=False, index=True)
    stripe_subscription_id = Column(String(255), nullable=True, unique=True)

    tier    = Column(
        SAEnum(OrgTier, name="sub_tier", create_constraint=True),
        default=OrgTier.free,
        nullable=False,
    )
    status  = Column(
        SAEnum(SubscriptionStatus, name="sub_status", create_constraint=True),
        default=SubscriptionStatus.active,
        nullable=False,
    )

    next_billing_date = Column(DateTime, nullable=True)
    # Tracks current-period usage: {"api_calls": 42, "projects": 3, …}
    usage_json        = Column(JSON, nullable=True, default=dict)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ── Relationships ─────────────────────────────────────────────────────────
    organization = relationship("Organization", back_populates="subscriptions")


# ── AuditLog ──────────────────────────────────────────────────────────────────

class AuditLog(Base):
    """
    Immutable audit trail — one row per change event inside an org.
    """
    __tablename__ = "audit_logs"

    id            = _uuid_pk()
    org_id        = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"),
                           nullable=False, index=True)
    actor_id      = Column(Integer,    ForeignKey("users.id", ondelete="SET NULL"),
                           nullable=True, index=True)

    action        = Column(String(80),  nullable=False)          # e.g. "project.create"
    resource_type = Column(String(80),  nullable=True)           # e.g. "project"
    resource_id   = Column(String(120), nullable=True)           # str / int / uuid
    changes       = Column(JSON,        nullable=True)           # before/after diff
    timestamp     = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # ── Relationships ─────────────────────────────────────────────────────────
    organization = relationship("Organization", back_populates="audit_logs")
    actor        = relationship("User", foreign_keys=[actor_id])
