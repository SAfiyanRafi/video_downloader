import re
import asyncio
import logging
from pathlib import Path
from typing import List
from app.services.processing.ffmpeg_service import get_ffmpeg_executable
from app.utils.process_utils import _exec_subprocess

logger = logging.getLogger("yt_splitter")

class SceneAnalyzer:
    """
    Visual Scene Analyzer for Smart Hook Detection Engine:
    Detects scene cuts, camera transitions, and visual shifts using FFmpeg's scene filter.
    """
    def __init__(self):
        self.ffmpeg_bin = get_ffmpeg_executable()

    async def detect_scene_changes(self, video_path: Path, threshold: float = 0.3, max_seconds: float = 300.0) -> List[float]:
        """Returns a list of timestamps (in seconds) where visual scene changes occurred."""
        if not video_path.exists():
            return []

        # FFmpeg filter select='gt(scene,0.3)'
        cmd = [
            self.ffmpeg_bin, "-y",
            "-t", str(max_seconds),
            "-i", str(video_path),
            "-filter_complex", f"select='gt(scene,{threshold})',metadata=print:file=-",
            "-f", "null", "-"
        ]

        returncode, stdout, stderr = await asyncio.to_thread(_exec_subprocess, cmd)
        timestamps = []
        if returncode == 0:
            # Parse pts_time from FFmpeg metadata output
            matches = re.findall(r"pts_time:(\d+\.\d+)", stdout)
            for m in matches:
                try:
                    timestamps.append(float(m))
                except ValueError:
                    pass

        logger.info(f"[Hook Engine] Detected {len(timestamps)} visual scene changes in {video_path.name}")
        return timestamps

scene_analyzer = SceneAnalyzer()
