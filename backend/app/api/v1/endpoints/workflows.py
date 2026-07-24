from typing import List
from fastapi import APIRouter, HTTPException, status
from app.models.workflow import WorkflowProfile
from app.services.branding.workflow_service import workflow_service
from app.services.ai.content_helper import ai_content_helper, AIContentSuggestions

router = APIRouter()

@router.get("", response_model=List[WorkflowProfile])
async def list_workflows():
    """
    Returns configured Workflow Profiles (Shorts vs Long-Form).
    """
    return workflow_service.get_all_workflows()

@router.post("/ai-suggestions", response_model=AIContentSuggestions)
async def generate_ai_suggestions(title: str, transcript: str = ""):
    """
    Generates AI title options, description drafts, hashtags, and chapters for upload preparation.
    """
    return ai_content_helper.generate_suggestions(title, transcript)
