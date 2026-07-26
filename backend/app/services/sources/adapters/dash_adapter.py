import asyncio
import logging
from pathlib import Path
from typing import Tuple, Optional, Callable
from app.models.source import MediaMetadata, SourceType
from app.services.sources.base_adapter import BaseSourceAdapter
from app.services.processing.ffmpeg_service import get_ffmpeg_executable
from app.services.branding.branding_service import _exec_subprocess

logger = logging.getLogger("yt_splitter")

class DashAdapter(BaseSourceAdapter):
    """
    Standard MPEG-DASH Manifest (.mpd) Stream Adapter using FFmpeg stream dump.
    """
    def __init__(self):
        self.ffmpeg_bin = get_ffmpeg_executable()

    @property
    def source_type(self) -> SourceType:
        return SourceType.DASH

    def supports(self, source: str) -> bool:
        s = source.strip().lower()
        return (s.startswith("http://") or s.startswith("https://")) and (".mpd" in s)

    def validate(self, source: str) -> Tuple[bool, Optional[str]]:
        if not self.supports(source):
            return False, "Not a valid MPEG-DASH .mpd manifest URL"
        return True, None

    async def probe(self, source: str) -> MediaMetadata:
        url = source.strip()
        filename = url.split("/")[-1].split("?")[0].replace(".mpd", ".mp4") or "dash_stream.mp4"
        return MediaMetadata(
            source_type=SourceType.DASH,
            source_uri=url,
            filename=filename
        )

    async def import_media(
        self,
        source: str,
        target_dir: Path,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> Path:
        target_dir.mkdir(parents=True, exist_ok=True)
        url = source.strip()
        out_file = target_dir / "dash_stream.mp4"

        cmd = [
            self.ffmpeg_bin, "-y",
            "-i", url,
            "-c", "copy",
            str(out_file)
        ]

        logger.info(f"[DashAdapter] Dumping DASH manifest {url} -> {out_file.name}...")
        returncode, _, err = await asyncio.to_thread(_exec_subprocess, cmd)
        if returncode != 0:
            raise RuntimeError(f"DASH stream dump failed: {err[:200]}")

        return out_file
