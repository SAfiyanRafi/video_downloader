import re
import asyncio
import logging
from pathlib import Path
from typing import Tuple, Optional, Callable
from app.models.source import MediaMetadata, SourceType
from app.services.sources.base_adapter import BaseSourceAdapter
from app.services.download.youtube import YouTubeDownloader

logger = logging.getLogger("yt_splitter")

class YouTubeAdapter(BaseSourceAdapter):
    def __init__(self):
        self.yt_service = YouTubeDownloader()

    @property
    def source_type(self) -> SourceType:
        return SourceType.YOUTUBE

    def supports(self, source: str) -> bool:
        s = source.strip().lower()
        if not (s.startswith("http://") or s.startswith("https://")):
            return False
        if ".m3u8" in s or ".mpd" in s:
            return False
        if any(s.endswith(ext) or f"{ext}?" in s for ext in [".mp4", ".mov", ".mkv", ".webm", ".avi"]):
            return False
        return True

    def validate(self, source: str) -> Tuple[bool, Optional[str]]:
        s = source.strip().lower()
        if not (s.startswith("http://") or s.startswith("https://")):
            return False, "Invalid web URL format. URL must start with http:// or https://"
        return True, None

    async def probe(self, source: str) -> MediaMetadata:
        try:
            info = await self.yt_service.extract_info(source.strip())
            return MediaMetadata(
                source_type=SourceType.YOUTUBE,
                source_uri=source,
                filename=f"{info.get('title', 'youtube_video')}.mp4",
                duration=float(info.get('duration', 0.0)),
                resolution=f"{info.get('width', 1920)}x{info.get('height', 1080)}",
                width=int(info.get('width', 1920)),
                height=int(info.get('height', 1080)),
                fps=float(info.get('fps', 30.0)),
                thumbnail=info.get('thumbnail')
            )
        except Exception as e:
            logger.warning(f"Failed to probe YouTube URL: {e}")
            return MediaMetadata(
                source_type=SourceType.YOUTUBE,
                source_uri=source,
                filename="youtube_video.mp4"
            )

    async def import_media(
        self,
        source: str,
        target_dir: Path,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> Path:
        target_dir.mkdir(parents=True, exist_ok=True)
        out_file = await self.yt_service.download(source.strip(), target_dir, progress_callback=progress_callback)
        return Path(out_file).resolve()
