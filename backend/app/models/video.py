from typing import Optional
from pydantic import BaseModel, Field

class VideoMetadata(BaseModel):
    duration: float = Field(..., description="Duration in seconds")
    width: Optional[int] = Field(None, description="Video width in pixels")
    height: Optional[int] = Field(None, description="Video height in pixels")
    fps: Optional[float] = Field(None, description="Frames per second")
    codec_name: Optional[str] = Field(None, description="Video stream codec")
    audio_codec: Optional[str] = Field(None, description="Audio stream codec")
    bit_rate: Optional[int] = Field(None, description="Bitrate in bits/s")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    title: Optional[str] = Field(None, description="Video title")

class SegmentInfo(BaseModel):
    part_number: int
    start_time: float
    end_time: float
    duration: float
    filename: str
    download_url: Optional[str] = None
