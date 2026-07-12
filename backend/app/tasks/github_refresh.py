"""
Periodic refresh of GitHub engineering-pattern digests.

Runs weekly via Celery beat. Refreshes the pattern cache for:
  1. A seed list of popular stacks (so first-time users get instant patterns).
  2. Every distinct (tech_stack, domain) users actually generated in the last
     30 days — the corpus automatically tracks what your users build.

Failures are per-key and non-fatal; the cache simply serves stale digests
until the next successful refresh.
"""
import logging
from datetime import datetime, timedelta

from app.celery import app
from app.database import SessionLocal

logger = logging.getLogger(__name__)

SEED_STACKS = [
    ("python flask", "web development"),
    ("python fastapi", "web development"),
    ("react", "web development"),
    ("next.js", "web development"),
    ("python", "machine learning"),
    ("node.js express", "web development"),
    ("django", "web development"),
    ("android kotlin", "mobile development"),
]


@app.task(bind=True, max_retries=1)
def refresh_github_patterns(self):
    from app.models.project import Project
    from app.services.github_insights import refresh_patterns, _normalize_key

    db = SessionLocal()
    refreshed, failed = 0, 0
    try:
        # Stacks users actually generated recently
        cutoff = datetime.utcnow() - timedelta(days=30)
        recent = (
            db.query(Project.tech_stack, Project.domain)
            .filter(Project.created_at >= cutoff)
            .distinct()
            .limit(50)
            .all()
        )
        # Merge with seeds, dedupe on normalized cache key
        targets, seen = [], set()
        for tech, dom in [*SEED_STACKS, *[(t or "", d or "") for t, d in recent]]:
            key = _normalize_key(tech, dom)
            if key not in seen:
                seen.add(key)
                targets.append((tech, dom))

        for tech, dom in targets:
            try:
                if refresh_patterns(db, tech, dom):
                    refreshed += 1
                else:
                    failed += 1
            except Exception as e:
                failed += 1
                logger.warning("Pattern refresh failed for %r/%r: %s", tech, dom, e)

        logger.info("GitHub pattern refresh done: %d refreshed, %d failed/empty", refreshed, failed)
        return {"refreshed": refreshed, "failed": failed}
    finally:
        db.close()
