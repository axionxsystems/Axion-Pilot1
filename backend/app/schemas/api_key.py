"""Pydantic schemas for API key routes."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


# ──────────────────────────────────────────────────────────────────────────────
# Request Schemas
# ──────────────────────────────────────────────────────────────────────────────

class APIKeyCreateRequest(BaseModel):
    """Request to create a new API key."""
    
    name: str = Field(
        ...,
        min_length=1,
        max_length=120,
        description="Human-readable name for this API key (e.g., 'ml-pipeline', 'data-sync')",
    )
    scopes: List[str] = Field(
        default=["read:projects"],
        description="List of scopes this key has access to",
    )
    rate_limit_rpm: int = Field(
        default=1000,
        ge=1,
        le=100000,
        description="Requests per minute limit",
    )
    expires_at: Optional[datetime] = Field(
        default=None,
        description="Optional expiration datetime. If not provided, key never expires.",
    )


class APIKeyUpdateRequest(BaseModel):
    """Request to update an existing API key."""
    
    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=120,
        description="New name for the key",
    )
    scopes: Optional[List[str]] = Field(
        default=None,
        description="New list of scopes",
    )
    rate_limit_rpm: Optional[int] = Field(
        default=None,
        ge=1,
        le=100000,
        description="New rate limit",
    )
    expires_at: Optional[datetime] = Field(
        default=None,
        description="New expiration datetime",
    )
    active: Optional[bool] = Field(
        default=None,
        description="Enable/disable the key without deleting it",
    )


# ──────────────────────────────────────────────────────────────────────────────
# Response Schemas
# ──────────────────────────────────────────────────────────────────────────────

class APIKeyResponse(BaseModel):
    """Response when creating an API key (includes full key, shown once only)."""
    
    id: str
    full_key: str = Field(
        ...,
        description="FULL API KEY (shown only on creation, never again). Store securely.",
    )
    name: str
    key_prefix: str = Field(..., description="First 12 characters for display: sk_axion_XXXX")
    scopes: List[str]
    rate_limit_rpm: int
    created_at: datetime
    expires_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "key-123abc",
                "full_key": "sk_axion_abcdef123456ghijkl789012mnopqr",
                "name": "ml-pipeline",
                "key_prefix": "sk_axion_abcd",
                "scopes": ["read:projects", "write:projects"],
                "rate_limit_rpm": 1000,
                "created_at": "2026-05-14T12:00:00Z",
                "expires_at": None,
            }
        }


class APIKeyListItemResponse(BaseModel):
    """Response when listing API keys (prefix only, no full key)."""
    
    id: str
    name: str
    key_prefix: str = Field(..., description="First 12 characters: sk_axion_XXXX")
    scopes: List[str]
    rate_limit_rpm: int
    created_at: datetime
    last_used_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    active: bool
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "key-123abc",
                "name": "ml-pipeline",
                "key_prefix": "sk_axion_abcd",
                "scopes": ["read:projects"],
                "rate_limit_rpm": 1000,
                "created_at": "2026-05-14T12:00:00Z",
                "last_used_at": "2026-05-14T12:30:15Z",
                "expires_at": None,
                "active": True,
            }
        }


class APIKeyListResponse(BaseModel):
    """Response for listing all API keys."""
    
    items: List[APIKeyListItemResponse]
    total: int


class APIKeyRotateResponse(BaseModel):
    """Response when rotating an API key."""
    
    old_key: APIKeyListItemResponse = Field(
        ...,
        description="The old key (now deprecated, marked inactive)"
    )
    new_key: APIKeyResponse = Field(
        ...,
        description="The new key (full key shown once only)"
    )
    message: str = Field(
        default="Key rotated successfully. Old key deprecated.",
        description="Additional message"
    )


class APIKeyErrorResponse(BaseModel):
    """Error response for API key operations."""
    
    error: str
    message: str
    details: Optional[dict] = None


# ──────────────────────────────────────────────────────────────────────────────
# Helper Functions
# ──────────────────────────────────────────────────────────────────────────────

def api_key_to_response(api_key, include_full_key: bool = False) -> dict:
    """Convert APIKey model to response dict."""
    response = {
        "id": api_key.id,
        "name": api_key.name,
        "key_prefix": api_key.key_prefix,
        "scopes": api_key.scopes,
        "rate_limit_rpm": api_key.rate_limit_rpm,
        "created_at": api_key.created_at,
        "last_used_at": api_key.last_used_at,
        "expires_at": api_key.expires_at,
        "active": api_key.active,
    }
    
    # Remove last_used_at if not set
    if response["last_used_at"] is None:
        del response["last_used_at"]
    
    return response


def api_key_to_list_response(api_key) -> dict:
    """Convert APIKey model to list response dict."""
    response = {
        "id": api_key.id,
        "name": api_key.name,
        "key_prefix": api_key.key_prefix,
        "scopes": api_key.scopes,
        "rate_limit_rpm": api_key.rate_limit_rpm,
        "created_at": api_key.created_at,
        "expires_at": api_key.expires_at,
        "active": api_key.active,
    }
    
    # Include last_used_at if available
    if api_key.last_used_at:
        response["last_used_at"] = api_key.last_used_at
    
    return response
