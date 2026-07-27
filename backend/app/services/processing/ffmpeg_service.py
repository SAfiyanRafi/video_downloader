import asyncio
import logging
from pathlib import Path
from typing import Callable, List, Optional
from app.models.video import SegmentInfo
from app.utils.ffmpeg_finder import get_ffmpeg_executable

logger = logging.getLogger("yt_splitter")

class FFmpegService:
    """
    Executes video splitting using FFmpeg stream copy without re-encoding.
    Isolated from downloading or source-specific logic.
    """

    async def split_video(
        self,
        input_file: Path,
        output_dir: Path,
        segments: List[SegmentInfo],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[Path]:
        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")

        output_dir.mkdir(parents=True, exist_ok=True)
        ffmpeg_bin = get_ffmpeg_executable()
        generated_clips: List[Path] = []
        total = len(segments)

        loop = asyncio.get_running_loop()

        for idx, segment in enumerate(segments):
            clip_path = output_dir / segment.filename
            
            # Fast stream copy command using -ss before -i for fast seek
            cmd = [
                ffmpeg_bin,
                "-y",
                "-ss", str(segment.start_time),
                "-to", str(segment.end_time),
                "-i", str(input_file),
                "-map", "0:v:0",
                "-map", "0:a:0?",
                "-c:v", "copy",
                "-c:a", "copy",
                "-avoid_negative_ts", "make_zero",
                "-movflags", "+faststart",
                str(clip_path)
            ]

            def _run_clip_cmd(c=cmd):
                import subprocess
                subprocess.run(c, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

            try:
                await loop.run_in_executor(None, _run_clip_cmd)
            except Exception as e:
                logger.warning(f"Fast copy failed for segment {segment.part_number} ({e}), attempting fallback re-encode mode")
                # Fallback to re-encode if keyframe copy boundary fails
                fallback_cmd = [
                    ffmpeg_bin,
                    "-y",
                    "-ss", str(segment.start_time),
                    "-to", str(segment.end_time),
                    "-i", str(input_file),
                    "-map", "0:v:0",
                    "-map", "0:a:0?",
                    "-c:v", "libx264",
                    "-preset", "ultrafast",
                    "-pix_fmt", "yuv420p",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-movflags", "+faststart",
                    str(clip_path)
                ]
                def _run_fallback(fc=fallback_cmd):
                    import subprocess
                    subprocess.run(fc, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                await loop.run_in_executor(None, _run_fallback)

            generated_clips.append(clip_path)

            if progress_callback:
                progress_callback(idx + 1, total)

        return generated_clips
