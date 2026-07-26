import asyncio
import logging
from pathlib import Path
from typing import List, Optional
from app.services.processing.ffmpeg_service import get_ffmpeg_executable
from app.utils.process_utils import _exec_subprocess

logger = logging.getLogger("yt_splitter")

class ThumbnailService:
    """
    Smart Thumbnail Engine:
    - Extracts high-quality candidate frames across video duration.
    - Saves crisp .jpg thumbnail image candidates alongside exports.
    """
    def __init__(self):
        self.ffmpeg_bin = get_ffmpeg_executable()

    async def generate_thumbnails(
        self,
        video_path: Path,
        output_dir: Path,
        count: int = 3
    ) -> List[Path]:
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found at {video_path}")

        output_dir.mkdir(parents=True, exist_ok=True)
        thumbnails: List[Path] = []

        # Get video duration using FFmpeg
        cmd_dur = [self.ffmpeg_bin, "-i", str(video_path)]
        _, _, stderr = await asyncio.to_thread(_exec_subprocess, cmd_dur)

        import re
        dur_match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", stderr)
        total_sec = 10.0
        if dur_match:
            h, m, s = dur_match.groups()
            total_sec = int(h) * 3600 + int(m) * 60 + float(s)

        # Timestamps for extraction (e.g. 25%, 50%, 75%)
        timestamps = [(total_sec * (i + 1) / (count + 1)) for i in range(count)]

        for idx, ts in enumerate(timestamps, start=1):
            out_img = output_dir / f"{video_path.stem}_thumb_{idx:02d}.jpg"
            cmd_thumb = [
                self.ffmpeg_bin, "-y",
                "-ss", f"{ts:.2f}",
                "-i", str(video_path),
                "-vframes", "1",
                "-q:v", "2",  # High quality JPEG
                str(out_img)
            ]
            returncode, _, err = await asyncio.to_thread(_exec_subprocess, cmd_thumb)
            if returncode == 0 and out_img.exists() and out_img.stat().st_size > 0:
                thumbnails.append(out_img)
                logger.info(f"Generated thumbnail candidate {idx}: {out_img.name}")
            else:
                logger.warning(f"Failed to generate thumbnail candidate {idx}: {err[:200]}")

        return thumbnails

thumbnail_service = ThumbnailService()
