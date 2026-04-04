from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
from datetime import datetime
from app.database import Base
from sqlalchemy.orm import relationship

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    topic = Column(String)
    tech_stack = Column(String)
    complexity = Column(String)
    status = Column(String, default="active") # active, flagged, low_quality, deleted
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="projects")
    contents = relationship("ProjectContent", back_populates="project", cascade="all, delete-orphan")

class ProjectContent(Base):
    __tablename__ = "project_contents"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"))
    type = Column(String) # idea, architecture, modules, code, report, presentation, viva
    content = Column(JSON) # JSON content or text
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="contents")
