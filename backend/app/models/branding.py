from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from app.database import Base


def _uuid_pk():
    from sqlalchemy import Column, String
    import uuid
    return Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)


class OrgBranding(Base):
    __tablename__ = "org_branding"

    id = _uuid_pk()
    org_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    brand_name = Column(String(120), nullable=True)
    primary_color = Column(String(7), nullable=True)
    secondary_color = Column(String(7), nullable=True)
    accent_color = Column(String(7), nullable=True)
    support_email = Column(String(255), nullable=True)

    logo_filename = Column(String(255), nullable=True)
    logo_content_type = Column(String(80), nullable=True)
    logo_data = Column(LargeBinary, nullable=True)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    organization = relationship("Organization", back_populates="branding")
