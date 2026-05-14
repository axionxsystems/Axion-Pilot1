"""API key management routes."""

import uuid
from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.api_key import APIKey
from app.models.user import User
from app.auth.dependencies import get_current_user
from app.auth.dual_auth_dependency import get_auth_context, AuthContext
from app.security.api_key import generate_api_key
from app.schemas.api_key import (
    APIKeyCreateRequest,
    APIKeyUpdateRequest,
    APIKeyResponse,
    APIKeyListItemResponse,
    APIKeyListResponse,
    APIKeyRotateResponse,
)

router = APIRouter()


# ──────────────────────────────────────────────────────────────────────────────
# POST /api-keys — Create a new API key
# ──────────────────────────────────────────────────────────────────────────────

@router.post(
    "/",
    response_model=APIKeyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new API key",
    description="Generate a new API key for programmatic access. The full key is returned only once and should be stored securely.",
)
async def create_api_key(
    request: APIKeyCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> APIKeyResponse:
    """
    Create a new API key for the current user's organization.
    
    Returns the full key ONCE. After this, only the prefix is shown.
    """
    if not current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to an organization to create API keys",
        )
    
    # Validate scopes
    from app.security.scopes import validate_scopes
    if not validate_scopes(request.scopes):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid scope(s) provided",
        )
    
    # Generate the API key
    full_key, key_prefix, key_hash = generate_api_key()
    
    # Create API key record in database
    api_key = APIKey(
        id=str(uuid.uuid4()),
        org_id=current_user.org_id,
        created_by_user_id=current_user.id,
        name=request.name,
        key_prefix=key_prefix,
        key_hash=key_hash,
        scopes=request.scopes,
        rate_limit_rpm=request.rate_limit_rpm,
        expires_at=request.expires_at,
        active=True,
    )
    
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    
    return APIKeyResponse(
        id=api_key.id,
        full_key=full_key,
        name=api_key.name,
        key_prefix=api_key.key_prefix,
        scopes=api_key.scopes,
        rate_limit_rpm=api_key.rate_limit_rpm,
        created_at=api_key.created_at,
        expires_at=api_key.expires_at,
    )


# ──────────────────────────────────────────────────────────────────────────────
# GET /api-keys — List all API keys for the current org
# ──────────────────────────────────────────────────────────────────────────────

@router.get(
    "/",
    response_model=APIKeyListResponse,
    summary="List API keys",
    description="List all API keys for the current organization (shows prefix only, no full keys).",
)
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    active_only: bool = Query(False, description="Filter to active keys only"),
    db: Session = Depends(get_db),
) -> APIKeyListResponse:
    """
    List all API keys for the current user's organization.
    
    Only shows key prefix (first 12 chars), never the full key.
    """
    if not current_user.org_id:
        return APIKeyListResponse(items=[], total=0)
    
    query = db.query(APIKey).filter(APIKey.org_id == current_user.org_id)
    
    if active_only:
        query = query.filter(APIKey.active == True)
    
    api_keys = query.order_by(APIKey.created_at.desc()).all()
    
    items = [
        APIKeyListItemResponse(
            id=key.id,
            name=key.name,
            key_prefix=key.key_prefix,
            scopes=key.scopes,
            rate_limit_rpm=key.rate_limit_rpm,
            created_at=key.created_at,
            last_used_at=key.last_used_at,
            expires_at=key.expires_at,
            active=key.active,
        )
        for key in api_keys
    ]
    
    return APIKeyListResponse(items=items, total=len(items))


# ──────────────────────────────────────────────────────────────────────────────
# PATCH /api-keys/{key_id} — Update an API key
# ──────────────────────────────────────────────────────────────────────────────

