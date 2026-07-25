import asyncio
import logging
from pathlib import Path
from typing import Optional
from pydantic import BaseModel
from app.services.download.youtube import YouTubeDownloader
from app.services.metadata.ffprobe_service import FFprobeService

logger = logging.getLogger("yt_splitter")

class VideoMetadataInspection(BaseModel):
    title: str
    duration: float
    resolution: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    fps: Optional[float] = None
    video_codec: Optional[str] = None
    audio_codec: Optional[str] = None
    bitrate: Optional[int] = None
    filesize_approx: Optional[int] = None
    is_url: bool = True

class MetadataInspector:
    """
    Metadata Inspector:
    Inspects video parameters (resolution, fps, codecs, duration) before job execution.
    """
    def __init__(self):
        self.downloader = YouTubeDownloader()
        self.ffprobe_service = FFprobeService()

    async def inspect_url(self, url: str) -> VideoMetadataInspection:
        meta = await self.downloader.extract_info(url)
        res_str = None
        if meta.width and meta.height:
            res_str = f"{meta.width}x{meta.height}"

        return VideoMetadataInspection(
            title=meta.title or "YouTube Video",
            duration=meta.duration,
            resolution=res_str,
            width=meta.width,
            height=meta.height,
            fps=meta.fps,
            video_codec=meta.vcodec,
            audio_codec=meta.acodec,
            bitrate=meta.bitrate,
            filesize_approx=meta.filesize_approx,
            is_url=True
        )

    async def inspect_file(self, file_path: Path) -> VideoMetadataInspection:
        meta = await self.ffprobe_service.get_metadata(file_path)
        res_str = None
        if meta.width and meta.height:
            res_str = f"{meta.width}x{meta.height}"

        return VideoMetadataInspection(
            title=file_path.stem,
            duration=meta.duration,
            resolution=res_str,
            width=meta.width,
            height=meta.height,
            fps=meta.fps,
            video_codec=meta.video_codec,
            audio_codec=meta.audio_codec,
            bitrate=meta.bitrate,
            filesize_approx=file_path.stat().st_size if file_path.exists() else None,
            is_url=False
        )

metadata_inspector = MetadataInspector()
