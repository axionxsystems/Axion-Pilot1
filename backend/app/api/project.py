from fastapi import APIRouter, Depends
from app.core.generators.project_gen import generate_project

router = APIRouter()

@router.post("/generate")
def generate_project_api(payload: dict):
    return generate_project(payload)
