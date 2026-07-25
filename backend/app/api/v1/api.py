from fastapi import APIRouter
from app.api.v1.endpoints import jobs, mcp, channels, studio, workflows, hooks

api_router = APIRouter()

api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(channels.router, prefix="/channels", tags=["channels"])
api_router.include_router(workflows.router, prefix="/workflows", tags=["workflows"])
api_router.include_router(studio.router, prefix="/studio", tags=["studio"])
api_router.include_router(hooks.router, prefix="/hooks", tags=["hooks"])
api_router.include_router(mcp.router, prefix="/mcp", tags=["mcp"])
