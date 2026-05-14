"""Rate limit logging model for API key usage tracking."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base


class RateLimitLog(Base):
    """Log of API key rate limit usage for analytics and enforcement."""
    
    __tablename__ = "rate_limit_logs"
    __table_args__ = (
        Index("ix_rate_limit_logs_api_key_id", "api_key_id"),
        Index("ix_rate_limit_logs_timestamp", "timestamp"),
        Index("ix_rate_limit_logs_minute_bucket", "minute_bucket"),
        Index("ix_rate_limit_logs_composite", "api_key_id", "timestamp"),
    )
    
    # Primary & Foreign Keys
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    api_key_id = Column(String(36), ForeignKey("api_keys.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Tracking
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    request_count = Column(Integer, nullable=False, default=1)  # Requests in this time bucket
    minute_bucket = Column(String(20), nullable=False, index=True)  # E.g., "2026-05-14_12_30" for aggregation
    
    # Relationship
    api_key = relationship("APIKey", back_populates="rate_limit_logs")
    
    def __repr__(self) -> str:
        return f"<RateLimitLog api_key={self.api_key_id[:8]}... count={self.request_count} time={self.minute_bucket}>"
    
    @classmethod
    def get_minute_bucket(cls, dt: datetime = None) -> str:
        """
        Generate a minute bucket string for aggregation.
        
        Example: datetime(2026, 5, 14, 12, 30, 45) -> "2026-05-14_12_30"
        """
        if dt is None:
            dt = datetime.utcnow()
        return dt.strftime("%Y-%m-%d_%H_%M")
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API response."""
        return {
            "id": self.id,
            "api_key_id": self.api_key_id,
            "timestamp": self.timestamp.isoformat(),
            "request_count": self.request_count,
            "minute_bucket": self.minute_bucket,
        }
