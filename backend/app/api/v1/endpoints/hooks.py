from typing import List, Dict
from fastapi import APIRouter, HTTPException, status
from app.models.hook import HookAnalysisRequest, HookAnalysisResponse
from app.services.hooks.hook_engine import hook_engine

router = APIRouter()

@router.post("/analyze", response_model=HookAnalysisResponse)
async def analyze_smart_hooks(request: HookAnalysisRequest):
    """
    Analyzes a video file and identifies ranked starting timestamps (hooks) for short-form content.
    Acts as an AI editorial advisor without forcing edits.
    """
    try:
        return await hook_engine.analyze_hooks(request)
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/settings")
async def get_hook_settings():
    """
    Returns configurable curiosity phrases and detection settings.
    """
    return {
        "curiosity_keywords": hook_engine.curiosity_keywords,
        "default_sensitivity": "medium",
        "default_min_confidence": 60.0,
        "default_max_suggestions": 5
    }
