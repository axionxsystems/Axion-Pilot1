from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class ProjectRequest(BaseModel):
    api_key: str
    domain: str
    topic: Optional[str] = "Random innovative topic"
    difficulty: str
    tech_stack: str
    year: str

class ProjectResponse(BaseModel):
    title: str
    abstract: str
    problem_statement: Optional[str] = ""
    architecture_description: Optional[str] = ""
    tech_stack_details: Dict[str, str] = {}
    files: List[Dict[str, str]] = []
    viva_questions: List[Dict[str, str]] = []
    # Optional fields for compatibility if needed
    features: Optional[List[str]] = []
    tech_stack: Optional[List[str]] = []

class VivaRequest(BaseModel):
    api_key: str
    messages: List[Dict[str, str]]
    project_data: Dict[str, Any]

class VivaResponse(BaseModel):
    response: str
