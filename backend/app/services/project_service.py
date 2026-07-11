from collections import Counter
from datetime import datetime, date

from sqlalchemy.orm import Session

from app.models.analytics import DailyAnalytics, FeatureUsage, UserActivity
from app.models.project import Project, ProjectContent
from app.schemas.project import ProjectGenerateRequest
from app.core.generators.project_gen import generate_project
import logging
import os

logger = logging.getLogger(__name__)

class ProjectService:
    @staticmethod
    def _merge_feature_counts(existing: dict, new_counts: dict) -> dict:
        merged = Counter(existing or {})
        merged.update(new_counts or {})
        return dict(merged)

    @staticmethod
    def _get_or_create_daily_analytics(db: Session, org_id: str, analytics_date: date = None) -> DailyAnalytics:
        analytics_date = analytics_date or date.today()
        record = (
            db.query(DailyAnalytics)
            .filter(DailyAnalytics.org_id == org_id, DailyAnalytics.date == analytics_date)
            .first()
        )
        if not record:
            record = DailyAnalytics(org_id=org_id, date=analytics_date, features_used={})
            db.add(record)
            db.commit()
            db.refresh(record)
        return record

    @staticmethod
    def _log_feature_usage(db: Session, org_id: str, feature_name: str, count: int = 1):
        if count <= 0:
            return None
        entry = FeatureUsage(org_id=org_id, feature_name=feature_name, count=count)
        db.add(entry)
        db.commit()
        return entry

    @staticmethod
    def _record_user_activity(db: Session, org_id: str, user_id: int, action: str, resource_type: str = "project"):
        activity = UserActivity(
            org_id=org_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
        )
        db.add(activity)
        db.commit()
        return activity

    @staticmethod
    def log_generation_metrics(
        db: Session,
        org_id: str,
        user_id: int,
        duration_ms: int,
        documents_created: int,
        code_lines_generated: int,
        feature_names: list[str] | None = None,
        success: bool = True,
        failed: bool = False,
    ):
        analytics_date = date.today()
        record = ProjectService._get_or_create_daily_analytics(db, org_id, analytics_date)

        if success:
            old_total_projects = record.projects_generated
            accumulated_time = record.avg_generation_time_ms * old_total_projects
            record.projects_generated = old_total_projects + 1
            record.avg_generation_time_ms = (
                int((accumulated_time + duration_ms) / record.projects_generated)
                if record.projects_generated
                else 0
            )
            record.documents_created += documents_created
            record.code_lines_generated += code_lines_generated
            record.active_users += 1

            feature_counts = {
                "project_generation": 1,
                "documents_created": documents_created,
                "code_lines_generated": code_lines_generated,
            }
            if feature_names:
                for feature_name in feature_names:
                    if feature_name:
                        feature_counts[f"feature:{feature_name}"] = feature_counts.get(
                            f"feature:{feature_name}", 0
                        ) + 1

            record.features_used = ProjectService._merge_feature_counts(
                record.features_used, feature_counts
            )

        if failed:
            record.failed_generations += 1
            record.features_used = ProjectService._merge_feature_counts(
                record.features_used,
                {"failed_generation": 1},
            )

        db.add(record)
        db.commit()

        ProjectService._record_user_activity(
            db,
            org_id,
            user_id,
            action="PROJECT_GENERATION_FAILED" if failed else "PROJECT_GENERATION",
        )

        if success:
            ProjectService._log_feature_usage(db, org_id, "project_generation", 1)
        if failed:
            ProjectService._log_feature_usage(db, org_id, "failed_generation", 1)

        ProjectService._log_feature_usage(db, org_id, "documents_created", documents_created)
        ProjectService._log_feature_usage(db, org_id, "code_lines_generated", code_lines_generated)

        if feature_names:
            for feature_name in feature_names:
                ProjectService._log_feature_usage(db, org_id, f"feature:{feature_name}", 1)

        return record

    @staticmethod
    def create_project_skeleton(db: Session, user_id: int, org_id: str, request: ProjectGenerateRequest):
        """
        Initializes a new project in the database with org scoping.
        """
        db_project = Project(
            user_id=user_id,
            org_id=org_id,   # [Multi-tenancy]
            title=request.topic,
            tech_stack=request.techStack,
            difficulty=request.complexity,
            domain="General AI", # Default domain if not provided
            description=f"AI-generated project for {request.topic} using {request.techStack}"
        )
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        
        logger.info(f"Project created: {db_project.id} for user {user_id} in org {org_id}")
        return db_project

    @staticmethod
    def add_project_content(db: Session, project_id: int, content_type: str, content: any):
        """
        Adds or updates content for a specific project.
        """
        db_content = ProjectContent(
            project_id=project_id,
            type=content_type,
            content=content
        )
        db.add(db_content)
        db.commit()
        db.refresh(db_content)
        return db_content

    @staticmethod
    def get_project_full(db: Session, project_id: int, user_id: int, org_id: str = None):
        """
        Retrieves a project by ID ensuring it belongs to the user and their org.
        """
        query = db.query(Project).filter(Project.id == project_id, Project.user_id == user_id)
        if org_id:
            query = query.filter(Project.org_id == org_id)
        return query.first()

    @staticmethod
    def run_ai_pipeline(db: Session, db_project: Project):
        """
        Runs the actual AI generation pipeline and stores results in ProjectContent.
        """
        logger.info(f"Starting AI pipeline for project {db_project.id}")
        start_time = datetime.utcnow()

        try:
            # Use the existing generator
            ai_results = generate_project(
                api_key=None, # Will use env
                provider=os.getenv("AI_PROVIDER", "ollama"),
                domain=db_project.domain or "Engineering",
                topic=db_project.title,
                description=db_project.description or "",
                difficulty=db_project.difficulty,
                tech_stack=db_project.tech_stack,
                level="Advanced"
            )

            # Map AI results to ProjectContent types
            # sections: idea, architecture, modules, code, report, presentation, viva
            sections = {
                "idea": ai_results.get("abstract", ""),
                "architecture": ai_results.get("architecture_description", ""),
                "modules": ai_results.get("features", []),
                "code": {"files": ai_results.get("files", [])},
                "report": ai_results.get("abstract", ""), # Full report would be larger
                "presentation": {"slides": ai_results.get("logic_flow", "")},
                "viva": ai_results.get("viva_questions", [])
            }

            created_contents = []
            for section_type, content in sections.items():
                db_content = ProjectContent(
                    project_id=db_project.id,
                    type=section_type,
                    content=content
                )
                db.add(db_content)
                created_contents.append(db_content)

            db_project.progress = 100
            db.commit()

            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            documents_created = sum(
                1 for section_type, content in sections.items() if section_type != "code" and content
            )
            code_files = ai_results.get("files", []) or []
            code_lines = sum(
                len(str(file.get("content", "")).splitlines())
                for file in code_files
                if isinstance(file, dict)
            )
            feature_names = ai_results.get("features", []) or []
            ProjectService.log_generation_metrics(
                db,
                db_project.org_id,
                db_project.user_id,
                duration_ms,
                documents_created,
                code_lines,
                feature_names,
                success=True,
                failed=False,
            )

            logger.info(f"AI pipeline completed for project {db_project.id}")
            return created_contents

        except Exception as e:
            logger.error(f"AI Pipeline Failed: {e}")
            fallback_contents = ProjectService.run_mock_pipeline(db, db_project)
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            documents_created = len(fallback_contents)
            code_lines = sum(
                len(str(content).splitlines()) for content in fallback_contents if isinstance(content, dict)
            )
            ProjectService.log_generation_metrics(
                db,
                db_project.org_id,
                db_project.user_id,
                duration_ms,
                documents_created,
                code_lines,
                feature_names=None,
                success=True,
                failed=True,
            )
            return fallback_contents

    @staticmethod
    def run_mock_pipeline(db: Session, db_project: Project):
        """
        Fallback mock generation pipeline.
        """
        sections = {
            "idea": f"Comprehensive idea expansion for {db_project.title} using {db_project.tech_stack}.",
            "architecture": f"High-level system architecture designed for {db_project.difficulty} complexity.",
            "modules": ["Authentication", "Core Logic", "Database API", "Notification Service"],
            "code": {"structure": "src/", "files": ["main.py", "models.py", "utils.py"]},
            "report": f"Generated technical report for {db_project.title}.",
            "presentation": "Slide deck structure with 5 core slides.",
            "viva": ["Q: What is the core logic? A: ...", "Q: How do you handle scale? A: ..."]
        }

        created_contents = []
        for section_type, content in sections.items():
            db_content = ProjectContent(
                project_id=db_project.id,
                type=section_type,
                content=content
            )
            db.add(db_content)
            created_contents.append(db_content)

        db_project.progress = 100
        db.commit()
        return created_contents
    @staticmethod
    def list_projects(db: Session, user_id: int, org_id: str = None):
        """
        Lists all active projects for a specific user, optionally scoped by org.
        """
        query = db.query(Project).filter(
            Project.user_id == user_id,
            Project.status != "deleted"
        )
        if org_id:
            query = query.filter(Project.org_id == org_id)
        
        return query.order_by(Project.created_at.desc()).all()

    @staticmethod
    def get_user_stats(db: Session, user_id: int, org_id: str = None):
        """
        Retrieves project and activity stats for a user, scoped by org.
        """
        from app.models.activity import Activity
        
        project_query = db.query(Project).filter(Project.user_id == user_id)
        if org_id:
            project_query = project_query.filter(Project.org_id == org_id)
        
        project_count = project_query.count()
        
        # Activity is also org-scoped in a mature implementation, but for now we filter by user
        report_count = db.query(Activity).filter(
            Activity.user_id == user_id,
            Activity.action_type == "REPORT_GEN"
        ).count()
        ppt_count = db.query(Activity).filter(
            Activity.user_id == user_id,
            Activity.action_type == "PPT_GEN"
        ).count()
        
        # Calculate total viva questions across scoped projects
        projects = project_query.all()
        viva_count = sum(len(p.data.get("viva_questions", [])) for p in projects if isinstance(p.data, dict))

        return {
            "projects_generated": project_count,
            "reports_created": report_count,
            "presentations_created": ppt_count,
            "viva_questions": viva_count
        }

    @staticmethod
    def delete_project(db: Session, project_id: int, user_id: int, org_id: str = None):
        """
        Soft deletes or removes a project with org scoping.
        """
        query = db.query(Project).filter(Project.id == project_id, Project.user_id == user_id)
        if org_id:
            query = query.filter(Project.org_id == org_id)
        
        project = query.first()
        if project:
            project.status = "deleted"
            db.commit()
            return True
        return False
