from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any

from app.models.job import JobCreateRequest, QualityOption
from app.services.jobs.job_manager import job_manager
from app.utils.validators import validate_youtube_url

router = APIRouter()

class MCPToolDefinition(BaseModel):
    name: str = "split_video"
    description: str = "Downloads a YouTube video, splits it into equal parts losslessly with FFmpeg, and provides downloadable clip links and a ZIP archive."
    parameters: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "Valid YouTube Video URL"
            },
            "parts": {
                "type": "integer",
                "description": "Number of equal parts to split video into (between 2 and 50)",
                "default": 4
            },
            "quality": {
                "type": "string",
                "enum": ["best", "1080p", "720p", "audio_only"],
                "default": "best"
            }
        },
        "required": ["url"]
    }

@router.get("/tools")
def get_mcp_tools():
    """Returns available MCP tools list for AI assistants."""
    return {"tools": [MCPToolDefinition()]}

@router.post("/execute")
async def execute_mcp_tool(payload: Dict[str, Any]):
    """
    Executes split_video tool call from an MCP server or AI assistant.
    """
    tool_name = payload.get("name") or payload.get("tool")
    arguments = payload.get("arguments", {})

    if tool_name != "split_video":
        raise HTTPException(status_code=400, detail=f"Unknown tool: {tool_name}")

    url = arguments.get("url")
    parts = arguments.get("parts", 4)
    quality_str = arguments.get("quality", "best")

    try:
        quality = QualityOption(quality_str)
    except ValueError:
        quality = QualityOption.BEST

    clean_url = validate_youtube_url(url)
    job_response = job_manager.create_job(clean_url, parts, quality)

    return {
        "status": "success",
        "job_id": job_response.job_id,
        "message": f"Video splitting job '{job_response.job_id}' started for {url} into {parts} parts.",
        "status_url": f"/api/v1/jobs/{job_response.job_id}",
        "downloads_url": f"/api/v1/jobs/{job_response.job_id}/downloads"
    }
