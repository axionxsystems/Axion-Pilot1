"""
Pydantic schemas for Organization, Subscription, AuditLog, and related request/response bodies.
"""
from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


# ── Helpers ───────────────────────────────────────────────────────────────────

_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9\-]{1,78}[a-z0-9]$")


def _validate_slug(v: str) -> str:
    if not _SLUG_RE.match(v):
        raise ValueError(
            "Slug must be 3-80 chars, lowercase alphanumeric or hyphens, "
            "and must not start/end with a hyphen."
        )
    return v


# ── Organization ──────────────────────────────────────────────────────────────

class OrganizationCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    slug: str = Field(..., min_length=3, max_length=80)

    @field_validator("slug")
    @classmethod
    def slug_format(cls, v: str) -> str:
        return _validate_slug(v.lower())


class OrganizationUpdate(BaseModel):
    """Fields the org admin can change via PATCH /organizations/{org_id}/settings."""
    name:      Optional[str] = Field(None, min_length=2, max_length=120)
    api_quota: Optional[int] = Field(None, ge=0, le=1_000_000)
    meta:      Optional[Dict[str, Any]] = None


class OrganizationResponse(BaseModel):
    id:         str
    name:       str
    slug:       str
    tier:       str
    api_quota:  int
    created_at: datetime
    meta:       Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


# ── Member management ─────────────────────────────────────────────────────────

class AddMemberRequest(BaseModel):
    """Body for POST /organizations/{org_id}/members."""
    email: str
    role:  str = Field("member", pattern="^(admin|member|viewer)$")


class MemberResponse(BaseModel):
    id:       int
    name:     Optional[str]
    email:    str
    org_role: Optional[str]

    class Config:
        from_attributes = True


# ── Subscription ──────────────────────────────────────────────────────────────

class SubscriptionResponse(BaseModel):
    id:                     str
    org_id:                 str
    stripe_subscription_id: Optional[str]
    tier:                   str
    status:                 str
    next_billing_date:      Optional[datetime]
    usage_json:             Optional[Dict[str, Any]]
    created_at:             datetime

    class Config:
        from_attributes = True


# ── AuditLog ──────────────────────────────────────────────────────────────────

class AuditLogResponse(BaseModel):
    id:            str
    org_id:        str
    actor_id:      Optional[int]
    action:        str
    resource_type: Optional[str]
    resource_id:   Optional[str]
    changes:       Optional[Dict[str, Any]]
    timestamp:     datetime

    class Config:
        from_attributes = True


# ── Project (org-scoped list) ─────────────────────────────────────────────────

class OrgProjectResponse(BaseModel):
    id:         int
    title:      str
    domain:     str
    difficulty: str
    tech_stack: str
    status:     str
    created_at: datetime

    class Config:
        from_attributes = True
