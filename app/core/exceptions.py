from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.logging import logger


class AppError(Exception):
    """Raise this whenever something goes wrong and you want a clean JSON error back."""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


async def app_error_handler(request: Request, exc: AppError):
    logger.error(f"{request.url.path} -> {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "success": False},
    )


async def unhandled_error_handler(request: Request, exc: Exception):
    logger.error(f"{request.url.path} -> unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Something went wrong on our end. Please try again.", "success": False},
    )
