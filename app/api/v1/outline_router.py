from fastapi import APIRouter
from app.schemas.outline import OutlineRequest, OutlineResponse
from app.services.outline_service import outline_service
from app.core.exceptions import AppError
from app.core.logging import logger

router = APIRouter(prefix="/api/v1", tags=["Outline Generation"])

@router.post("/outline", response_model=OutlineResponse)
async def generate_outline_endpoint(req: OutlineRequest):
    """Looks at competitors, then builds an editable content outline."""
    try:
        return await outline_service.generate_outline_async(req)
    except Exception as e:
        logger.error(f"Outline request failed: {e}")
        raise AppError(f"Could not generate the outline: {e}", status_code=500)
