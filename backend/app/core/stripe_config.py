"""
Stripe Configuration and Product/Price Mappings.
Define all Stripe product IDs, price IDs, and tier limits here.
"""
import os
from enum import Enum
from typing import Dict, Any
from datetime import datetime


# ── Stripe API Keys ───────────────────────────────────────────────────────────

STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "").strip()
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY", "").strip()
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "").strip()

if not STRIPE_SECRET_KEY or not STRIPE_SECRET_KEY.startswith("sk_"):
    raise ValueError("STRIPE_SECRET_KEY not set or invalid (must start with 'sk_')")
if not STRIPE_PUBLISHABLE_KEY or not STRIPE_PUBLISHABLE_KEY.startswith("pk_"):
    raise ValueError("STRIPE_PUBLISHABLE_KEY not set or invalid (must start with 'pk_')")
if not STRIPE_WEBHOOK_SECRET or not STRIPE_WEBHOOK_SECRET.startswith("whsec_"):
    raise ValueError("STRIPE_WEBHOOK_SECRET not set or invalid (must start with 'whsec_')")


# ── Environment ───────────────────────────────────────────────────────────────

STRIPE_ENV = os.environ.get("STRIPE_ENV", "test")  # "test" or "live"
IS_STRIPE_LIVE = STRIPE_ENV == "live"


# ── Pricing Tiers & Limits ────────────────────────────────────────────────────

class PricingTier(str, Enum):
    FREE       = "free"
    STARTER    = "starter"
    PRO        = "pro"
    TEAMS      = "teams"
    ENTERPRISE = "enterprise"


# Tier configuration: limits, pricing, features
TIER_CONFIG: Dict[PricingTier, Dict[str, Any]] = {
    PricingTier.FREE: {
        "name": "Free",
        "stripe_product_id": os.environ.get("STRIPE_PRODUCT_FREE", "prod_free_placeholder"),
        "stripe_price_id": os.environ.get("STRIPE_PRICE_FREE", "price_free_placeholder"),
        "price_monthly": 0,
        "price_annually": 0,
        "billing_interval": "month",
        "trial_days": 0,
        
        # Limits per month
        "max_projects_per_month": 3,
        "max_documents": 5,
        "max_api_calls": 1000,
        "max_team_seats": 1,
        "features": [
            "3 projects/month",
            "Basic documentation",
            "Email support",
            "Community access",
        ],
    },
    
    PricingTier.STARTER: {
        "name": "Starter",
        "stripe_product_id": os.environ.get("STRIPE_PRODUCT_STARTER", "prod_starter_placeholder"),
        "stripe_price_id": os.environ.get("STRIPE_PRICE_STARTER", "price_starter_placeholder"),
        "price_monthly": 2900,  # $29 in cents
        "price_annually": 29000,  # $290 (roughly 10 months for annual)
        "billing_interval": "month",
        "trial_days": 14,
        
        # Limits per month
        "max_projects_per_month": 30,
        "max_documents": 50,
        "max_api_calls": 10000,
        "max_team_seats": 1,
        "features": [
            "30 projects/month",
            "Advanced documentation",
            "Email & chat support",
            "Prioritized generation",
            "Export to PDF/Word",
        ],
    },
    
    PricingTier.PRO: {
        "name": "Pro",
        "stripe_product_id": os.environ.get("STRIPE_PRODUCT_PRO", "prod_pro_placeholder"),
        "stripe_price_id": os.environ.get("STRIPE_PRICE_PRO", "price_pro_placeholder"),
        "price_monthly": 9900,  # $99 in cents
        "price_annually": 99000,  # $990
        "billing_interval": "month",
        "trial_days": 14,
        
        # Limits per month
        "max_projects_per_month": 999999,  # Unlimited
        "max_documents": 999999,
        "max_api_calls": 100000,
        "max_team_seats": 3,
        "features": [
            "Unlimited projects",
            "Advanced analytics",
            "Priority support (24/7)",
            "API access",
            "Custom branding",
            "Team collaboration (3 seats)",
        ],
    },
    
    PricingTier.TEAMS: {
        "name": "Teams",
        "stripe_product_id": os.environ.get("STRIPE_PRODUCT_TEAMS", "prod_teams_placeholder"),
        "stripe_price_id": os.environ.get("STRIPE_PRICE_TEAMS", "price_teams_placeholder"),
        "price_monthly": 29900,  # $299 in cents
        "price_annually": 299000,  # $2990
        "billing_interval": "month",
        "trial_days": 14,
        
        # Limits per month
        "max_projects_per_month": 999999,  # Unlimited
        "max_documents": 999999,
        "max_api_calls": 999999,
        "max_team_seats": 999999,  # Unlimited seats
        "features": [
            "Unlimited everything",
            "Unlimited team seats",
            "Advanced team management",
            "SSO/SAML integration",
            "Audit logs",
            "Dedicated account manager",
            "Priority support (24/7)",
        ],
    },
    
    PricingTier.ENTERPRISE: {
        "name": "Enterprise",
        "stripe_product_id": None,  # Custom pricing, no fixed Stripe product
        "stripe_price_id": None,
        "price_monthly": None,  # Contact sales
        "price_annually": None,
        "billing_interval": None,
        "trial_days": 30,
        
        # Limits per month (customizable)
        "max_projects_per_month": 999999,
        "max_documents": 999999,
        "max_api_calls": 999999,
        "max_team_seats": 999999,
        "features": [
            "Unlimited everything",
            "Custom SLA",
            "Custom integrations",
            "Dedicated infrastructure",
            "Dedicated support team",
            "24/7 phone support",
            "On-premise deployment available",
        ],
    },
}


