from fastapi import APIRouter
from app.schemas.revise import ReviseRequest, ReviseResponse
from app.services.revision_service import revision_service
from app.core.exceptions import CWTException
from app.core.logging import logger

router = APIRouter(prefix="/api/v1", tags=["Content Revision"])

@router.post("/revise", response_model=ReviseResponse)
async def revise_content_endpoint(req: ReviseRequest):
    """
    Revision Endpoint: Re-runs generation chain anchored to confirmed outline incorporating user revision feedback asynchronously.
    """
    try:
        return await revision_service.revise_content_async(req)
    except Exception as e:
        logger.error(f"Error in revision endpoint: {e}")
        raise CWTException(f"Failed to revise content: {str(e)}", status_code=500)
