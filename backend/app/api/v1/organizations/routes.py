"""
Organization API Routes
=======================
All endpoints are under /api/v1/organizations (registered in api/v1/__init__.py).

Security model
--------------
*  Every mutating endpoint checks that the authenticated user belongs to the
   target org AND has the required role (admin / member / viewer).
*  All DB queries that touch multi-tenant tables include ``.filter(Model.org_id == org_id)``
   so cross-org data leakage is structurally impossible even if a bug slips an
   incorrect org_id into a URL parameter.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.middleware.tenant import get_current_org_id_optional
from app.models.organization import AuditLog, Organization, OrgMemberRole, Subscription
from app.models.project import Project
from app.models.user import User
from app.schemas.organization import (
    AddMemberRequest,
    MemberResponse,
    OrgProjectResponse,
    OrganizationCreate,
    OrganizationResponse,
    OrganizationUpdate,
)

logger = logging.getLogger(__name__)
router = APIRouter()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_org_or_404(db: Session, org_id: str) -> Organization:
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Organization not found.")
    return org


def _require_org_member(user: User, org_id: str) -> None:
    """Raise 403 if user does not belong to org_id."""
    if user.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this organization.",
        )


def _require_org_admin(user: User, org_id: str) -> None:
    """Raise 403 if user is not an admin of org_id."""
    _require_org_member(user, org_id)
    if user.org_role != OrgMemberRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required for this action.",
        )


def _write_audit(
    db: Session,
    *,
    org_id: str,
    actor_id: int,
    action: str,
    resource_type: str | None = None,
    resource_id: str | None = None,
    changes: dict | None = None,
) -> None:
    """Insert one AuditLog row (call before db.commit())."""
    db.add(
        AuditLog(
            id=str(uuid.uuid4()),
            org_id=org_id,
            actor_id=actor_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            changes=changes,
            timestamp=datetime.utcnow(),
        )
    )


# ── POST /organizations ────────────────────────────────────────────────────────

@router.post("", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
def create_organization(
    body: OrganizationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new organization. The calling user becomes its first **admin**.

    Rules
    -----
    * A user can only belong to one org at a time (org_id is a single FK).
    * Slug must be globally unique.

    Example request
    ---------------
    ```json
    POST /api/v1/organizations
    Authorization: Bearer <jwt>

    { "name": "Acme Corp", "slug": "acme-corp" }
    ```

    Example response (201)
    ----------------------
    ```json
    {
      "id": "550e8400-...",
      "name": "Acme Corp",
      "slug": "acme-corp",
      "tier": "free",
      "api_quota": 100,
      "created_at": "2026-05-12T00:00:00",
      "meta": {}
    }
    ```
    """
    # Slug uniqueness
    existing = db.query(Organization).filter(Organization.slug == body.slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Slug '{body.slug}' is already taken.",
        )

    org = Organization(
        id=str(uuid.uuid4()),
        name=body.name,
        slug=body.slug,
        tier="free",
        api_quota=100,
        created_at=datetime.utcnow(),
        meta={},
    )
    db.add(org)
    db.flush()  # get org.id before committing

    # Promote the creating user to org admin
    current_user.org_id   = org.id
    current_user.org_role = OrgMemberRole.admin

    # Bootstrap a free subscription
    sub = Subscription(
        id=str(uuid.uuid4()),
        org_id=org.id,
        tier="free",
        status="active",
    )
    db.add(sub)

    _write_audit(
        db,
        org_id=org.id,
        actor_id=current_user.id,
        action="organization.create",
        resource_type="organization",
        resource_id=org.id,
        changes={"name": org.name, "slug": org.slug},
    )

    db.commit()
    db.refresh(org)
    logger.info("[Org] Created org=%s by user=%s", org.id, current_user.id)
    return org


# ── GET /organizations/{org_id} ────────────────────────────────────────────────

