from fastapi import APIRouter
from app.api.admin import infrastructure, dashboard

router = APIRouter()

router.include_router(dashboard.router)
router.include_router(infrastructure.router)
