"""
Usage Enforcement Middleware - Block requests when usage limits exceeded.
Integrates with project generation and API calls.
"""
from functools import wraps
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import logging

from app.services.stripe_service import UsageMetricsService
from app.core.stripe_config import StripeErrorCode

logger = logging.getLogger(__name__)


class UsageLimitExceeded(HTTPException):
    """Raised when organization exceeds usage limits."""
    def __init__(self, tier: str, limit: int, current: int):
        super().__init__(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "error": StripeErrorCode.USAGE_LIMIT_EXCEEDED.value,
                "message": f"Tier '{tier}' allows {limit} projects/month. Current: {current}.",
                "tier": tier,
                "limit": limit,
                "current": current,
            },
        )


def enforce_project_limit(org_id: str, db: Session) -> bool:
    """
    Enforce project generation limit for organization.
    Raises 402 Payment Required if limit exceeded.
    
    Usage:
        from app.middleware.usage_enforcement import enforce_project_limit
        
        @router.post("/projects")
        async def create_project(org_id: str, db: Session = Depends(get_db)):
            enforce_project_limit(org_id, db)  # Raises if over limit
            # ... rest of project creation logic
    """
    can_generate = UsageMetricsService.check_project_limit(db, org_id)
    
    if not can_generate:
        stats = UsageMetricsService.get_usage_stats(db, org_id)
        raise UsageLimitExceeded(
            tier=stats["tier"],
            limit=stats["limits"]["max_projects_per_month"],
            current=stats["usage"]["projects_generated"],
        )
    
    logger.info(f"Project limit check passed for org {org_id}")
    return True


def enforce_api_call_limit(org_id: str, db: Session) -> bool:
    """
    Enforce API call limit for organization.
    Similar to project limit but for total API calls.
    """
    stats = UsageMetricsService.get_usage_stats(db, org_id)
    
    if stats["usage"]["api_calls"] >= stats["limits"]["max_api_calls"]:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "error": StripeErrorCode.USAGE_LIMIT_EXCEEDED.value,
                "message": f"API call limit ({stats['limits']['max_api_calls']}) exceeded for {stats['tier']} tier",
                "tier": stats["tier"],
                "limit": stats["limits"]["max_api_calls"],
                "current": stats["usage"]["api_calls"],
            },
        )
    
    return True


def increment_project_count(org_id: str, db: Session) -> None:
    """
    Increment project counter after successful project creation.
    
    Usage:
        # After project is successfully created:
        increment_project_count(org_id, db)
    """
    UsageMetricsService.increment_project_count(db, org_id, count=1)
    logger.info(f"Incremented project count for org {org_id}")


def increment_api_calls(org_id: str, db: Session, count: int = 1) -> None:
    """Increment API call counter."""
    UsageMetricsService.increment_api_calls(db, org_id, count=count)


# ── Decorator for Routes ──────────────────────────────────────────────────────

def require_project_limit(func):
    """
    Decorator: Check project limit before route execution.
    
    Usage:
        @router.post("/projects")
        @require_project_limit
        async def create_project(...):
            ...
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract org_id and db from kwargs
        org_id = kwargs.get("org_id") or (args[0] if args else None)
        db = kwargs.get("db") or next((arg for arg in args if isinstance(arg, Session)), None)
        
        if org_id and db:
            enforce_project_limit(org_id, db)
        
        return await func(*args, **kwargs)
    
    return wrapper
