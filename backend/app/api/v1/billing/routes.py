"""
Billing API Routes - Stripe integration endpoints.
Handles subscriptions, checkouts, usage tracking, and plan changes.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.database import get_db
from app.core.stripe_config import PricingTier, StripeErrorCode
from app.services.stripe_service import (
    StripeCustomerService, StripeSubscriptionService, UsageMetricsService,
    StripeInvoiceService,
)
from app.middleware.tenant import get_current_org_id
from app.models.organization import Organization
from pydantic import BaseModel, EmailStr

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/billing", tags=["Billing"])


# ── Pydantic Schemas ──────────────────────────────────────────────────────────

class CheckoutRequest(BaseModel):
    tier: str  # "free", "starter", "pro", "teams", "enterprise"
    quantity: int = 1  # For Teams tier (number of seats)


class CheckoutResponse(BaseModel):
    checkout_url: str
    session_id: str


class SubscriptionResponse(BaseModel):
    tier: str
    status: str
    current_period_start: str
    current_period_end: str
    cancel_at_period_end: bool
    stripe_subscription_id: str


class ChangePlanRequest(BaseModel):
    new_tier: str


class UsageResponse(BaseModel):
    tier: str
    usage: dict
    limits: dict
    billing_period: dict


# ── Checkout Endpoint ─────────────────────────────────────────────────────────

@router.post("/setup-checkout", response_model=CheckoutResponse)
async def setup_checkout(
    request: CheckoutRequest,
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db),
):
    """
    Create a Stripe Checkout session for subscription.
    
    **Step 1** in the payment flow:
    1. Frontend calls this endpoint
    2. Get checkout URL
    3. Redirect to Stripe Checkout
    4. User completes payment
    5. Redirect to success_url
    """
    try:
        # Validate tier
        try:
            tier = PricingTier(request.tier)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid tier: {request.tier}",
            )
        
        # Get organization
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )
        
        # Create checkout session
        checkout_url = StripeSubscriptionService.create_checkout_session(
            db=db,
            org_id=org_id,
            tier=tier,
            customer_email=org.meta.get("admin_email", "admin@example.com") if org.meta else "admin@example.com",
            quantity=request.quantity,
        )
        
        logger.info(f"Created checkout session for org {org_id}, tier {tier}")
        
        return CheckoutResponse(
            checkout_url=checkout_url,
            session_id=checkout_url.split("session_id=")[-1] if "session_id=" in checkout_url else "",
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating checkout: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create checkout session",
        )


# ── Get Subscription ──────────────────────────────────────────────────────────

@router.get("/subscription/{org_id}", response_model=Optional[SubscriptionResponse])
async def get_subscription(
    org_id: str,
    current_org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db),
):
    """
    Fetch subscription details for organization.
    
    Returns active subscription info:
    - Current tier
    - Billing cycle dates
    - Stripe subscription ID
    - Status (active, trialing, canceled, etc.)
    """
    # Verify access
    if org_id != current_org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    try:
        subscription = StripeSubscriptionService.get_active_subscription(db, org_id)
        
        if not subscription:
            # Return free tier default
            return {
                "tier": "free",
                "status": "active",
                "current_period_start": "",
                "current_period_end": "",
                "cancel_at_period_end": False,
                "stripe_subscription_id": "",
            }
        
        return SubscriptionResponse(
            tier=subscription.tier.value,
            status=subscription.status.value,
            current_period_start=subscription.current_period_start.isoformat(),
            current_period_end=subscription.current_period_end.isoformat(),
            cancel_at_period_end=subscription.cancel_at_period_end,
            stripe_subscription_id=subscription.stripe_subscription_id,
        )
        
    except Exception as e:
        logger.error(f"Error fetching subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch subscription",
        )


# ── Change Plan ───────────────────────────────────────────────────────────────

@router.patch("/subscription/{org_id}/change-plan")
async def change_plan(
    org_id: str,
    request: ChangePlanRequest,
    current_org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db),
):
    """
    Upgrade or downgrade subscription plan.
    
    Proration handled automatically:
    - Upgrade: credits applied to next invoice
    - Downgrade: invoice generated for difference
    """
    # Verify access
    if org_id != current_org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    try:
        # Validate new tier
        try:
            new_tier = PricingTier(request.new_tier)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid tier: {request.new_tier}",
            )
        
        # Change plan
        subscription = StripeSubscriptionService.change_plan(db, org_id, new_tier)
        
        logger.info(f"Changed subscription for org {org_id} to tier {new_tier}")
        
        return {
            "message": f"Plan changed to {new_tier.value}",
            "tier": subscription.tier.value,
            "status": subscription.status.value,
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error changing plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change plan",
        )


# ── Cancel Subscription ───────────────────────────────────────────────────────

@router.delete("/subscription/{org_id}/cancel")
async def cancel_subscription(
    org_id: str,
    immediate: bool = False,
    current_org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db),
):
    """
    Cancel subscription for organization.
    
    Parameters:
    - immediate: If true, cancel immediately. Otherwise cancel at end of billing period.
    """
    # Verify access
    if org_id != current_org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    try:
        subscription = StripeSubscriptionService.cancel_subscription(
            db, org_id, immediate=immediate
        )
        
        logger.info(f"Cancelled subscription for org {org_id}, immediate={immediate}")
        
        return {
            "message": "Subscription cancelled",
            "tier": subscription.tier.value,
            "status": subscription.status.value,
            "cancel_at_period_end": subscription.cancel_at_period_end,
            "canceled_at": subscription.canceled_at.isoformat() if subscription.canceled_at else None,
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error canceling subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel subscription",
        )


# ── Get Usage & Limits ────────────────────────────────────────────────────────

@router.get("/usage/{org_id}", response_model=UsageResponse)
async def get_usage(
    org_id: str,
    current_org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db),
):
    """
    Get current month usage and tier limits.
    
    Usage tracking:
    - projects_generated: incremented on each project creation
    - api_calls: tracked per API call
    - documents_created: tracked on document generation
    
    Returns:
    - Current usage counters
    - Tier limits
    - Billing period dates
    - Days remaining in period
    """
    # Verify access
    if org_id != current_org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    try:
        stats = UsageMetricsService.get_usage_stats(db, org_id)
        return UsageResponse(**stats)
        
    except Exception as e:
        logger.error(f"Error fetching usage: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch usage stats",
        )


# ── Check Project Limit (Internal) ────────────────────────────────────────────

@router.get("/can-generate-project/{org_id}")
async def can_generate_project(
    org_id: str,
    current_org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db),
):
    """
    Internal endpoint: Check if organization can generate another project.
    
    Called before project generation to enforce usage limits.
    
    Returns:
    - can_generate: bool
    - reason: string explaining if denied
    - remaining: int, projects remaining this month
    """
    # Verify access
    if org_id != current_org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    try:
        can_gen = UsageMetricsService.check_project_limit(db, org_id)
        
        if can_gen:
            stats = UsageMetricsService.get_usage_stats(db, org_id)
            remaining = stats["limits"]["max_projects_per_month"] - stats["usage"]["projects_generated"]
            return {
                "can_generate": True,
                "remaining": remaining,
                "tier": stats["tier"],
            }
        else:
            stats = UsageMetricsService.get_usage_stats(db, org_id)
            return {
                "can_generate": False,
                "reason": f"Tier {stats['tier']} limit ({stats['limits']['max_projects_per_month']} projects/month) reached",
                "tier": stats["tier"],
                "remaining": 0,
            }
        
    except Exception as e:
        logger.error(f"Error checking project limit: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check limit",
        )
