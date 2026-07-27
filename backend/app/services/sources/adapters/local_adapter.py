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

import os

def resolve_local_path(source: str) -> Path:
    clean = source.strip().strip('"').strip("'")
    if not clean:
        return Path(clean)
    
    p = Path(clean)
    if p.exists() and p.is_file():
        return p.resolve()

    # Search common user directories on Windows
    user_profile = os.environ.get("USERPROFILE", "C:\\Users\\ABC")
    common_dirs = [
        Path(user_profile) / "OneDrive" / "Desktop",
        Path(user_profile) / "Desktop",
        Path(user_profile) / "OneDrive" / "Desktop" / "Youtube" / "Download",
        Path(user_profile) / "Downloads",
        Path(user_profile) / "Videos",
    ]

    ext_candidates = ["", ".ts", ".mp4", ".mkv", ".mov", ".avi", ".webm", ".flv"]

    for base_dir in common_dirs:
        for ext in ext_candidates:
            target = base_dir / f"{clean}{ext}"
            if target.exists() and target.is_file():
                logger.info(f"[LocalAdapter] Auto-resolved '{source}' -> {target.resolve()}")
                return target.resolve()

    return p

class LocalAdapter(BaseSourceAdapter):

    def __init__(self):
        self.ffmpeg_bin = get_ffmpeg_executable()

    @property
    def source_type(self) -> SourceType:
        return SourceType.LOCAL_FILE

    def supports(self, source: str) -> bool:
        try:
            s = source.strip().strip('"').strip("'")
            if s.startswith("http://") or s.startswith("https://"):
                return False
            resolved = resolve_local_path(s)
            return resolved.exists() and resolved.is_file()
        except Exception:
            return False

    def validate(self, source: str) -> Tuple[bool, Optional[str]]:
        try:
            resolved = resolve_local_path(source)
            if not resolved.exists():
                return False, f"Local file not found: '{source}'. Please verify file path or use 'Browse Local File'."
            if not resolved.is_file():
                return False, f"Path is a directory, not a file: '{source}'"
            return True, None
        except Exception as e:
            return False, f"Invalid local file path: {e}"

    async def probe(self, source: str) -> MediaMetadata:
        resolved = resolve_local_path(source)
        return MediaMetadata(
            source_type=SourceType.LOCAL_FILE,
            source_uri=str(resolved),
            filename=resolved.name,
            duration=0.0
        )

    async def import_media(
        self,
        source: str,
        target_dir: Path,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> Path:
        resolved = resolve_local_path(source)
        if not resolved.exists():
            raise FileNotFoundError(f"Local file not found at {resolved}")

        target_dir.mkdir(parents=True, exist_ok=True)
        dest_path = target_dir / resolved.name
        if resolved != dest_path:
            shutil.copy2(resolved, dest_path)

        return dest_path