@router.get("/{org_id}", response_model=OrganizationResponse)
def get_organization(
    org_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Fetch full organization details.

    Any member of the org can call this.

    Example response (200)
    ----------------------
    ```json
    {
      "id": "550e8400-...",
      "name": "Acme Corp",
      "slug": "acme-corp",
      "tier": "pro",
      "api_quota": 5000,
      "created_at": "2026-05-12T00:00:00",
      "meta": {"brand_color": "#4A90D9"}
    }
    ```
    """
    _require_org_member(current_user, org_id)
    return _get_org_or_404(db, org_id)


# ── POST /organizations/{org_id}/members ──────────────────────────────────────

@router.post("/{org_id}/members", response_model=MemberResponse,
             status_code=status.HTTP_201_CREATED)
def add_member(
    org_id: str,
    body: AddMemberRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Add a registered user to the organization with a specific role.

    Requires **admin** role.

    Example request
    ---------------
    ```json
    POST /api/v1/organizations/550e8400-.../members
    Authorization: Bearer <admin-jwt>

    { "email": "alice@example.com", "role": "member" }
    ```

    Example response (201)
    ----------------------
    ```json
    {
      "id": 7,
      "name": "Alice",
      "email": "alice@example.com",
      "org_role": "member"
    }
    ```
    """
    _require_org_admin(current_user, org_id)
    org = _get_org_or_404(db, org_id)

    target = db.query(User).filter(User.email == body.email.strip().lower()).first()
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No user found with that email address.",
        )

    if target.org_id and target.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already belongs to a different organization.",
        )

    target.org_id   = org_id
    target.org_role = OrgMemberRole(body.role)

    _write_audit(
        db,
        org_id=org_id,
        actor_id=current_user.id,
        action="member.add",
        resource_type="user",
        resource_id=str(target.id),
        changes={"role": body.role},
    )

    db.commit()
    db.refresh(target)
    logger.info("[Org] Added user=%s to org=%s as %s", target.id, org_id, body.role)
    return target


# ── GET /organizations/{org_id}/projects ──────────────────────────────────────

@router.get("/{org_id}/projects", response_model=List[OrgProjectResponse])
def list_org_projects(
    org_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List all non-deleted projects that belong to this organization.

    **Security**: query unconditionally filters by `org_id` — even if the URL
    parameter is tampered, the user membership check runs first.

    Example response (200)
    ----------------------
    ```json
    [
      {
        "id": 1,
        "title": "Smart Parking System",
        "domain": "IoT",
        "difficulty": "intermediate",
        "tech_stack": "Python, MQTT",
        "status": "active",
        "created_at": "2026-05-12T00:00:00"
      }
    ]
    ```
    """
    _require_org_member(current_user, org_id)

    # [Security] Always filter by the org_id so cross-org leakage is impossible
    projects = (
        db.query(Project)
        .filter(
            Project.org_id == org_id,      # ← tenant isolation
            Project.status != "deleted",
        )
        .order_by(Project.created_at.desc())
        .all()
    )
    return projects


# ── PATCH /organizations/{org_id}/settings ────────────────────────────────────

@router.patch("/{org_id}/settings", response_model=OrganizationResponse)
def update_org_settings(
    org_id: str,
    body: OrganizationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update organization settings (name, api_quota, metadata).

    Requires **admin** role.

    Example request
    ---------------
    ```json
    PATCH /api/v1/organizations/550e8400-.../settings
    Authorization: Bearer <admin-jwt>

    {
      "name": "Acme Corp (Rebranded)",
      "api_quota": 2000,
      "meta": {"brand_color": "#FF6600"}
    }
    ```

    Example response (200)
    ----------------------
    ```json
    {
      "id": "550e8400-...",
      "name": "Acme Corp (Rebranded)",
      "slug": "acme-corp",
      "tier": "free",
      "api_quota": 2000,
      "created_at": "2026-05-12T00:00:00",
      "meta": {"brand_color": "#FF6600"}
    }
    ```
    """
    _require_org_admin(current_user, org_id)
    org = _get_org_or_404(db, org_id)

    changes: dict = {}
    if body.name is not None:
        changes["name"] = {"before": org.name, "after": body.name}
        org.name = body.name
    if body.api_quota is not None:
        changes["api_quota"] = {"before": org.api_quota, "after": body.api_quota}
        org.api_quota = body.api_quota
    if body.meta is not None:
        # Merge meta — never silently discard existing keys
        existing_meta = org.meta or {}
        merged = {**existing_meta, **body.meta}
        changes["meta"] = {"before": existing_meta, "after": merged}
        org.meta = merged

    if changes:
        _write_audit(
            db,
            org_id=org_id,
            actor_id=current_user.id,
            action="organization.update",
            resource_type="organization",
            resource_id=org_id,
            changes=changes,
        )
        db.commit()
        db.refresh(org)

    return org
