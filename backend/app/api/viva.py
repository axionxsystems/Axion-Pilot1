from fastapi import APIRouter, HTTPException
from app.schemas.project import VivaRequest, VivaResponse
from app.core.generators.viva_gen import get_viva_response

router = APIRouter()

@router.post("/ask", response_model=VivaResponse)
async def chat_viva(request: VivaRequest):
    try:
        response_text = get_viva_response(
            api_key=request.api_key,
            history=request.messages,
            project_data=request.project_data
        )
        return VivaResponse(response=response_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
