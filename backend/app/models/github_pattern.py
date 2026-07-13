"""Cache of engineering-pattern digests mined from top open-source GitHub repos.

One row per (tech_stack, domain) cache key. The digest JSON holds *structural*
patterns only (directory layout, presence of tests/CI/Docker, repo attribution)
— never copied source code — distilled by app/services/github_insights.py and
injected into generation prompts so output mirrors how the best real-world
projects are engineered.
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, JSON

from app.database import Base


class GitHubPatternCache(Base):
    __tablename__ = "github_pattern_cache"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    # Normalized "tech|domain" key, e.g. "flask|web development"
    cache_key = Column(String(200), unique=True, nullable=False, index=True)
    digest = Column(JSON, nullable=False, default=dict)
    refreshed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
