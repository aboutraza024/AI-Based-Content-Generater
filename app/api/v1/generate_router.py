from fastapi import APIRouter
from app.schemas.generate import GenerateRequest, GenerateResponse
from app.services.generation_service import generation_service
from app.core.exceptions import AppError
from app.core.logging import logger

router = APIRouter(prefix="/api/v1", tags=["Content Generation"])

@router.post("/generate", response_model=GenerateResponse)
async def generate_content_endpoint(req: GenerateRequest):
    """Generates the full piece of content from a confirmed outline."""
    try:
        return await generation_service.generate_full_content_async(req)
    except Exception as e:
        logger.error(f"Generate request failed: {e}")
        raise AppError(f"Could not generate the content: {e}", status_code=500)
