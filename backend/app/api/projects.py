from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.auth.dependencies import get_current_user
from app.schemas.project import ProjectRequest, ProjectResponse
from app.core.generators.project_gen import generate_project
from app.core.generators.report_gen import generate_report
from app.core.generators.ppt_gen import generate_ppt
from app.core.generators.code_gen import generate_code_zip
import io

router = APIRouter()

@router.post("/generate", response_model=ProjectResponse)
async def create_project(request: ProjectRequest, current_user: User = Depends(get_current_user)):
    try:
        project_data = generate_project(
            api_key=request.api_key,
            domain=request.domain,
            topic=request.topic,
            difficulty=request.difficulty,
            tech_stack=request.tech_stack,
            level=request.year
        )
        return project_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/download/report")
async def download_report(project_data: dict):
    try:
        buffer = generate_report(project_data)
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": "attachment; filename=project_report.docx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/download/ppt")
async def download_ppt(project_data: dict):
    try:
        buffer = generate_ppt(project_data)
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers={"Content-Disposition": "attachment; filename=project_presentation.pptx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/download/code")
async def download_code(project_data: dict):
    try:
        buffer = generate_code_zip(project_data)
        return StreamingResponse(
            buffer,
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=project_code.zip"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
