from sqlalchemy.orm import Session
from app.models.project import Project, ProjectContent
from app.schemas.project import ProjectGenerateRequest
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ProjectService:
    @staticmethod
    def create_project_skeleton(db: Session, user_id: int, request: ProjectGenerateRequest):
        """
        Initializes a new project in the database.
        """
        db_project = Project(
            user_id=user_id,
            topic=request.topic,
            tech_stack=request.techStack,
            complexity=request.complexity
        )
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        
        logger.info(f"Project created: {db_project.id} for user {user_id}")
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
    def get_project_full(db: Session, project_id: int, user_id: int):
        """
        Retrieves a project by ID ensuring it belongs to the user.
        """
        return db.query(Project).filter(Project.id == project_id, Project.user_id == user_id).first()

    # AI Pipeline Mock Integration
    @staticmethod
    def run_mock_pipeline(db: Session, db_project: Project):
        """
        Runs a mock generation pipeline and stores each section in ProjectContent.
        """
        sections = {
            "idea": f"Comprehensive idea expansion for {db_project.topic} using {db_project.tech_stack}.",
            "architecture": f"High-level system architecture designed for {db_project.complexity} complexity.",
            "modules": ["Authentication", "Core Logic", "Database API", "Notification Service"],
            "code": {"structure": "src/", "files": ["main.py", "models.py", "utils.py"]},
            "report": f"Generated technical report for {db_project.topic}.",
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
        
        db.commit()
        logger.info(f"Mock pipeline completed for project {db_project.id}")
        return created_contents
