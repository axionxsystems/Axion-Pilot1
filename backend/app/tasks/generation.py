from app.celery import app
from app.models.job import Job
from app.models.project import Project
from app.database import SessionLocal
from app.services.project_service import ProjectService
import json
from datetime import datetime
import time

# Mocking the missing llm_provider for now, or using a placeholder
def generate_code(project_id: str, section: str):
    time.sleep(1) # Simulate delay
    return f"Generated {section} for project {project_id}"

@app.task(bind=True, max_retries=3)
def generate_project_async(self, project_id: str, org_id: str, user_id: str):
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.celery_task_id == self.request.id).first()
        if not job:
            job = Job(
                org_id=org_id,
                project_id=project_id,
                celery_task_id=self.request.id,
                job_type="generate_project",
                status="processing"
            )
            db.add(job)
            db.commit()

        # Step 1: Generate abstract
        job.progress_percentage = 25
        db.commit()
        abstract = generate_code(project_id, "abstract")

        # Step 2: Generate architecture
        job.progress_percentage = 50
        db.commit()
        architecture = generate_code(project_id, "architecture")

        # Step 3: Generate code
        job.progress_percentage = 75
        db.commit()
        code = generate_code(project_id, "code")

        # Step 4: Store results
        project = db.query(Project).filter(Project.id == project_id).first()
        if project:
            project.status = "completed"
            db.commit()

            duration_ms = int((datetime.utcnow() - project.created_at).total_seconds() * 1000)
            document_count = 3
            code_line_count = len(abstract.splitlines()) + len(architecture.splitlines()) + len(code.splitlines())
            ProjectService.log_generation_metrics(
                db,
                org_id,
                int(user_id) if user_id.isdigit() else project.user_id,
                duration_ms,
                document_count,
                code_line_count,
                feature_names=["async_abstract", "async_architecture", "async_code"],
                success=True,
                failed=False,
            )

        job.status = "completed"
        job.progress_percentage = 100
        job.result = {"abstract_lines": len(abstract), "code_lines": len(code)}
        job.completed_at = datetime.utcnow()
        db.commit()

        return {"status": "completed", "project_id": project_id}

    except Exception as exc:
        if 'job' in locals() and job:
            job.status = "failed"
            job.error_message = str(exc)
            db.commit()
        raise self.retry(exc=exc, countdown=60)
    finally:
        db.close()

@app.task(bind=True, max_retries=2)
def generate_pdf_async(self, project_id: str):
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    import io
    
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return {"error": "Project not found"}
        
        # Generate PDF
        pdf_buffer = io.BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=letter)
        c.drawString(100, 750, f"Project: {project.title}")
        c.drawString(100, 730, f"Abstract: {project.description[:200]}...")
        c.save()
        
        # Save to storage
        pdf_path = f"projects/{project.org_id}/{project_id}/report.pdf"
        # TODO: upload to S3 or local storage
        
        return {"pdf_path": pdf_path}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=30)
    finally:
        db.close()

@app.task(bind=True, max_retries=3)
def send_notification_async(self, user_id: str, message: str):
    try:
        print(f"Sending notification to {user_id}: {message}")
        time.sleep(1) # Simulate email/push sending
        return {"status": "sent", "user_id": user_id}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=30)
