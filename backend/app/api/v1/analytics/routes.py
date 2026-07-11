from datetime import date, datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth.org_dependencies import require_org_member, require_org_admin
from app.database import get_db
from app.models.analytics import DailyAnalytics, FeatureUsage

router = APIRouter()


@router.get("/overview")
def get_analytics_overview(
    days: int = 30,
    org_ctx=Depends(require_org_member),
    db: Session = Depends(get_db),
):
    _, org = org_ctx
    start_date = datetime.utcnow().date() - timedelta(days=days)
    daily_records: List[DailyAnalytics] = db.query(DailyAnalytics).filter(
        DailyAnalytics.org_id == org.id,
        DailyAnalytics.date >= start_date,
    ).order_by(DailyAnalytics.date.asc()).all()

    total_projects = sum(d.projects_generated for d in daily_records)
    avg_generation_time = (
        sum(d.avg_generation_time_ms for d in daily_records) / len(daily_records)
        if daily_records
        else 0
    )
    total_active_users = sum(d.active_users for d in daily_records)

    return {
        "period_days": days,
        "total_projects": total_projects,
        "avg_generation_time_ms": int(avg_generation_time),
        "total_active_users": total_active_users,
        "daily_data": [
            {
                "date": d.date,
                "projects": d.projects_generated,
                "active_users": d.active_users,
                "failed_generations": d.failed_generations,
            }
            for d in daily_records
        ],
    }


@router.get("/features")
def get_feature_usage(
    days: int = 30,
    org_ctx=Depends(require_org_member),
    db: Session = Depends(get_db),
):
    _, org = org_ctx
    start_date = datetime.utcnow().date() - timedelta(days=days)
    features = (
        db.query(FeatureUsage.feature_name, func.sum(FeatureUsage.count))
        .filter(
            FeatureUsage.org_id == org.id,
            FeatureUsage.date >= start_date,
        )
        .group_by(FeatureUsage.feature_name)
        .all()
    )

    return {
        "features": [
            {"name": feature, "usage_count": int(count)}
            for feature, count in features
        ]
    }


@router.get("/users")
def get_user_retention(
    org_ctx=Depends(require_org_member),
    db: Session = Depends(get_db),
):
    _, org = org_ctx
    last_30_days = (
        db.query(DailyAnalytics)
        .filter(
            DailyAnalytics.org_id == org.id,
            DailyAnalytics.date >= datetime.utcnow().date() - timedelta(days=30),
        )
        .order_by(DailyAnalytics.date.asc())
        .all()
    )

    return {
        "dau": [
            {"date": d.date, "active_users": d.active_users}
            for d in last_30_days
        ]
    }


@router.get("/export")
def export_analytics(
    format: str = "csv",
    org_ctx=Depends(require_org_admin),
    db: Session = Depends(get_db),
):
    _, org = org_ctx
    data = (
        db.query(DailyAnalytics)
        .filter(DailyAnalytics.org_id == org.id)
        .order_by(DailyAnalytics.date.asc())
        .all()
    )

    if format.lower() == "csv":
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "date",
            "projects_generated",
            "avg_generation_time_ms",
            "documents_created",
            "code_lines_generated",
            "active_users",
            "failed_generations",
        ])
        for d in data:
            writer.writerow([
                d.date,
                d.projects_generated,
                d.avg_generation_time_ms,
                d.documents_created,
                d.code_lines_generated,
                d.active_users,
                d.failed_generations,
            ])
        return JSONResponse(content={"csv": output.getvalue()})

    return {
        "data": [
            {
                "date": d.date,
                "projects_generated": d.projects_generated,
                "avg_generation_time_ms": d.avg_generation_time_ms,
                "documents_created": d.documents_created,
                "code_lines_generated": d.code_lines_generated,
                "active_users": d.active_users,
                "failed_generations": d.failed_generations,
                "features_used": d.features_used,
            }
            for d in data
        ]
    }

