from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

class SubtitleStylePreset(str, Enum):
    TIKTOK = "tiktok"
    MRBEAST = "mrbeast"
    GAMING = "gaming"
    PODCAST = "podcast"
    MINIMAL = "minimal"

class SubtitleMode(str, Enum):
    BURNED_IN = "burned_in"
    SOFT_SRT = "soft_srt"
    BOTH = "both"

class StudioJobRequest(BaseModel):
    video_path: str = Field(..., description="Path to local video file")
    enable_subtitles: bool = Field(default=True, description="Generate AI subtitles")
    subtitle_preset: SubtitleStylePreset = Field(default=SubtitleStylePreset.TIKTOK)
    subtitle_mode: SubtitleMode = Field(default=SubtitleMode.BURNED_IN)
    normalize_audio: bool = Field(default=True, description="EBU R128 loudness normalization")
    target_lufs: float = Field(default=-16.0, description="Target LUFS (-16.0 for Shorts/Reels, -24.0 for standard)")
    pitch_semitones: float = Field(default=0.0, description="Subtle pitch adjustment (-3.0 to +3.0 semitones)")
    whisper_model: str = Field(default="tiny", description="Whisper model size (tiny, base, small, medium)")

class StudioJobResponse(BaseModel):
    job_id: str
    video_name: str
    status: str
    progress: float
    message: str
    output_video_path: Optional[str] = None
    srt_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    error: Optional[str] = None
