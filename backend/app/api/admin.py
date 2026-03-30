from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.user import User
from app.models.project import Project
from app.models.activity import Activity
from app.models.settings import PlatformSettings, ProjectTemplate
from app.auth.dependencies import get_current_user
from datetime import datetime, timedelta
from typing import List, Dict

router = APIRouter()

def check_admin(user: User):
    is_super_admin = user.email.lower() == "niyant214@gmail.com"
    if not (is_super_admin or user.is_admin):
        raise HTTPException(status_code=403, detail="Strict Access Denied. Admin privilege only.")

@router.get("/stats")
async def get_platform_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    check_admin(current_user)
    
    total_users = db.query(User).count()
    total_projects = db.query(Project).count()
    
    # Count generated assets from activity logs
    total_reports = db.query(Activity).filter(Activity.action_type == "REPORT_GEN").count()
    total_presentations = db.query(Activity).filter(Activity.action_type == "PPT_GEN").count()
    
    return {
        "total_users": total_users,
        "total_projects": total_projects,
        "total_reports": total_reports,
        "total_presentations": total_presentations
    }

@router.get("/activity", response_model=Dict)
async def get_recent_activity(
    page: int = 1, 
    size: int = 50, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    check_admin(current_user)
    
    # Calculate offset
    skip = (page - 1) * size
    
    total = db.query(Activity).count()
    
    # Get actions with user details
    logs = db.query(Activity, User.email)\
        .outerjoin(User, Activity.user_id == User.id)\
        .order_by(Activity.created_at.desc())\
        .offset(skip).limit(size).all()
    
    result = []
    for log, email in logs:
        result.append({
            "id": log.id,
            "action_type": log.action_type,
            "description": log.description,
            "user_email": email or "System",
            "created_at": log.created_at.isoformat() if log.created_at else datetime.utcnow().isoformat()
        })
        
    return {
        "items": result,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }

@router.get("/charts/projects-per-day")
async def get_projects_per_day(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    check_admin(current_user)
    
    # Group projects by date for the last 14 days
    fourteen_days_ago = datetime.utcnow() - timedelta(days=14)
    
    stats = db.query(
        func.date(Project.created_at).label('date'),
        func.count(Project.id).label('count')
    ).filter(Project.created_at >= fourteen_days_ago).group_by(func.date(Project.created_at)).all()
    
    return [{"date": str(s.date), "count": s.count} for s in stats]

@router.get("/charts/projects-per-domain")
async def get_projects_per_domain(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    check_admin(current_user)
    
    domain_stats = db.query(
        Project.domain,
        func.count(Project.id).label('count')
    ).group_by(Project.domain).all()
    
    return [{"domain": s.domain, "count": s.count} for s in domain_stats]

@router.get("/charts/projects-per-difficulty")
async def get_projects_per_difficulty(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    check_admin(current_user)
    
    diff_stats = db.query(
        Project.difficulty,
        func.count(Project.id).label('count')
    ).group_by(Project.difficulty).all()
    
    return [{"difficulty": s.difficulty, "count": s.count} for s in diff_stats]

# --- NEW USER MANAGEMENT ENDPOINTS ---

@router.get("/users", response_model=List[Dict])
async def list_users(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    check_admin(current_user)
    
    # Get all users with project counts
    users = db.query(
        User,
        func.count(Project.id).label("project_count")
    ).outerjoin(Project, User.id == Project.user_id).group_by(User.id).all()
    
    return [{
        "id": u.User.id,
        "email": u.User.email,
        "is_active": u.User.is_active,
        "plan": u.User.plan,
        "created_at": u.User.created_at.isoformat(),
        "project_count": u.project_count,
        "name": getattr(u.User, "name", None)
    } for u in users]

@router.post("/users/{user_id}/toggle-status")
async def toggle_user_status(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    check_admin(current_user)
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.email == "niyant214@gmail.com":
        raise HTTPException(status_code=400, detail="Cannot suspend the super-admin")
        
    user.is_active = not user.is_active
    db.commit()
    return {"message": f"User status updated to {'active' if user.is_active else 'suspended'}"}

@router.delete("/users/{user_id}")
async def delete_user(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    check_admin(current_user)
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.email == "niyant214@gmail.com":
        raise HTTPException(status_code=400, detail="Cannot delete the super-admin")

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

# --- NEW PROJECT MONITORING ENDPOINTS ---

@router.get("/projects", response_model=List[Dict])
async def list_all_projects(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    check_admin(current_user)
    
    # Join with User to show owner email
    projects = db.query(
        Project,
        User.email.label("user_email")
    ).join(User, Project.user_id == User.id).order_by(Project.created_at.desc()).all()
    
    return [{
        "id": p.Project.id,
        "title": p.Project.title,
        "domain": p.Project.domain,
        "difficulty": p.Project.difficulty,
        "tech_stack": p.Project.tech_stack,
        "user_email": p.user_email,
        "created_at": p.Project.created_at.isoformat(),
        "data": p.Project.data
    } for p in projects]

@router.delete("/projects/{project_id}")
async def admin_delete_project(project_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    check_admin(current_user)
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully"}

# --- AI SETTINGS ENDPOINTS ---

@router.get("/settings/ai")
async def get_ai_settings(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    check_admin(current_user)
    settings = db.query(PlatformSettings).filter(PlatformSettings.setting_key == "AI_CONFIG").first()
    if not settings:
        # Default settings if none exist
        return {
            "model": "gemini-1.5-flash",
            "temperature": 0.7,
            "max_tokens": 4096,
            "complexity_level": "standard",
            "features": {
                "advanced_mode": True,
                "deep_code": True,
                "extended_docs": True,
                "arch_planning": True
            }
        }
    return settings.setting_value

@router.post("/settings/ai")
async def update_ai_settings(config: Dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    check_admin(current_user)
    settings = db.query(PlatformSettings).filter(PlatformSettings.setting_key == "AI_CONFIG").first()
    if not settings:
        settings = PlatformSettings(setting_key="AI_CONFIG", setting_value=config)
        db.add(settings)
    else:
        settings.setting_value = config
    db.commit()
    return {"message": "AI configuration updated successfully"}

# --- TEMPLATE MANAGEMENT ENDPOINTS ---

@router.get("/templates")
async def list_templates(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    check_admin(current_user)
    return db.query(ProjectTemplate).all()

@router.post("/templates")
async def create_template(template_data: Dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    check_admin(current_user)
    new_template = ProjectTemplate(
        name=template_data.get("name"),
        domain=template_data.get("domain"),
        difficulty=template_data.get("difficulty"),
        tech_stack=template_data.get("tech_stack"),
        description=template_data.get("description")
    )
    db.add(new_template)
    db.commit()
    db.refresh(new_template)
    return new_template

@router.delete("/templates/{template_id}")
async def delete_template(template_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    check_admin(current_user)
    template = db.query(ProjectTemplate).filter(ProjectTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    db.delete(template)
    db.commit()
    return {"message": "Template deleted successfully"}

# --- MODERATION SYSTEM ENDPOINTS ---

@router.get("/moderation/projects")
async def get_moderation_projects(status: str = "active", current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    check_admin(current_user)
    projects = db.query(
        Project,
        User.email.label("user_email")
    ).join(User, Project.user_id == User.id).filter(Project.status == status).order_by(Project.created_at.desc()).all()
    
    return [{
        "id": p.Project.id,
        "title": p.Project.title,
        "user_email": p.user_email,
        "domain": p.Project.domain,
        "difficulty": p.Project.difficulty,
        "status": p.Project.status,
        "created_at": p.Project.created_at.isoformat()
    } for p in projects]

@router.post("/moderation/projects/{project_id}/status")
async def update_project_status(project_id: int, status_data: Dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    check_admin(current_user)
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    new_status = status_data.get("status")
    if new_status not in ["active", "flagged", "low_quality", "approved"]:
        raise HTTPException(status_code=400, detail="Invalid status")
        
    project.status = new_status
    db.commit()
    return {"message": f"Project status updated to {new_status}"}
