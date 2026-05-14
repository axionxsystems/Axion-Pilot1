from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, UniqueConstraint
from datetime import datetime
from app.database import Base
from sqlalchemy.orm import relationship

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    # ── Multi-tenancy: every project MUST belong to an org ────────────────────
    org_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"),
                    nullable=True, index=True)

    title = Column(String)
    domain = Column(String)
    difficulty = Column(String)
    tech_stack = Column(String)
    description = Column(String, nullable=True)
    data = Column(JSON, nullable=True) # Full generation details json
    status = Column(String, default="active") # active, completed, pending, flagged, deleted
    progress = Column(Integer, default=0) # 0-100
    deadline = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Unique project title per org (allows same title across different orgs)
    __table_args__ = (
        UniqueConstraint("org_id", "title", name="uq_org_project_title"),
    )

    # Relationships
    owner        = relationship("User",         back_populates="projects")
    organization = relationship("Organization", back_populates="projects",
                                foreign_keys=[org_id])
    contents     = relationship("ProjectContent", back_populates="project", cascade="all, delete-orphan")


class ProjectContent(Base):
    __tablename__ = "project_contents"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"))
    type = Column(String) # idea, architecture, modules, code, report, presentation, viva
    content = Column(JSON) # JSON content or text
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="contents")
