import asyncio
import json
import logging
from pathlib import Path
from typing import Optional
from app.models.video import VideoMetadata
from app.utils.ffmpeg_finder import get_ffprobe_executable

logger = logging.getLogger("yt_splitter")

class FFprobeService:
    """
    Service responsible for gathering detailed video metadata using ffprobe.
    """

    async def get_metadata(self, video_path: Path) -> VideoMetadata:
        if not video_path.exists():
            raise FileNotFoundError(f"Video file does not exist: {video_path}")

        ffprobe_bin = get_ffprobe_executable()
        
        cmd = [
            ffprobe_bin,
            "-v", "error",
            "-show_format",
            "-show_streams",
            "-print_format", "json",
            str(video_path)
        ]

        loop = asyncio.get_running_loop()

        def _run_ffprobe():
            import subprocess
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            return json.loads(res.stdout)

        try:
            probe_data = await loop.run_in_executor(None, _run_ffprobe)
        except Exception as e:
            logger.warning(f"ffprobe execution failed ({e}), falling back to file stats")
            file_size = video_path.stat().st_size
            return VideoMetadata(
                duration=0.0,
                file_size=file_size,
                title=video_path.name
            )

        format_info = probe_data.get("format", {})
        streams = probe_data.get("streams", [])
        
        duration = float(format_info.get("duration", 0.0))
        bitrate = int(format_info.get("bit_rate", 0)) if format_info.get("bit_rate") else None
        file_size = int(format_info.get("size", video_path.stat().st_size))

        video_stream = next((s for s in streams if s.get("codec_type") == "video"), {})
        audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), {})

        width = video_stream.get("width")
        height = video_stream.get("height")
        v_codec = video_stream.get("codec_name")
        a_codec = audio_stream.get("codec_name")

        # Parse FPS from r_frame_rate (e.g., "30/1" or "30000/1001")
        fps: Optional[float] = None
        r_frame_rate = video_stream.get("r_frame_rate")
        if r_frame_rate and "/" in r_frame_rate:
            try:
                num, den = map(float, r_frame_rate.split("/"))
                if den > 0:
                    fps = round(num / den, 2)
            except Exception:
                pass

        return VideoMetadata(
            duration=duration,
            width=width,
            height=height,
            fps=fps,
            codec_name=v_codec,
            audio_codec=a_codec,
            bit_rate=bitrate,
            file_size=file_size,
            title=video_path.stem
        )
