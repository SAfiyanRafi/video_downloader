import urllib.request
import asyncio
import logging
from pathlib import Path
from typing import Tuple, Optional
from app.models.source import MediaMetadata, SourceType
from app.services.sources.base_adapter import BaseSourceAdapter

logger = logging.getLogger("yt_splitter")

class DirectUrlAdapter(BaseSourceAdapter):
    SUPPORTED_EXTS = {".mp4", ".mov", ".mkv", ".avi", ".webm"}

    @property
    def source_type(self) -> SourceType:
        return SourceType.DIRECT_URL

    def supports(self, source: str) -> bool:
        s = source.strip().lower()
        if not (s.startswith("http://") or s.startswith("https://")):
            return False
        return any(s.endswith(ext) or f"{ext}?" in s for ext in self.SUPPORTED_EXTS)

    def validate(self, source: str) -> Tuple[bool, Optional[str]]:
        if not self.supports(source):
            return False, "Not a valid direct video URL"
        return True, None

    async def probe(self, source: str) -> MediaMetadata:
        url = source.strip()
        filename = url.split("/")[-1].split("?")[0] or "direct_video.mp4"
        return MediaMetadata(
            source_type=SourceType.DIRECT_URL,
            source_uri=url,
            filename=filename
        )

    async def import_media(self, source: str, target_dir: Path) -> Path:
        target_dir.mkdir(parents=True, exist_ok=True)
        url = source.strip()
        filename = url.split("/")[-1].split("?")[0] or "direct_video.mp4"
        out_file = target_dir / filename

        def _download():
            logger.info(f"[DirectUrlAdapter] Downloading {url} -> {out_file.name}...")
            urllib.request.urlretrieve(url, str(out_file))

        await asyncio.to_thread(_download)
        return out_file
