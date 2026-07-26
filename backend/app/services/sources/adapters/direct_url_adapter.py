import urllib.request
import asyncio
import logging
from pathlib import Path
from typing import Tuple, Optional, Callable
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

    async def import_media(
        self,
        source: str,
        target_dir: Path,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> Path:
        target_dir.mkdir(parents=True, exist_ok=True)
        url = source.strip()
        filename = url.split("/")[-1].split("?")[0] or "direct_video.mp4"
        if not filename.endswith((".mp4", ".mov", ".mkv", ".webm", ".avi")):
            filename += ".mp4"
        out_file = target_dir / filename

        # Tier 1: Try yt-dlp first (handles CDN tokens & HTTP headers automatically)
        from app.services.download.youtube import YouTubeDownloader
        try:
            logger.info(f"[DirectUrlAdapter] Downloading direct video via yt-dlp: {url}")
            yt_dl = YouTubeDownloader()
            dl_file = await yt_dl.download(url, target_dir, progress_callback=progress_callback)
            if dl_file and dl_file.exists() and dl_file.stat().st_size > 0:
                return dl_file
        except Exception as e:
            logger.warning(f"[DirectUrlAdapter] yt-dlp direct download failed: {e}. Falling back to FFmpeg/urllib...")

        # Tier 2: Try FFmpeg stream copy with browser headers
        from app.services.processing.ffmpeg_service import get_ffmpeg_executable
        from app.services.branding.branding_service import _exec_subprocess

        ffmpeg_bin = get_ffmpeg_executable()
        cmd = [
            ffmpeg_bin, "-y",
            "-user_agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "-headers", "Referer: https://aniwatch.co.at/\r\n",
            "-i", url,
            "-c", "copy",
            str(out_file)
        ]

        returncode, _, err = await asyncio.to_thread(_exec_subprocess, cmd)
        if returncode == 0 and out_file.exists() and out_file.stat().st_size > 0:
            return out_file

        # Tier 3: Fallback to urllib with browser headers
        def _download_urllib():
            logger.info(f"[DirectUrlAdapter] Downloading via urllib: {url}")
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                    "Accept": "*/*",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Referer": "https://aniwatch.co.at/"
                }
            )
            import shutil
            with urllib.request.urlopen(req) as resp, open(out_file, "wb") as f:
                shutil.copyfileobj(resp, f)

        try:
            await asyncio.to_thread(_download_urllib)
            if out_file.exists() and out_file.stat().st_size > 0:
                return out_file
        except Exception as e:
            raise RuntimeError(f"Failed to download direct media URL: {e}")

        return out_file
