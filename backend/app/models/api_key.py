"""API Key model for programmatic access."""

import uuid
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base


class APIKey(Base):
    """API Key for programmatic/OAuth2 access to Axion-Pilot APIs."""
    
    __tablename__ = "api_keys"
    __table_args__ = (
        Index("ix_api_keys_org_id_active", "org_id", "active"),
        Index("ix_api_keys_key_prefix", "key_prefix"),
        Index("ix_api_keys_created_by", "created_by_user_id"),
        Index("ix_api_keys_id", "id"),
    )
    
    # Primary & Foreign Keys
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Key Fields
    name = Column(String(120), nullable=False)  # E.g., "ml-pipeline", "data-sync"
    key_prefix = Column(String(12), nullable=False, index=True)  # First 12 chars: "sk_axion_XXXX"
    key_hash = Column(String(255), nullable=False)  # bcrypt hash of full key
    
    # Permissions & Rate Limiting
    scopes = Column(JSON, nullable=False, default=list)  # ["read:projects", "write:projects"]
    rate_limit_rpm = Column(Integer, nullable=False, server_default="1000")  # Requests per minute
    
    # Timestamps & Status
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)  # Track usage patterns
    expires_at = Column(DateTime, nullable=True)  # Optional expiration
    active = Column(Boolean, nullable=False, default=True)  # Soft delete
    
    # Relationships
    organization = relationship("Organization", back_populates="api_keys")
    created_by = relationship("User", foreign_keys=[created_by_user_id])
    rate_limit_logs = relationship("RateLimitLog", cascade="all, delete-orphan", back_populates="api_key")
    
    def __repr__(self) -> str:
        return f"<APIKey id={self.id[:8]}... name={self.name} org={self.org_id[:8]}...>"
    
    @property
    def masked_key(self) -> str:
        """Return masked key for display: sk_axion_XXXX."""
        return self.key_prefix
    
    def is_active(self) -> bool:
        """Check if key is active (not revoked and not expired)."""
        if not self.active:
            return False
        if self.expires_at and self.expires_at < datetime.utcnow():
            return False
        return True
    
    def is_expired(self) -> bool:
        """Check if key has expired."""
        return self.expires_at is not None and self.expires_at < datetime.utcnow()
    
    def matches_scope(self, required_scope: str | List[str]) -> bool:
        """Check if API key has required scope(s)."""
        required_scopes = [required_scope] if isinstance(required_scope, str) else required_scope
        return any(scope in self.scopes for scope in required_scopes)
    
    def update_last_used(self, db_session=None) -> None:
        """Update last_used_at timestamp."""
        self.last_used_at = datetime.utcnow()
        if db_session:
            db_session.commit()
    
    def to_dict(self, include_prefix_only: bool = True) -> dict:
        """Convert to dictionary for API response."""
        if include_prefix_only:
            return {
                "id": self.id,
                "name": self.name,
                "key_prefix": self.masked_key,
                "scopes": self.scopes,
                "rate_limit_rpm": self.rate_limit_rpm,
                "created_at": self.created_at.isoformat(),
                "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
                "expires_at": self.expires_at.isoformat() if self.expires_at else None,
                "active": self.active,
            }
        # Full response (only on creation, never again)
        return {
            "id": self.id,
            "name": self.name,
            "key_prefix": self.masked_key,
            "scopes": self.scopes,
            "rate_limit_rpm": self.rate_limit_rpm,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }
