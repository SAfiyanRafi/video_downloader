from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class HookSensitivity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class HookCandidate(BaseModel):
    id: str
    timestamp: float = Field(..., description="Hook timestamp in seconds")
    timestamp_formatted: str = Field(..., description="Formated timestamp (e.g. 00:00:18)")
    confidence: float = Field(..., description="Confidence score percentage (0-100%)")
    reasons: List[str] = Field(..., description="Human readable reasons for hook detection")
    text_snippet: Optional[str] = Field(default=None, description="Transcript text snippet around hook")
    speech_energy: float = Field(default=0.0, description="Speech energy score")
    has_scene_change: bool = Field(default=False, description="Whether a visual scene transition occurred")
    has_curiosity_phrase: bool = Field(default=False, description="Whether a curiosity phrase was detected")

class HookAnalysisRequest(BaseModel):
    video_path: str = Field(..., description="Path to video file")
    sensitivity: HookSensitivity = Field(default=HookSensitivity.MEDIUM)
    max_suggestions: int = Field(default=5, ge=1, le=10)
    min_confidence: float = Field(default=60.0, ge=0.0, le=100.0)
    search_duration_seconds: Optional[float] = Field(default=300.0, description="Max search duration window (None for entire video)")

class HookAnalysisResponse(BaseModel):
    video_name: str
    total_scene_changes: int
    candidates: List[HookCandidate]
    processing_time_seconds: float
