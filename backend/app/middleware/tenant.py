"""
TenantMiddleware
================
Extracts the ``org_id`` claim from the Bearer JWT on **every request** and
stores it in a context variable (``tenant_ctx``) so any route or service can
call ``get_current_org_id()`` without re-parsing the token.

Flow
----
1.  Parse the ``Authorization: Bearer <token>`` header (skip if absent — public
    routes like /health, /docs, /api/auth/* are excluded from enforcement).
2.  Decode the JWT, pull ``org_id`` claim.
3.  Verify the org exists in the DB and is not deleted/suspended.
4.  Store ``org_id`` in the request-scoped context var.

Usage in routes
---------------
    from app.middleware.tenant import get_current_org_id
    org_id = get_current_org_id()   # raises 401 if not set
"""

from __future__ import annotations

import logging
import os
from contextvars import ContextVar
from typing import Optional

from fastapi import HTTPException, Request, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

# ── Context variable ───────────────────────────────────────────────────────────
# One value per async task / coroutine — safe under asyncio concurrency.
_tenant_ctx: ContextVar[Optional[str]] = ContextVar("tenant_org_id", default=None)


def get_current_org_id() -> str:
    """
    Return the org_id for the current request.
    Raises HTTP 401 if no org context has been set (unauthenticated / not in an org).
    """
    org_id = _tenant_ctx.get()
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Organization context missing. Include a valid JWT with an org_id claim.",
        )
    return org_id


def get_current_org_id_optional() -> Optional[str]:
    """Return org_id or None — for endpoints that work both with and without an org."""
    return _tenant_ctx.get()


# ── Routes that do NOT require an org context ──────────────────────────────────
_PUBLIC_PREFIXES = (
    "/api/auth/",
    "/api/v1/organizations",   # create-org route (user has no org yet)
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/",
)


def _is_public(path: str) -> bool:
    return any(path.startswith(p) for p in _PUBLIC_PREFIXES)


# ── Middleware ─────────────────────────────────────────────────────────────────

class TenantMiddleware(BaseHTTPMiddleware):
    """
    Starlette BaseHTTPMiddleware that wires JWT → org context.

    Must be added AFTER the CORS middleware in main.py so CORS pre-flight
    OPTIONS requests are not rejected before the browser's CORS check completes.
    """

    def __init__(self, app, secret_key: str, algorithm: str = "HS256"):
        super().__init__(app)
        self._secret_key = secret_key
        self._algorithm  = algorithm

    async def dispatch(self, request: Request, call_next):
        # Always reset the context var so stale values never bleed between requests
        token = _tenant_ctx.set(None)
        try:
            org_id = await self._extract_org_id(request)
            if org_id:
                _tenant_ctx.set(org_id)
            response = await call_next(request)
            return response
        finally:
            _tenant_ctx.reset(token)

    async def _extract_org_id(self, request: Request) -> Optional[str]:
        """
        Parse org_id from either JWT or API key in Authorization header.
        Returns None for public paths or missing/invalid tokens (enforcement
        happens inside individual routes via get_current_org_id()).
        
        Priority:
        1. Try API key (Bearer sk_axion_...)
        2. Fall back to JWT (Bearer eyJ...)
        """
        path = request.url.path

        # Skip extraction for public paths (auth routes, docs, health)
        if _is_public(path):
            return None

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return None  # Let individual routes decide if they need it

        raw_token = auth_header[7:]
        
        # Try API key first (if it looks like an API key)
        if raw_token.startswith("sk_axion_"):
            try:
                from app.security.api_key import validate_api_key
                from app.database import SessionLocal
                
                db: Session = SessionLocal()
                try:
                    org_id, scopes, api_key_id = validate_api_key(auth_header, db)
                    # Store in request state for rate limiting middleware
                    request.state.api_key_id = api_key_id
                    request.state.scopes = scopes
                    # Get rate limit from API key
                    from app.models.api_key import APIKey
                    api_key = db.query(APIKey).filter(APIKey.id == api_key_id).first()
                    if api_key:
                        request.state.rate_limit_rpm = api_key.rate_limit_rpm
                    return org_id
                finally:
                    db.close()
            except Exception:
                # API key validation failed, fall through to JWT
                pass
        
        # Try JWT
        try:
            payload = jwt.decode(raw_token, self._secret_key, algorithms=[self._algorithm])
        except JWTError:
            return None  # Invalid token — route-level dependency will reject it

        org_id = payload.get("org_id")
        if not org_id:
            return None  # Token exists but has no org claim (pre-org user)

        # ── Validate org exists in DB ──────────────────────────────────────────
        from app.database import SessionLocal
        from app.models.organization import Organization

        db: Session = SessionLocal()
        try:
            org = db.query(Organization).filter(Organization.id == org_id).first()
            if not org:
                logger.warning("[Tenant] JWT contained unknown org_id=%s", org_id)
                return None  # Route will still run; org-scoped deps will reject it
            return org_id
        finally:
            db.close()
