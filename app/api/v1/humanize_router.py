from fastapi import APIRouter

from app.schemas.humanize import HumanizeRequest, HumanizeResponse
from app.services.humanize_service import humanize_service
from app.core.exceptions import AppError
from app.core.logging import logger

router = APIRouter(prefix="/api/v1", tags=["Content Humanization"])


@router.post("/humanize", response_model=HumanizeResponse)
async def humanize_text(req: HumanizeRequest):
    """Takes any text and rewrites it so it reads naturally, like a person wrote it."""
    try:
        return await humanize_service.humanize(req)
    except Exception as e:
        logger.error(f"Humanize request failed: {e}")
        raise AppError(f"Could not humanize this text: {e}", status_code=500)
