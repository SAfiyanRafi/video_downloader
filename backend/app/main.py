import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.api.v1.api import api_router
from app.services.jobs.job_manager import job_manager

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing YouTube Video Splitter Platform backend...")
    cleanup_task = asyncio.create_task(job_manager.auto_cleanup_loop())
    yield
    logger.info("Shutting down backend...")
    cleanup_task.cancel()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok", "app": settings.PROJECT_NAME, "version": "1.0.0"}

@app.get("/", tags=["health"])
def root():
    return {
        "message": "Welcome to YouTube Video Splitter API",
        "docs": "/docs",
        "mcp_tools": f"{settings.API_V1_STR}/mcp/tools"
    }
