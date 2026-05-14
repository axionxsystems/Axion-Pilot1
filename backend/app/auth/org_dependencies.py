"""
Org-scoped FastAPI dependencies
================================
Drop-in replacements for get_current_user that additionally enforce
that the caller belongs to a specific org and has the required role.

Usage example
-------------
    from app.auth.org_dependencies import require_org_member, require_org_admin

    @router.get("/{org_id}/something")
    def my_endpoint(
        org_id: str,
        ctx: tuple = Depends(require_org_member),   # (user, org)
        db: Session = Depends(get_db),
    ):
        user, org = ctx
        projects = db.query(Project).filter(
            Project.org_id == org.id   # ← always filter by org
        ).all()
        ...
"""

from __future__ import annotations

from typing import Tuple

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.organization import Organization, OrgMemberRole
from app.models.user import User


def _get_org_or_404(db: Session, org_id: str) -> Organization:
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found.",
        )
    return org


def _assert_member(user: User, org_id: str) -> None:
    if user.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this organization.",
        )


def _assert_admin(user: User, org_id: str) -> None:
    _assert_member(user, org_id)
    if user.org_role != OrgMemberRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required.",
        )


def _assert_not_viewer(user: User, org_id: str) -> None:
    _assert_member(user, org_id)
    if user.org_role == OrgMemberRole.viewer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Viewers cannot perform this action.",
        )


# ── Dependency factories ───────────────────────────────────────────────────────

def require_org_member(
    org_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Tuple[User, Organization]:
    """
    Verify that the calling user is a member (any role) of `org_id`.
    Returns (user, org) so routes can use both without extra DB queries.
    """
    _assert_member(current_user, org_id)
    org = _get_org_or_404(db, org_id)
    return current_user, org


def require_org_writer(
    org_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Tuple[User, Organization]:
    """Member or Admin (not viewer). Use for create/update/delete actions."""
    _assert_not_viewer(current_user, org_id)
    org = _get_org_or_404(db, org_id)
    return current_user, org


def require_org_admin(
    org_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Tuple[User, Organization]:
    """Admin role only. Use for settings, member management, billing."""
    _assert_admin(current_user, org_id)
    org = _get_org_or_404(db, org_id)
    return current_user, org
