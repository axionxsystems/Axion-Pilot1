from datetime import datetime, date, timedelta
from sqlalchemy import func

from app.celery import app
from app.database import SessionLocal
from app.models.analytics import DailyAnalytics, FeatureUsage, UserActivity


@app.task(bind=True, max_retries=3)
def aggregate_daily_analytics(self, target_date: str | None = None):
    """Recalculate a daily analytics summary from raw feature and activity events."""
    if target_date:
        try:
            target_date = datetime.strptime(target_date, "%Y-%m-%d").date()
        except ValueError as exc:
            raise ValueError("target_date must be in YYYY-MM-DD format") from exc
    else:
        target_date = (date.today() - timedelta(days=1))

    db = SessionLocal()
    try:
        features_by_org = (
            db.query(FeatureUsage.org_id, FeatureUsage.feature_name, func.sum(FeatureUsage.count))
            .filter(FeatureUsage.date == target_date)
            .group_by(FeatureUsage.org_id, FeatureUsage.feature_name)
            .all()
        )

        activity_by_org = (
            db.query(UserActivity.org_id, func.count(func.distinct(UserActivity.user_id)))
            .filter(func.date(UserActivity.timestamp) == target_date)
            .group_by(UserActivity.org_id)
            .all()
        )

        org_active_users = {org_id: active_users for org_id, active_users in activity_by_org}
        org_feature_counts: dict[str, dict[str, int]] = {}

        for org_id, feature_name, count in features_by_org:
            org_feature_counts.setdefault(org_id, {})[feature_name] = int(count)

        for org_id, feature_counts in org_feature_counts.items():
            record = (
                db.query(DailyAnalytics)
                .filter(DailyAnalytics.org_id == org_id, DailyAnalytics.date == target_date)
                .first()
            )
            if not record:
                record = DailyAnalytics(org_id=org_id, date=target_date, features_used={})
                db.add(record)

            record.active_users = org_active_users.get(org_id, 0)
            record.features_used = feature_counts
            record.projects_generated = feature_counts.get("project_generation", record.projects_generated)
            record.failed_generations = feature_counts.get("failed_generation", record.failed_generations)
            record.documents_created = feature_counts.get("documents_created", record.documents_created)
            record.code_lines_generated = feature_counts.get("code_lines_generated", record.code_lines_generated)

            db.add(record)

        db.commit()
        return {
            "date": target_date,
            "updated_orgs": len(org_feature_counts),
            "rows_processed": len(features_by_org),
        }
    finally:
        db.close()
