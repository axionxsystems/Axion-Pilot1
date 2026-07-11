from sqlalchemy import Column, String, JSON, DateTime, Enum, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.database import Base

class Job(Base):
    __tablename__ = "jobs"
    
    # We use String for UUID to be compatible with SQLite in dev if needed,
    # or proper UUID for Postgres. Given typical FastAPI setup, we can use String.
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(String, ForeignKey("organizations.id"))
    project_id = Column(Integer, ForeignKey("projects.id"))
    celery_task_id = Column(String, unique=True, index=True)
    job_type = Column(String)  # "generate_project", "generate_pdf", "send_email"
    status = Column(String, default="pending")  # pending/processing/completed/failed
    progress_percentage = Column(Integer, default=0)
    result = Column(JSON, nullable=True)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
