from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from app.models.video import VideoMetadata, SegmentInfo

class QualityOption(str, Enum):
    BEST = "best"
    P2160 = "2160p"
    P1440 = "1440p"
    P1080 = "1080p"
    P720 = "720p"
    P480 = "480p"
    AUDIO_ONLY = "audio_only"

class AspectRatioOption(str, Enum):
    ORIGINAL = "original"
    V_9_16 = "9:16"
    H_16_9 = "16:9"
    S_1_1 = "1:1"
    P_4_5 = "4:5"

class ExportPreset(str, Enum):
    ORIGINAL = "original_quality"
    HIGH = "high_quality"
    BALANCED = "balanced"
    SMALL = "small_file"

class PaddingMode(str, Enum):
    BLACK_BARS = "black_bars"
    BLURRED = "blurred"
    SOLID_COLOR = "solid_color"

class NamingTemplate(str, Enum):
    CHANNEL_PART = "{channel}_Part_{number}"
    ORIGINAL_CLIP = "{original}_Clip_{number}"
    DATE_CHANNEL_PART = "{date}_{channel}_Part_{number}"

class JobStatus(str, Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    ANALYZING = "analyzing"
    SPLITTING = "splitting"
    ZIPPING = "zipping"
    COMPLETED = "completed"
    FAILED = "failed"

class JobCreateRequest(BaseModel):
    url: str = Field(..., description="YouTube Video URL")
    parts: int = Field(default=4, ge=2, le=50, description="Number of equal parts to split into")
    quality: QualityOption = Field(default=QualityOption.BEST, description="Desired download resolution quality")
    aspect_ratio: AspectRatioOption = Field(default=AspectRatioOption.ORIGINAL, description="Target aspect ratio dimension (e.g. 9:16 for Shorts/Reels, 16:9, 1:1)")
    export_preset: ExportPreset = Field(default=ExportPreset.HIGH, description="Export encoding preset (original, high, balanced, small)")
    padding_mode: PaddingMode = Field(default=PaddingMode.BLACK_BARS, description="Padding style for aspect ratio letterboxing (black_bars, blurred, solid_color)")
    naming_template: NamingTemplate = Field(default=NamingTemplate.CHANNEL_PART, description="Filename naming pattern template")
    crop_fill: bool = Field(default=False, description="Enable cropping instead of fitting whole frame")

class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    progress: float = Field(0.0, description="Progress percentage 0-100")
    message: str = "Job created"
    created_at: datetime
    updated_at: datetime
    error: Optional[str] = None
    metadata: Optional[VideoMetadata] = None
    url: Optional[str] = None
    parts: Optional[int] = None
    channel: Optional[str] = None

class JobDownloadsResponse(BaseModel):
    job_id: str
    status: JobStatus
    zip_url: Optional[str] = None
    clips: List[SegmentInfo] = []
    metadata: Optional[VideoMetadata] = None
