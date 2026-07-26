import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exceptions import AppError, app_error_handler, unhandled_error_handler
from app.api.v1.outline_router import router as outline_router
from app.api.v1.generate_router import router as generate_router
from app.api.v1.humanize_router import router as humanize_router

setup_logging()

app = FastAPI(
    title=settings.APP_NAME,
    description="Turns rough drafts and ideas into natural, human-sounding content.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(Exception, unhandled_error_handler)

app.include_router(outline_router)
app.include_router(generate_router)
app.include_router(humanize_router)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
async def home():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": f"{settings.APP_NAME} is running. See /docs for the API."}


@app.get("/health", tags=["Health Check"])
async def health_check():
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "azure_configured": bool(settings.AZURE_OPENAI_API_KEY),
        "tavily_configured": bool(settings.TAVILY_API_KEY),
    }
