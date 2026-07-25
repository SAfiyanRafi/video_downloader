import shutil
import asyncio
import logging
from pathlib import Path
from typing import Tuple, Optional
from app.models.source import MediaMetadata, SourceType
from app.services.sources.base_adapter import BaseSourceAdapter
from app.services.processing.ffmpeg_service import get_ffmpeg_executable
from app.services.branding.branding_service import _exec_subprocess

logger = logging.getLogger("yt_splitter")

class LocalAdapter(BaseSourceAdapter):
    SUPPORTED_EXTS = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".flv"}

    def __init__(self):
        self.ffmpeg_bin = get_ffmpeg_executable()

    @property
    def source_type(self) -> SourceType:
        return SourceType.LOCAL_FILE

    def supports(self, source: str) -> bool:
        p = Path(source.strip())
        return p.is_file() and p.suffix.lower() in self.SUPPORTED_EXTS

    def validate(self, source: str) -> Tuple[bool, Optional[str]]:
        p = Path(source.strip())
        if not p.exists():
            return False, f"Local file not found: {source}"
        if not p.is_file():
            return False, f"Path is a directory, not a file: {source}"
        if p.suffix.lower() not in self.SUPPORTED_EXTS:
            return False, f"Unsupported file extension: {p.suffix}"
        return True, None

    async def probe(self, source: str) -> MediaMetadata:
        p = Path(source.strip()).resolve()
        return MediaMetadata(
            source_type=SourceType.LOCAL_FILE,
            source_uri=str(p),
            filename=p.name,
            duration=0.0
        )

    async def import_media(self, source: str, target_dir: Path) -> Path:
        src_path = Path(source.strip()).resolve()
        if not src_path.exists():
            raise FileNotFoundError(f"Local file not found at {src_path}")

        target_dir.mkdir(parents=True, exist_ok=True)
        dest_path = target_dir / src_path.name
        if src_path != dest_path:
            shutil.copy2(src_path, dest_path)

        return dest_path
