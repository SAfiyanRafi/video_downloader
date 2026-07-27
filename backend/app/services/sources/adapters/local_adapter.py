import shutil
import asyncio
import logging
from pathlib import Path
from typing import Tuple, Optional, Callable
from app.models.source import MediaMetadata, SourceType
from app.services.sources.base_adapter import BaseSourceAdapter
from app.services.processing.ffmpeg_service import get_ffmpeg_executable
from app.utils.process_utils import _exec_subprocess

logger = logging.getLogger("yt_splitter")

class LocalAdapter(BaseSourceAdapter):

    def __init__(self):
        self.ffmpeg_bin = get_ffmpeg_executable()

    @property
    def source_type(self) -> SourceType:
        return SourceType.LOCAL_FILE

    def supports(self, source: str) -> bool:
        try:
            p = Path(source.strip())
            return p.exists() and p.is_file()
        except Exception:
            return False

    def validate(self, source: str) -> Tuple[bool, Optional[str]]:
        try:
            p = Path(source.strip())
            if not p.exists():
                return False, f"Local file not found: {source}"
            if not p.is_file():
                return False, f"Path is a directory, not a file: {source}"
            return True, None
        except Exception as e:
            return False, f"Invalid local file path: {e}"

    async def probe(self, source: str) -> MediaMetadata:
        p = Path(source.strip()).resolve()
        return MediaMetadata(
            source_type=SourceType.LOCAL_FILE,
            source_uri=str(p),
            filename=p.name,
            duration=0.0
        )

    async def import_media(
        self,
        source: str,
        target_dir: Path,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> Path:
        src_path = Path(source.strip()).resolve()
        if not src_path.exists():
            raise FileNotFoundError(f"Local file not found at {src_path}")

        target_dir.mkdir(parents=True, exist_ok=True)
        dest_path = target_dir / src_path.name
        if src_path != dest_path:
            shutil.copy2(src_path, dest_path)

        return dest_path
