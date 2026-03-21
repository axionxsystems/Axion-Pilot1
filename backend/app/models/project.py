from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
from datetime import datetime
from app.database import Base
from sqlalchemy.orm import relationship

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    domain = Column(String)
    difficulty = Column(String)
    tech_stack = Column(String)
    data = Column(JSON) # Stores the full project_data dictionary
    status = Column(String, default="active") # active, flagged, low_quality, deleted
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="projects")
