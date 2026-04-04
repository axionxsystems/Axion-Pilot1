from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ProjectRequest(BaseModel):
    # api_key is accepted for frontend compatibility but IGNORED server-side if not explicitly given.
    # The server uses its own GROQ_API_KEY environment variable if empty.
    api_key: Optional[str] = Field(default=None, max_length=200)
    ai_provider: Optional[str] = Field(default="groq", max_length=50)
    domain: str = Field(..., min_length=2, max_length=100)
    topic: Optional[str] = Field(default="Random innovative topic", max_length=200)
    description: Optional[str] = Field(default="", max_length=1000)
    difficulty: str = Field(..., min_length=2, max_length=50)
    tech_stack: str = Field(..., min_length=2, max_length=200)
    year: str = Field(..., min_length=1, max_length=20)

class ProjectResponse(BaseModel):
    id: Optional[int] = None
    created_at: Optional[str] = None
    title: str
    abstract: str
    problem_statement: Optional[str] = ""
    architecture_description: Optional[str] = ""
    tech_stack_details: Dict[str, str] = {}
    files: List[Dict[str, str]] = []
    viva_questions: List[Dict[str, str]] = []
    tags: List[str] = []
    estimated_completion_time: Optional[str] = ""
    domain: Optional[str] = ""
    difficulty: Optional[str] = ""
    # Pipeline fields
    features: Optional[List[str]] = []
    database_design: Optional[str] = ""
    logic_flow: Optional[str] = ""
    literature_survey: Optional[str] = ""
    methodology: Optional[str] = ""
    security_measures: Optional[str] = ""

class VivaRequest(BaseModel):
    api_key: Optional[str] = Field(default=None)
    ai_provider: Optional[str] = Field(default="groq")
    messages: List[Dict[str, str]]
    project_data: Dict[str, Any]

class ProjectGenerateRequest(BaseModel):
    topic: str
    techStack: str = Field(..., alias="techStack")
    complexity: str

    class Config:
        populate_by_name = True

class ProjectFullResponse(BaseModel):
    id: int
    userId: int = Field(..., alias="user_id")
    topic: str
    techStack: str = Field(..., alias="tech_stack")
    complexity: str
    createdAt: Any = Field(..., alias="created_at")

    class Config:
        from_attributes = True
        populate_by_name = True

class ProjectContentResponse(BaseModel):
    projectId: int = Field(..., alias="project_id")
    type: str
    content: Any
    
    class Config:
        from_attributes = True
        populate_by_name = True

class ProjectGenerationResponse(BaseModel):
    project: ProjectFullResponse
    contents: List[ProjectContentResponse]

    class Config:
        populate_by_name = True

