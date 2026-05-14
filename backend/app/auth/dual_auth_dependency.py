"""Dual authentication: JWT or API key."""

from typing import Optional, Tuple, List
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.jwt_handler import verify_token
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.security.api_key import validate_api_key


class AuthContext:
    """Context object holding authentication information."""
    
    def __init__(
        self,
        org_id: str,
        user_id: Optional[int] = None,
        api_key_id: Optional[str] = None,
        scopes: Optional[List[str]] = None,
        auth_type: str = "jwt",
    ):
        self.org_id = org_id
        self.user_id = user_id
        self.api_key_id = api_key_id
        self.scopes = scopes or []
        self.auth_type = auth_type  # "jwt" or "api_key"
    
    @property
    def is_api_key(self) -> bool:
        """Check if authenticated via API key."""
        return self.auth_type == "api_key"
    
    @property
    def is_jwt(self) -> bool:
        """Check if authenticated via JWT."""
        return self.auth_type == "jwt"
    
    def has_scope(self, required_scope: str | List[str]) -> bool:
        """Check if context has required scope(s)."""
        if isinstance(required_scope, str):
            required_scope = [required_scope]
        
        # Admin scope implies all others
        if "admin:org" in self.scopes:
            return True
        
        return any(scope in self.scopes for scope in required_scope)


async def get_auth_context(
    request: Request,
    db: Session = Depends(get_db),
) -> AuthContext:
    """
    Resolve authentication context from either JWT or API key.
    
    Tries in order:
    1. Check Authorization header for API key (Bearer sk_axion_...)
    2. Fall back to JWT via existing OAuth2 flow
    3. Raise 401 if neither found
    
    Args:
        request: FastAPI request object
        db: Database session
    
    Returns:
        AuthContext with org_id, user_id, scopes, etc.
    
    Raises:
        HTTPException (401): If neither JWT nor API key is provided
    """
    authorization_header = request.headers.get("Authorization", "")
    
    # Try API key first (if header starts with "Bearer sk_axion_")
    if authorization_header.startswith("Bearer sk_axion_"):
        try:
            org_id, scopes, api_key_id = validate_api_key(authorization_header, db)
            return AuthContext(
                org_id=org_id,
                api_key_id=api_key_id,
                scopes=scopes,
                auth_type="api_key",
            )
        except HTTPException:
            # If API key validation fails, re-raise the error
            raise
    
    # Fall back to JWT
    try:
        # Use existing JWT dependency
        user: User = await get_current_user(
            token=authorization_header.replace("Bearer ", "") if authorization_header else "",
            db=db,
        )
        
        return AuthContext(
            org_id=user.org_id,
            user_id=user.id,
            scopes=["admin:org"],  # JWT users get full admin access for now
            auth_type="jwt",
        )
    except HTTPException:
        # If JWT fails, raise 401
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Provide either JWT or API key.",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def require_api_key() -> AuthContext:
    """
    Require API key authentication (reject JWT).
    
    Use this dependency when you want to enforce API key-only access.
    
    Example:
        @router.post("/webhook", dependencies=[Depends(require_api_key)])
        def webhook_handler():
            ...
    """
    async def dependency(auth: AuthContext = Depends(get_auth_context)) -> AuthContext:
        if not auth.is_api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key authentication required for this endpoint",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return auth
    
    return dependency


async def require_jwt() -> AuthContext:
    """
    Require JWT authentication (reject API key).
    
    Use this dependency when you want to enforce JWT-only access.
    """
    async def dependency(auth: AuthContext = Depends(get_auth_context)) -> AuthContext:
        if not auth.is_jwt:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="JWT authentication required for this endpoint",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return auth
    
    return dependency