# ── Stripe Product Mapping ────────────────────────────────────────────────────

def get_tier_by_price_id(stripe_price_id: str) -> PricingTier:
    """
    Look up pricing tier by Stripe price ID.
    Useful for webhook handling.
    """
    for tier, config in TIER_CONFIG.items():
        if config.get("stripe_price_id") == stripe_price_id:
            return tier
    raise ValueError(f"Unknown Stripe price ID: {stripe_price_id}")


def get_tier_by_product_id(stripe_product_id: str) -> PricingTier:
    """
    Look up pricing tier by Stripe product ID.
    """
    for tier, config in TIER_CONFIG.items():
        if config.get("stripe_product_id") == stripe_product_id:
            return tier
    raise ValueError(f"Unknown Stripe product ID: {stripe_product_id}")


# ── Tier Feature Limits ───────────────────────────────────────────────────────

def get_tier_limits(tier: PricingTier) -> Dict[str, int]:
    """
    Get usage limits for a tier.
    Returns dict with max_projects_per_month, max_api_calls, etc.
    """
    config = TIER_CONFIG.get(tier)
    if not config:
        raise ValueError(f"Unknown tier: {tier}")
    
    return {
        "max_projects_per_month": config.get("max_projects_per_month", 0),
        "max_documents": config.get("max_documents", 0),
        "max_api_calls": config.get("max_api_calls", 0),
        "max_team_seats": config.get("max_team_seats", 0),
    }


# ── Webhook Event Types ───────────────────────────────────────────────────────

class WebhookEventType(str, Enum):
    CUSTOMER_CREATED = "customer.created"
    CUSTOMER_UPDATED = "customer.updated"
    CUSTOMER_DELETED = "customer.deleted"
    
    SUBSCRIPTION_CREATED = "customer.subscription.created"
    SUBSCRIPTION_UPDATED = "customer.subscription.updated"
    SUBSCRIPTION_DELETED = "customer.subscription.deleted"
    
    INVOICE_CREATED = "invoice.created"
    INVOICE_PAYMENT_SUCCEEDED = "invoice.payment_succeeded"
    INVOICE_PAYMENT_FAILED = "invoice.payment_failed"
    INVOICE_PAID = "invoice.paid"
    
    PAYMENT_INTENT_SUCCEEDED = "payment_intent.succeeded"
    PAYMENT_INTENT_PAYMENT_FAILED = "payment_intent.payment_failed"


# ── Error Codes ───────────────────────────────────────────────────────────────

class StripeErrorCode(str, Enum):
    USAGE_LIMIT_EXCEEDED = "usage_limit_exceeded"
    SUBSCRIPTION_REQUIRED = "subscription_required"
    PAYMENT_REQUIRED = "payment_required"
    INVALID_TIER = "invalid_tier"
    NO_ACTIVE_SUBSCRIPTION = "no_active_subscription"
    STRIPE_API_ERROR = "stripe_api_error"


# ── Currency ──────────────────────────────────────────────────────────────────

DEFAULT_CURRENCY = "usd"
SUPPORTED_CURRENCIES = ["usd", "eur", "gbp", "aud", "cad"]


# ── Checkout Configuration ────────────────────────────────────────────────────

# Success/cancel redirect URLs (set in environment)
CHECKOUT_SUCCESS_URL = os.environ.get("CHECKOUT_SUCCESS_URL", "")
CHECKOUT_CANCEL_URL = os.environ.get("CHECKOUT_CANCEL_URL", "")

if not CHECKOUT_SUCCESS_URL or not CHECKOUT_CANCEL_URL:
    raise ValueError(
        "CHECKOUT_SUCCESS_URL and CHECKOUT_CANCEL_URL must be set in environment"
    )


# ── Idempotency & Retry ───────────────────────────────────────────────────────

MAX_RETRIES_WEBHOOK = 3
WEBHOOK_TIMEOUT_SECONDS = 30
