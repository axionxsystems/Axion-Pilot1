import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class SSOConfig(Base):
    __tablename__ = "sso_configs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    sso_method = Column(String(20), nullable=False)
    saml_domain = Column(String(255), nullable=True)
    auto_provision = Column(Boolean, default=True, nullable=False)
    require_mfa = Column(Boolean, default=False, nullable=False)
    allowed_domains = Column(JSON, nullable=True, default=list)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    organization = relationship("Organization")


class SSOSession(Base):
    __tablename__ = "sso_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    sso_method = Column(String(20), nullable=False)
    state = Column(String(255), nullable=False, unique=True, index=True)
    nonce = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)

    organization = relationship("Organization")
    user = relationship("User")
