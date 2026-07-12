from pathlib import Path
import os
from dotenv import load_dotenv
# Use absolute path relative to this file to ensure .env is found from any CWD
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

# from app.utils.ollama_generator import generate_code, generate_documentation, generate_viva_questions


from app.core.config import settings
from app.core.observability import setup_logging, init_sentry, RequestIDMiddleware
from app.database import engine, Base
from app.api import auth, users, projects, viva, passkey, admin
from app.api import v1
from app.limiter import limiter
from app.middleware.tenant import TenantMiddleware

# ── Ensure all models are imported so create_all sees them ────────────────────
import app.models  # noqa: F401 — registers every model module (see app/models/__init__.py)

# ── Config validation, logging & error tracking ───────────────────────────────
# Fail fast if a production deployment is misconfigured (weak SECRET_KEY, SQLite,
# missing CORS origins). No-op in development.
settings.validate_production()
setup_logging()
init_sentry()

# ── Environment ───────────────────────────────────────────────────────────────
ENV = settings.ENV
IS_PROD = settings.is_production

# ── DB tables ─────────────────────────────────────────────────────────────────
# SQLite (dev): creates the database file on first run. In production, schema is
# managed by Alembic migrations, so only auto-create outside production.
if not IS_PROD:
    Base.metadata.create_all(bind=engine)

# ── Security headers middleware ────────────────────────────────────────────────
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        # CSP: restrict resource origins for security
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        if IS_PROD:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="AxionX API",
    version="1.1.0",
    docs_url="/docs" if not IS_PROD else None,
    redoc_url="/redoc" if not IS_PROD else None,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
# Restricted Origins: no wildcards in production
# Allow all origins in dev for easier testing from different hosts/IPs
allowed_origins = (
    settings.allowed_origins_list
    if IS_PROD and settings.allowed_origins_list
    else ["*"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    # Wildcard origin ("*") cannot be used with allow_credentials=True
    allow_credentials=False if not IS_PROD else True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# ── Middlewares & Handlers ────────────────────────────────────────────────────
# The middlewares listed below are WRAPPED by the CORS middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SecurityHeadersMiddleware)
# RequestIDMiddleware: correlate logs/errors per request via X-Request-ID.
app.add_middleware(RequestIDMiddleware)

# TenantMiddleware: extracts org_id from JWT and stores in context var.
# Registered AFTER SecurityHeaders so it runs on the inner side of the stack.
app.add_middleware(TenantMiddleware, secret_key=settings.SECRET_KEY)

# RateLimitMiddleware: enforces rate limits for API keys
from app.middleware.rate_limiting import RateLimitMiddleware
app.add_middleware(RateLimitMiddleware)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(passkey.router, prefix="/api/auth", tags=["Passkey"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(viva.router, prefix="/api/viva", tags=["Viva"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(v1.router, prefix="/api/v1")

# WebSocket router
from app.websocket.progress import router as websocket_router
app.include_router(websocket_router)


@app.get("/")
async def root():
    return {"message": "ProjectPilot API is running", "env": ENV}


@app.get("/health")
async def health():
    """Liveness probe — process is up. Cheap, no dependencies touched."""
    return {"status": "ok", "env": ENV}


@app.get("/ready")
async def ready():
    """Readiness probe — verifies the database is reachable before taking traffic."""
    from sqlalchemy import text
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        logging.getLogger(__name__).error("Readiness check failed: %s", e)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unavailable", "detail": "database unreachable"},
        )
    return {"status": "ready", "env": ENV}



