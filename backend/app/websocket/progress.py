from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.celery import app as celery_app
from app.database import SessionLocal
from app.models.job import Job
import asyncio

router = APIRouter()

@router.websocket("/ws/projects/{project_id}/progress")
async def websocket_progress(websocket: WebSocket, project_id: str):
    await websocket.accept()
    db = SessionLocal()
    try:
        while True:
            job = db.query(Job).filter(Job.project_id == project_id).first()
            if job:
                steps = ["initializing", "generating_abstract", "generating_architecture", "generating_code", "completed"]
                step_idx = 0
                if job.progress_percentage > 0:
                    step_idx = int(job.progress_percentage/25)
                
                await websocket.send_json({
                    "status": job.status,
                    "progress": job.progress_percentage,
                    "current_step": steps[min(step_idx, len(steps)-1)]
                })
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass
    finally:
        db.close()
