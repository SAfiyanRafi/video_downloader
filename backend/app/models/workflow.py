from typing import Optional
from pydantic import BaseModel, Field

class WorkflowProfile(BaseModel):
    id: str
    display_name: str
    description: str
    aspect_ratio: str = Field(default="original")
    padding_mode: str = Field(default="black_bars")
    allow_intro_outro: bool = Field(default=True)
    enable_subtitles: bool = Field(default=False)
    subtitle_preset: str = Field(default="tiktok")
    enable_thumbnails: bool = Field(default=True)
    export_preset: str = Field(default="high_quality")