@router.patch(
    "/{key_id}",
    response_model=APIKeyListItemResponse,
    summary="Update an API key",
    description="Update name, scopes, rate limit, expiry, or active status of an API key.",
)
async def update_api_key(
    key_id: str,
    request: APIKeyUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> APIKeyListItemResponse:
    """
    Update an API key's settings.
    
    Can update: name, scopes, rate_limit_rpm, expires_at, active
    """
    if not current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must belong to an organization",
        )
    
    # Get the API key and verify ownership
    api_key = db.query(APIKey).filter(
        APIKey.id == key_id,
        APIKey.org_id == current_user.org_id,
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )
    
    # Validate new scopes if provided
    if request.scopes is not None:
        from app.security.scopes import validate_scopes
        if not validate_scopes(request.scopes):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid scope(s) provided",
            )
        api_key.scopes = request.scopes
    
    # Update fields
    if request.name is not None:
        api_key.name = request.name
    if request.rate_limit_rpm is not None:
        api_key.rate_limit_rpm = request.rate_limit_rpm
    if request.expires_at is not None:
        api_key.expires_at = request.expires_at
    if request.active is not None:
        api_key.active = request.active
    
    db.commit()
    db.refresh(api_key)
    
    return APIKeyListItemResponse(
        id=api_key.id,
        name=api_key.name,
        key_prefix=api_key.key_prefix,
        scopes=api_key.scopes,
        rate_limit_rpm=api_key.rate_limit_rpm,
        created_at=api_key.created_at,
        last_used_at=api_key.last_used_at,
        expires_at=api_key.expires_at,
        active=api_key.active,
    )


# ──────────────────────────────────────────────────────────────────────────────
# DELETE /api-keys/{key_id} — Revoke an API key
# ──────────────────────────────────────────────────────────────────────────────

@router.delete(
    "/{key_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke an API key",
    description="Revoke (deactivate) an API key. The key can be re-activated if needed.",
)
async def delete_api_key(
    key_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """
    Revoke an API key (soft delete via active=false).
    
    The key record is retained for audit purposes.
    """
    if not current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must belong to an organization",
        )
    
    # Get the API key and verify ownership
    api_key = db.query(APIKey).filter(
        APIKey.id == key_id,
        APIKey.org_id == current_user.org_id,
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )
    
    # Soft delete (set active=false)
    api_key.active = False
    db.commit()


# ──────────────────────────────────────────────────────────────────────────────
# POST /api-keys/{key_id}/rotate — Rotate an API key
# ──────────────────────────────────────────────────────────────────────────────

@router.post(
    "/{key_id}/rotate",
    response_model=APIKeyRotateResponse,
    summary="Rotate an API key",
    description="Generate a new API key and deprecate the old one. Useful for key rotation/security refresh.",
)
async def rotate_api_key(
    key_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> APIKeyRotateResponse:
    """
    Rotate an API key by creating a new one and deprecating the old one.
    
    Returns both keys for smooth transition period.
    """
    if not current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must belong to an organization",
        )
    
    # Get the old API key
    old_api_key = db.query(APIKey).filter(
        APIKey.id == key_id,
        APIKey.org_id == current_user.org_id,
    ).first()
    
    if not old_api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )
    
    # Generate new API key with same settings
    full_key, key_prefix, key_hash = generate_api_key()
    
    new_api_key = APIKey(
        id=str(uuid.uuid4()),
        org_id=current_user.org_id,
        created_by_user_id=current_user.id,
        name=f"{old_api_key.name} (rotated)",
        key_prefix=key_prefix,
        key_hash=key_hash,
        scopes=old_api_key.scopes,
        rate_limit_rpm=old_api_key.rate_limit_rpm,
        expires_at=old_api_key.expires_at,
        active=True,
    )
    
    # Deprecate old key
    old_api_key.active = False
    
    db.add(new_api_key)
    db.commit()
    db.refresh(old_api_key)
    db.refresh(new_api_key)
    
    return APIKeyRotateResponse(
        old_key=APIKeyListItemResponse(
            id=old_api_key.id,
            name=old_api_key.name,
            key_prefix=old_api_key.key_prefix,
            scopes=old_api_key.scopes,
            rate_limit_rpm=old_api_key.rate_limit_rpm,
            created_at=old_api_key.created_at,
            last_used_at=old_api_key.last_used_at,
            expires_at=old_api_key.expires_at,
            active=old_api_key.active,
        ),
        new_key=APIKeyResponse(
            id=new_api_key.id,
            full_key=full_key,
            name=new_api_key.name,
            key_prefix=new_api_key.key_prefix,
            scopes=new_api_key.scopes,
            rate_limit_rpm=new_api_key.rate_limit_rpm,
            created_at=new_api_key.created_at,
            expires_at=new_api_key.expires_at,
        ),
    )
