import asyncio
import logging
from pathlib import Path
from typing import Callable, Optional
import yt_dlp

from app.services.download.base import BaseDownloader
from app.models.job import QualityOption
from app.utils.ffmpeg_finder import get_ffmpeg_executable

logger = logging.getLogger("yt_splitter")

class YouTubeDownloader(BaseDownloader):
    """
    Downloads YouTube videos using yt-dlp library with progress hooks.
    """

    async def download(
        self,
        source: str,
        output_dir: Path,
        quality: QualityOption = QualityOption.BEST,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        out_template = str(output_dir / "original_video.%(ext)s")

        # Flexible format selector with broad compatibility
        format_selector = "bestvideo[height<=1080]+bestaudio/best[height<=1080]/bestvideo+bestaudio/best"
        if quality == QualityOption.P1080:
            format_selector = "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best"
        elif quality == QualityOption.P720:
            format_selector = "bestvideo[height<=720]+bestaudio/best[height<=720]/best"
        elif quality == QualityOption.AUDIO_ONLY:
            format_selector = "bestaudio/best"

        ffmpeg_location = get_ffmpeg_executable()

        def _yt_dlp_progress_hook(d):
            if d.get("status") == "downloading" and progress_callback:
                total_bytes = d.get("total_bytes") or d.get("total_bytes_estimate")
                downloaded_bytes = d.get("downloaded_bytes", 0)
                if total_bytes and total_bytes > 0:
                    pct = (downloaded_bytes / total_bytes) * 100.0
                    progress_callback(min(pct, 99.0))

        ydl_opts = {
            "format": format_selector,
            "outtmpl": out_template,
            "merge_output_format": "mp4",
            "quiet": True,
            "no_warnings": True,
            "no_color": True,
            "extractor_args": {
                "youtube": {
                    "player_client": ["mweb", "android", "web"],
                }
            },
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9"
            },
            "progress_hooks": [_yt_dlp_progress_hook],
            "ffmpeg_location": ffmpeg_location,
            "overwrites": True
        }

        loop = asyncio.get_running_loop()

        def _run_ydl():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(source, download=True)
                filename = ydl.prepare_filename(info)
                # Check for merged mp4 file if format was merged
                target_path = Path(filename)
                if not target_path.exists():
                    # Check for .mp4 variant
                    mp4_path = target_path.with_suffix(".mp4")
                    if mp4_path.exists():
                        return mp4_path
                return target_path

        downloaded_file = await loop.run_in_executor(None, _run_ydl)
        
        if not downloaded_file.exists():
            # Find any video file created in output_dir
            for item in output_dir.glob("original_video.*"):
                return item
            raise FileNotFoundError(f"Failed to find downloaded video file in {output_dir}")

        return downloaded_file
