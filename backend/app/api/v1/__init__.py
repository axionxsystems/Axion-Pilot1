from fastapi import APIRouter
from .projects import routes as projects
from .organizations import routes as organizations
from .subscriptions import routes as subscriptions
from .webhooks import routes as webhooks
from .api_keys import routes as api_keys
from .analytics import routes as analytics
from .templates import routes as templates
from .billing import router as billing_router
from .teams import router as teams
from .branding import routes as branding
from .code import routes as code_routes

router = APIRouter()

router.include_router(projects.router, prefix="/projects", tags=["Projects"])
router.include_router(organizations.router, prefix="/organizations", tags=["Organizations"])
router.include_router(subscriptions.router, prefix="/subscriptions", tags=["Subscriptions"])
router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
router.include_router(api_keys.router, prefix="/api_keys", tags=["API Keys"])
router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
router.include_router(templates.router, prefix="/templates", tags=["Templates"])
router.include_router(billing_router, prefix="/billing", tags=["Stripe Billing"])
router.include_router(teams, prefix="/teams", tags=["Teams"])
router.include_router(branding.router, prefix="/organizations", tags=["Branding"])
router.include_router(code_routes.router, prefix="/code", tags=["Code Editor"]) 
