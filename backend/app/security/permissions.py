from enum import Enum
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.project import Project
from app.models.collaboration import ProjectShare, TeamMember


class AccessLevel(str, Enum):
    READ = "read"
    EDIT = "edit"
    ADMIN = "admin"


async def can_read_project(user_id: int, project_id: int, org_id: str, db: Session) -> bool:
    project = db.query(Project).filter(Project.id == project_id, Project.org_id == org_id).first()
    if not project:
        return False

    if project.user_id == user_id:
        return True

    share = (
        db.query(ProjectShare)
        .join(TeamMember, ProjectShare.team_id == TeamMember.team_id)
        .filter(
            ProjectShare.project_id == project_id,
            TeamMember.user_id == user_id,
            ProjectShare.access_level.in_([
                AccessLevel.READ.value,
                AccessLevel.EDIT.value,
                AccessLevel.ADMIN.value,
            ]),
        )
        .first()
    )

    return share is not None


async def can_edit_project(user_id: int, project_id: int, org_id: str, db: Session) -> bool:
    project = db.query(Project).filter(Project.id == project_id, Project.org_id == org_id).first()
    if not project:
        return False

    if project.user_id == user_id:
        return True

    share = (
        db.query(ProjectShare)
        .join(TeamMember, ProjectShare.team_id == TeamMember.team_id)
        .filter(
            ProjectShare.project_id == project_id,
            TeamMember.user_id == user_id,
            ProjectShare.access_level.in_([
                AccessLevel.EDIT.value,
                AccessLevel.ADMIN.value,
            ]),
        )
        .first()
    )

    return share is not None
