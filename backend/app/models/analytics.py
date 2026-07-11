import uuid
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, JSON, DateTime, DATE, ForeignKey
from app.database import Base


def _uuid_pk():
    return Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)


class DailyAnalytics(Base):
    __tablename__ = "daily_analytics"

    id = _uuid_pk()
    org_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(DATE, default=date.today, nullable=False, index=True)
    projects_generated = Column(Integer, default=0, nullable=False)
    avg_generation_time_ms = Column(Integer, default=0, nullable=False)
    documents_created = Column(Integer, default=0, nullable=False)
    code_lines_generated = Column(Integer, default=0, nullable=False)
    active_users = Column(Integer, default=0, nullable=False)
    failed_generations = Column(Integer, default=0, nullable=False)
    features_used = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class FeatureUsage(Base):
    __tablename__ = "feature_usage"

    id = _uuid_pk()
    org_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    feature_name = Column(String(120), nullable=False, index=True)
    count = Column(Integer, default=1, nullable=False)
    date = Column(DATE, default=date.today, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class UserActivity(Base):
    __tablename__ = "user_activity"

    id = _uuid_pk()
    org_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    action = Column(String(120), nullable=False)
    resource_type = Column(String(120), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class RevenueMetrics(Base):
    __tablename__ = "revenue_metrics"

    id = _uuid_pk()
    org_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(DATE, default=date.today, nullable=False, index=True)
    mrr = Column(Integer, default=0, nullable=False)
    new_customers = Column(Integer, default=0, nullable=False)
    churned_customers = Column(Integer, default=0, nullable=False)
    expansion_mrr = Column(Integer, default=0, nullable=False)
    ltv_estimate = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
