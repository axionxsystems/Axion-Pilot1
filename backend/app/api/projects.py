from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.activity import Activity
from app.models.user import User
from app.models.project import Project
from app.auth.dependencies import get_current_user
from sqlalchemy import func
from app.schemas.project import ProjectRequest, ProjectResponse
from app.core.generators.project_gen import generate_project
from app.core.generators.report_gen import generate_report
from app.core.generators.ppt_gen import generate_ppt
from app.core.generators.code_gen import generate_code_zip, generate_full_zip
from app.models.settings import PlatformSettings, ProjectTemplate
import io
from typing import List

router = APIRouter()

@router.post("/generate", response_model=ProjectResponse)
def create_project(request: ProjectRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        # Fetch AI Config from admin settings
        ai_config = db.query(PlatformSettings).filter(PlatformSettings.setting_key == "AI_CONFIG").first()
        config_data = ai_config.setting_value if ai_config else None
        
        project_data = generate_project(
            api_key=request.api_key,
            domain=request.domain,
            topic=request.topic,
            description=request.description,
            difficulty=request.difficulty,
            tech_stack=request.tech_stack,
            level=request.year,
            ai_config=config_data # Pass the config
        )
        
        # Save to database
        db_project = Project(
            user_id=current_user.id,
            title=project_data.get("title", "Untitled Project"),
            domain=project_data.get("domain", request.domain),
            difficulty=project_data.get("difficulty", request.difficulty),
            tech_stack=request.tech_stack,
            data=project_data
        )
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        
        # Add the DB ID to the response
        project_data["id"] = db_project.id
        project_data["created_at"] = db_project.created_at.isoformat()
        
        # Log Activity
        log = Activity(
            user_id=current_user.id, 
            action_type="PROJECT_GEN", 
            description=f"Project generated: {db_project.title}",
            extra_data={"domain": db_project.domain, "difficulty": db_project.difficulty}
        )
        db.add(log)
        db.commit()
        
        return project_data
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list", response_model=List[dict])
async def get_projects(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        # Exclude projects marked as deleted
        projects = db.query(Project).filter(
            Project.user_id == current_user.id,
            Project.status != "deleted"
        ).order_by(Project.created_at.desc()).all()
        
        result = []
        for p in projects:
            p_data = p.data if isinstance(p.data, dict) else {}
            p_data["id"] = p.id
            p_data["created_at"] = p.created_at.isoformat()
            p_data["domain"] = p.domain
            p_data["difficulty"] = p.difficulty
            p_data["tech_stack"] = p.tech_stack
            p_data["status"] = p.status # Let UI know if it's flagged/low quality
            result.append(p_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{project_id}")
async def delete_project(project_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        db.delete(project)
        db.commit()
        return {"message": "Project deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/download/report")
async def download_report(project_data: dict, db: Session = Depends(get_db)):
    try:
        buffer = generate_report(project_data)
        
        # Log Activity
        log = Activity(
            action_type="REPORT_GEN", 
            description=f"Report downloaded for project: {project_data.get('title')}"
        )
        db.add(log)
        db.commit()
        
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": "attachment; filename=project_report.docx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/download/ppt")
async def download_ppt(project_data: dict, db: Session = Depends(get_db)):
    try:
        buffer = generate_ppt(project_data)
        
        # Log Activity
        log = Activity(
            action_type="PPT_GEN", 
            description=f"Presentation downloaded for project: {project_data.get('title')}"
        )
        db.add(log)
        db.commit()
        
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers={"Content-Disposition": "attachment; filename=project_presentation.pptx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/download/code")
async def download_code(project_data: dict, db: Session = Depends(get_db)):
    try:
        buffer = generate_code_zip(project_data)
        
        # Log Activity
        log = Activity(
            action_type="CODE_GEN", 
            description=f"Code bundle downloaded for project: {project_data.get('title')}"
        )
        db.add(log)
        db.commit()
        
        return StreamingResponse(
            buffer,
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=project_code.zip"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/download/full")
async def download_full_project(project_data: dict, db: Session = Depends(get_db)):
    try:
        buffer = generate_full_zip(project_data)
        
        # Log Activity
        log = Activity(
            action_type="CODE_GEN", 
            description=f"Full project package exported: {project_data.get('title')}"
        )
        db.add(log)
        db.commit()
        
        return StreamingResponse(
            buffer,
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=full_project_suite.zip"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates")
async def get_public_templates(db: Session = Depends(get_db)):
    try:
        # Only show active templates to users
        return db.query(ProjectTemplate).filter(ProjectTemplate.is_active == True).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_user_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        # Count projects
        project_count = db.query(Project).filter(Project.user_id == current_user.id).count()
        
        # Count activities by type for the user
        report_count = db.query(Activity).filter(
            Activity.user_id == current_user.id,
            Activity.action_type == "REPORT_GEN"
        ).count()
        
        ppt_count = db.query(Activity).filter(
            Activity.user_id == current_user.id,
            Activity.action_type == "PPT_GEN"
        ).count()
        
        # Viva questions (summed from projects or just count projects with a field? 
        # For now let's just count total viva questions across all user's projects)
        projects = db.query(Project).filter(Project.user_id == current_user.id).all()
        viva_count = sum(len(p.data.get("viva_questions", [])) for p in projects if isinstance(p.data, dict))

        return {
            "projects_generated": project_count,
            "reports_created": report_count,
            "presentations_created": ppt_count,
            "viva_questions": viva_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{project_id}")
async def get_project_by_id(project_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == current_user.id,
            Project.status != "deleted"
        ).first()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
            
        p_data = project.data if isinstance(project.data, dict) else {}
        p_data["id"] = project.id
        p_data["created_at"] = project.created_at.isoformat()
        p_data["domain"] = project.domain
        p_data["difficulty"] = project.difficulty
        p_data["tech_stack"] = project.tech_stack
        p_data["status"] = project.status
        
        return p_data
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{project_id}")
async def update_project(project_id: int, updates: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == current_user.id,
            Project.status != "deleted"
        ).first()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Merge updates into existing data
        existing = project.data if isinstance(project.data, dict) else {}
        
        # Allow updating specific top-level fields
        for key in ["title", "abstract", "problem_statement", "methodology", "literature_survey",
                     "architecture_description", "database_design", "features", "security_measures",
                     "logic_flow", "files", "viva_questions"]:
            if key in updates:
                existing[key] = updates[key]
        
        # Update model-level fields if provided
        if "title" in updates:
            project.title = updates["title"]
        if "domain" in updates:
            project.domain = updates["domain"]
        if "difficulty" in updates:
            project.difficulty = updates["difficulty"]
        if "tech_stack" in updates:
            project.tech_stack = updates["tech_stack"]
            
        project.data = existing
        db.commit()
        
        return {"message": "Project updated successfully"}
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=str(e))
