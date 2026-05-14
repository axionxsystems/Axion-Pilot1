from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.auth.dual_auth_dependency import get_auth_context, AuthContext
from app.models.user import User
from app.security.scopes import check_scopes
from app.services.project_service import ProjectService
from app.schemas.project import ProjectGenerateRequest, ProjectFullResponse, ProjectGenerationResponse
from app.cache import get_rate_limiter

router = APIRouter()


# ─────────────────────────────────────────────────────────────────────────────
# Helper: Get org_id and user_id from auth context
# ─────────────────────────────────────────────────────────────────────────────

def extract_auth_info(auth: AuthContext) -> tuple[str, Optional[int]]:
    """Extract org_id and optional user_id from auth context."""
    return auth.org_id, auth.user_id


# ─────────────────────────────────────────────────────────────────────────────
# GET /projects — List projects (supports both JWT and API key)
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/", response_model=List[ProjectFullResponse])
async def list_projects(
    auth: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
    request: Request = None,
):
    """
    List all projects for the authenticated user/org.
    
    Supports both JWT and API key authentication.
    - JWT: Returns projects scoped by user and org
    - API Key: Returns projects scoped by org (with read:projects scope required)
    
    Includes rate limit headers for API key auth.
    """
    # Validate scope if API key
    if auth.is_api_key:
        if not check_scopes(auth.scopes, "read:projects"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions. Required scope: read:projects",
            )
    
    # Get projects
    org_id, user_id = extract_auth_info(auth)
    
    # If API key (no user_id), get all org projects; if JWT, get user's projects
    if user_id:
        projects = ProjectService.list_projects(db, user_id, org_id)
    else:
        # For API keys: list all org projects
        from app.models.project import Project
        projects = db.query(Project).filter(Project.org_id == org_id).all()
    
    # Add rate limit info if API key
    if request and auth.is_api_key:
        limiter = get_rate_limiter()
        rate_limit_rpm = getattr(request.state, "rate_limit_rpm", 1000)
        _, remaining, reset_at = limiter.check_rate_limit(auth.api_key_id, rate_limit_rpm)
        request.state.rate_limit_remaining = remaining
        request.state.rate_limit_reset = reset_at
    
    return projects


# ─────────────────────────────────────────────────────────────────────────────
# POST /projects/generate — Create project (supports both JWT and API key)
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/", response_model=ProjectGenerationResponse, status_code=status.HTTP_201_CREATED)
async def generate_project(
    payload: ProjectGenerateRequest,
    auth: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
):
    """
    Generate a new project using AI.
    
    Supports both JWT and API key authentication.
    Requires: write:projects scope (for API keys)
    """
    # Validate scope if API key
    if auth.is_api_key:
        if not check_scopes(auth.scopes, "write:projects"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions. Required scope: write:projects",
            )
    
    # Get org_id and user_id
    org_id, user_id = extract_auth_info(auth)
    
    # For API keys without user_id, use a placeholder or org-level user
    if user_id is None:
        # Use org admin or first org user (can be enhanced later)
        from app.models.user import User
        org_user = db.query(User).filter(User.org_id == org_id).first()
        if not org_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization has no users",
            )
        user_id = org_user.id
    
    db_project = ProjectService.create_project_skeleton(db, user_id, org_id, payload)
    db_contents = ProjectService.run_ai_pipeline(db, db_project)
    return {
        "project": db_project,
        "contents": db_contents
    }


# ─────────────────────────────────────────────────────────────────────────────
# GET /projects/stats — Get usage stats (requires JWT for now)
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/stats")
def get_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get usage statistics for the authenticated user, scoped by org."""
    return ProjectService.get_user_stats(db, current_user.id, current_user.org_id)


# ─────────────────────────────────────────────────────────────────────────────
# GET /projects/{project_id} — Get project details
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/{project_id}")
async def get_project(
    project_id: int,
    auth: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db)
):
    """
    Get full details of a specific project.
    
    Supports both JWT and API key authentication.
    Requires: read:projects scope (for API keys)
    """
    # Validate scope if API key
    if auth.is_api_key:
        if not check_scopes(auth.scopes, "read:projects"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions. Required scope: read:projects",
            )
    
    org_id, user_id = extract_auth_info(auth)
    
    # Get project with org verification
    from app.models.project import Project
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.org_id == org_id,
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return project


# ─────────────────────────────────────────────────────────────────────────────
# DELETE /projects/{project_id} — Delete project
# ─────────────────────────────────────────────────────────────────────────────

@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    auth: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db)
):
    """
    Delete a project.
    
    Supports both JWT and API key authentication.
    Requires: delete:projects scope (for API keys)
    """
    # Validate scope if API key
    if auth.is_api_key:
        if not check_scopes(auth.scopes, "delete:projects"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions. Required scope: delete:projects",
            )
    
    org_id, user_id = extract_auth_info(auth)
    
    # Delete project with org verification
    from app.models.project import Project
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.org_id == org_id,
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(project)
    db.commit()
    
    return {"message": "Project deleted successfully"}
