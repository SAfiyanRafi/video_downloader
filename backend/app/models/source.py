from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class SourceType(str, Enum):
    LOCAL_FILE = "local_file"
    FOLDER = "folder"
    DIRECT_URL = "direct_url"
    HLS = "hls"
    DASH = "dash"
    YOUTUBE = "youtube"
    WEB_PAGE = "web_page"

class MediaMetadata(BaseModel):
    source_type: SourceType
    source_uri: str
    filename: str
    duration: float = Field(default=0.0, description="Duration in seconds")
    resolution: str = Field(default="1920x1080")
    width: int = Field(default=1920)
    height: int = Field(default=1080)
    fps: float = Field(default=30.0)
    vcodec: Optional[str] = Field(default="h264")
    acodec: Optional[str] = Field(default="aac")
    bitrate: Optional[int] = Field(default=None)
    thumbnail: Optional[str] = Field(default=None)

class ImportResult(BaseModel):
    local_path: str
    metadata: MediaMetadata
