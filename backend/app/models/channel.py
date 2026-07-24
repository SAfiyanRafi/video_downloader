from typing import Optional
from pydantic import BaseModel, Field

class ChannelProfile(BaseModel):
    id: str = Field(..., description="Unique identifier of channel profile")
    display_name: str = Field(..., description="Human-readable channel display name")
    intro: Optional[str] = Field(None, description="Relative path to intro MP4 video")
    outro: Optional[str] = Field(None, description="Relative path to outro MP4 video")
    filename_prefix: Optional[str] = Field(None, description="Prefix for split part filenames")
    
    # Future expansion fields
    watermark: Optional[str] = Field(None, description="Watermark image asset path")
    logo: Optional[str] = Field(None, description="Channel logo asset path")
    thumbnail: Optional[str] = Field(None, description="Channel default thumbnail asset path")
    resolution: Optional[str] = Field("1080p", description="Default channel output resolution")
    format: Optional[str] = Field("mp4", description="Output container format")
    normalize_audio: Optional[bool] = Field(True, description="Enable audio level normalization")
    default_quality: Optional[str] = Field("best", description="Default download quality option")
