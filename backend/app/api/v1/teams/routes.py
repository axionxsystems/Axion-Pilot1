from __future__ import annotations

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.collaboration import Team, TeamMember, ProjectShare
from app.models.organization import OrgMemberRole
from app.models.project import Project
from app.models.user import User
from app.schemas.organization import AddMemberRequest
from app.schemas.project import (
    TeamCreateRequest,
    TeamResponse,
    TeamProjectResponse,
)

router = APIRouter()


def _require_org_member(user: User, org_id: str) -> None:
    if user.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this organization.",
        )


def _require_team_admin(user: User, team: Team, db: Session) -> None:
    if user.org_id != team.org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to manage this team.",
        )

    if user.org_role == OrgMemberRole.admin or team.created_by == user.id:
        return

    membership = (
        db.query(TeamMember)
        .filter(TeamMember.team_id == team.id, TeamMember.user_id == user.id)
        .first()
    )
    if not membership or membership.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only team admins or organization admins can perform this action.",
        )


@router.post("", status_code=status.HTTP_201_CREATED)
def create_team(
    body: TeamCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_org_member(current_user, current_user.org_id)

    team = Team(
        id=str(uuid.uuid4()),
        org_id=current_user.org_id,
        name=body.name,
        description=body.description,
        created_by=current_user.id,
    )
    db.add(team)
    db.commit()
    db.refresh(team)

    return {
        "team_id": team.id,
        "name": team.name,
        "description": team.description,
    }


@router.get("/{team_id}")
def get_team(
    team_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    team = db.query(Team).filter(Team.id == team_id, Team.org_id == current_user.org_id).first()
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

    members = db.query(TeamMember).filter(TeamMember.team_id == team_id).all()
    return {
        "team_id": team.id,
        "name": team.name,
        "description": team.description,
        "members": [{"user_id": m.user_id, "role": m.role} for m in members],
    }


@router.post("/{team_id}/members", status_code=status.HTTP_201_CREATED)
def add_team_member(
    team_id: str,
    body: AddMemberRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    team = db.query(Team).filter(Team.id == team_id, Team.org_id == current_user.org_id).first()
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

    _require_team_admin(current_user, team, db)

    user = db.query(User).filter(User.email == body.email, User.org_id == current_user.org_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    existing = (
        db.query(TeamMember)
        .filter(TeamMember.team_id == team.id, TeamMember.user_id == user.id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already a member of this team.",
        )

    member = TeamMember(
        id=str(uuid.uuid4()),
        team_id=team.id,
        user_id=user.id,
        role=body.role,
    )
    db.add(member)
    db.commit()
    db.refresh(member)

    return {"user_id": user.id, "role": member.role}


@router.get("/{team_id}/projects", response_model=List[TeamProjectResponse])
def list_team_projects(
    team_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    team = db.query(Team).filter(Team.id == team_id, Team.org_id == current_user.org_id).first()
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

    _require_org_member(current_user, current_user.org_id)

    shares = db.query(ProjectShare).filter(ProjectShare.team_id == team_id).all()
    project_ids = [s.project_id for s in shares]
    if not project_ids:
        return []

    projects = (
        db.query(Project)
        .filter(Project.id.in_(project_ids), Project.org_id == current_user.org_id)
        .all()
    )

    share_map = {s.project_id: s.access_level for s in shares}
    return [
        {
            "id": project.id,
            "title": project.title,
            "access": share_map.get(project.id),
        }
        for project in projects
    ]
