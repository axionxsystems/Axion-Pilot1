from pathlib import Path
import os
from dotenv import load_dotenv
# Use absolute path relative to this file to ensure .env is found from any CWD
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

import logging
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from app.database import engine, Base
from app.api import auth, users, projects, project, viva, admin, passkey
from app.limiter import limiter

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

# ── DB tables ─────────────────────────────────────────────────────────────────
# SQLite: Creates the database file on first run
Base.metadata.create_all(bind=engine)

# ── Environment ───────────────────────────────────────────────────────────────
ENV = os.environ.get("ENV", "development")
IS_PROD = ENV == "production"

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
_raw_origins = os.environ.get("ALLOWED_ORIGINS", "")
allowed_origins = (
    [o.strip() for o in _raw_origins.split(",") if o.strip()]
    if IS_PROD and _raw_origins
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

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(passkey.router, prefix="/api/auth", tags=["Passkey"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(project.router, prefix="/project", tags=["Project Generation"])
app.include_router(viva.router, prefix="/api/viva", tags=["Viva"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])


@app.get("/")
async def root():
    return {"message": "ProjectPilot API is running", "env": ENV}


@app.get("/health")
async def health():
    """Health check endpoint for auto-heal platform checks."""
    return {"status": "ok", "env": ENV}
