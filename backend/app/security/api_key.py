"""API Key security: generation, hashing, and validation."""

import secrets
import string
from typing import Tuple, Optional, List
from datetime import datetime
from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.models.api_key import APIKey

# Bcrypt context for API key hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# API key prefix and length constants
API_KEY_PREFIX = "sk_axion_"
API_KEY_RANDOM_LENGTH = 40  # 40 chars after prefix = 48 total
API_KEY_DISPLAY_LENGTH = 12  # Show first 12 chars: sk_axion_XXXX


def generate_api_key() -> Tuple[str, str, str]:
    """
    Generate a new API key with prefix, and return key, prefix, and hash.
    
    Returns:
        Tuple of (full_key, key_prefix, key_hash)
        - full_key: Complete key (sk_axion_XXX...), shown to user ONE TIME ONLY
        - key_prefix: First 12 characters for display (sk_axion_XXXX)
        - key_hash: Bcrypt hash for storage in database
    
    Example:
        full_key, prefix, hash = generate_api_key()
        # full_key = "sk_axion_abc123def456..."  (48 chars)
        # prefix = "sk_axion_abc1"             (12 chars)
        # hash = "$2b$12$..."
    """
    # Generate cryptographically secure random string
    # Use alphanumeric (both cases) for readability
    random_chars = ''.join(
        secrets.choice(string.ascii_letters + string.digits)
        for _ in range(API_KEY_RANDOM_LENGTH)
    )
    
    full_key = f"{API_KEY_PREFIX}{random_chars}"
    key_prefix = full_key[:API_KEY_DISPLAY_LENGTH]
    key_hash = hash_api_key(full_key)
    
    return full_key, key_prefix, key_hash


def hash_api_key(key: str) -> str:
    """
    Hash an API key using bcrypt.
    
    Args:
        key: The full API key string (e.g., "sk_axion_abc123...")
    
    Returns:
        Bcrypt hash of the key
    """
    return pwd_context.hash(key)


def verify_api_key(plain_key: str, hashed_key: str) -> bool:
    """
    Verify a plain API key against a bcrypt hash.
    
    Args:
        plain_key: The full API key string provided by user
        hashed_key: The bcrypt hash from database
    
    Returns:
        True if key matches hash, False otherwise
    """
    return pwd_context.verify(plain_key, hashed_key)


def extract_bearer_token(authorization_header: str) -> Optional[str]:
    """
    Extract token from Authorization header.
    
    Supports:
        - "Bearer sk_axion_..." → "sk_axion_..."
        - "Bearer eyJ..." → "eyJ..." (JWT)
        - Invalid formats → None
    
    Args:
        authorization_header: Value of Authorization header
    
    Returns:
        Token string or None if invalid format
    """
    if not authorization_header:
        return None
    
    parts = authorization_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    
    return parts[1]


def validate_api_key(
    authorization_header: str,
    db: Session,
) -> Tuple[str, List[str], str]:
    """
    Validate an API key from Authorization header.
    
    Performs the following checks:
    1. Parse "Bearer sk_axion_..." format
    2. Look up key by prefix (first 12 chars)
    3. Verify key hash matches
    4. Check key is active (not revoked)
    5. Check key is not expired
    6. Update last_used_at timestamp
    
    Args:
        authorization_header: Value of Authorization header
        db: Database session
    
    Returns:
        Tuple of (org_id, scopes, api_key_id)
    
    Raises:
        HTTPException (401): If key is invalid, expired, inactive, or not found
        HTTPException (403): If key hash doesn't match
    
    Example:
        org_id, scopes, key_id = validate_api_key(
            "Bearer sk_axion_abc123...",
            db
        )
        # org_id = "org-123"
        # scopes = ["read:projects", "write:projects"]
        # key_id = "key-abc123"
    """
    # Extract token from header
    token = extract_bearer_token(authorization_header)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format. Use 'Bearer sk_axion_...'",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if it's an API key (starts with prefix)
    if not token.startswith(API_KEY_PREFIX):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key format. API keys must start with 'sk_axion_'",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract prefix (first 12 chars) for DB lookup
    key_prefix = token[:API_KEY_DISPLAY_LENGTH]
    
    # Look up API key by prefix
    api_key = db.query(APIKey).filter(
        APIKey.key_prefix == key_prefix,
        APIKey.active == True,
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify the full key matches the stored hash
    if not verify_api_key(token, api_key.key_hash):
        # This shouldn't happen in normal flow, but could indicate tampering
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key verification failed",
        )
    
    # Check if key is expired
    if api_key.is_expired():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last_used_at for usage tracking
    api_key.last_used_at = datetime.utcnow()
    db.add(api_key)
    try:
        db.commit()
    except Exception:
        db.rollback()  # Don't fail the request if we can't update timestamp
    
    return api_key.org_id, api_key.scopes, api_key.id
