import asyncio
import logging
from pathlib import Path
from typing import Tuple, Optional, Callable
from app.models.source import MediaMetadata, SourceType
from app.services.sources.base_adapter import BaseSourceAdapter
from app.services.processing.ffmpeg_service import get_ffmpeg_executable
from app.services.branding.branding_service import _exec_subprocess

logger = logging.getLogger("yt_splitter")

class HlsAdapter(BaseSourceAdapter):
    """
    Standard HLS Playlist (.m3u8) Stream Adapter using FFmpeg stream dump.
    """
    def __init__(self):
        self.ffmpeg_bin = get_ffmpeg_executable()

    @property
    def source_type(self) -> SourceType:
        return SourceType.HLS

    def supports(self, source: str) -> bool:
        s = source.strip().lower()
        return (s.startswith("http://") or s.startswith("https://")) and (".m3u8" in s)

    def validate(self, source: str) -> Tuple[bool, Optional[str]]:
        if not self.supports(source):
            return False, "Not a valid HLS .m3u8 stream URL"
        return True, None

    async def probe(self, source: str) -> MediaMetadata:
        url = source.strip()
        filename = url.split("/")[-1].split("?")[0].replace(".m3u8", ".mp4") or "hls_stream.mp4"
        return MediaMetadata(
            source_type=SourceType.HLS,
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
        # Tier 1: Try yt-dlp first (best HLS playlist handling & 16-thread speed)
        from app.services.download.youtube import YouTubeDownloader
        try:
            logger.info(f"[HlsAdapter] Downloading HLS playlist via yt-dlp: {url}")
            yt_dl = YouTubeDownloader()
            dl_file = await yt_dl.download(url, target_dir, progress_callback=progress_callback)
            if dl_file and dl_file.exists() and dl_file.stat().st_size > 0:
                return dl_file
        except Exception as e:
            logger.warning(f"[HlsAdapter] yt-dlp HLS download failed: {e}. Falling back to FFmpeg stream copy...")

        # Tier 2: Fallback to FFmpeg stream copy
        cmd = [
            self.ffmpeg_bin, "-y",
            "-user_agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "-headers", "Referer: https://aniwatch.co.at/\r\n",
            "-i", url,
            "-c", "copy",
            str(out_file)
        ]

        logger.info(f"[HlsAdapter] Dumping HLS stream via FFmpeg {url} -> {out_file.name}...")
        returncode, _, err = await asyncio.to_thread(_exec_subprocess, cmd)
        if returncode != 0:
            raise RuntimeError(f"HLS stream dump failed: {err[-300:]}")

        return out_file
