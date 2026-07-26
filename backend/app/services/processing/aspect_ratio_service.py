import asyncio
import logging
from pathlib import Path
from typing import Tuple, Optional, Callable

from app.models.job import AspectRatioOption, PaddingMode
from app.services.processing.ffmpeg_service import get_ffmpeg_executable
from app.utils.process_utils import _exec_subprocess

logger = logging.getLogger("yt_splitter")

class AspectRatioService:
    """
    High-performance Aspect Ratio transformation engine with multi-core CPU optimization.
    """

    def __init__(self):
        self.ffmpeg_bin = get_ffmpeg_executable()

    async def apply_aspect_ratio(
        self,
        clip_path: Path,
        output_path: Path,
        aspect_ratio: AspectRatioOption = AspectRatioOption.ORIGINAL,
        padding_mode: PaddingMode = PaddingMode.BLURRED,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> Path:
        """
        Applies aspect ratio transformation to a video clip.
        If aspect_ratio == ORIGINAL, performs a 0-second 100% lossless copy (-c copy).
        Otherwise uses multi-threaded ultrafast re-encoding (-preset ultrafast -threads 0 -tune fastdecode).
        """
        if not clip_path.exists():
            raise FileNotFoundError(f"Input clip not found at {clip_path}")

        # If ORIGINAL, skip encoding entirely and perform lossless copy
        if aspect_ratio == AspectRatioOption.ORIGINAL:
            logger.info(f"[AspectRatioService] Aspect ratio is ORIGINAL. Performing 0-second lossless copy for {clip_path.name}")
            cmd = [
                self.ffmpeg_bin, "-y",
                "-i", str(clip_path.resolve()),
                "-c", "copy",
                str(output_path.resolve())
            ]
            returncode, _, err = await asyncio.to_thread(_exec_subprocess, cmd)
            if returncode != 0:
                raise RuntimeError(f"Lossless clip copy failed: {err[:300]}")
            return output_path

        # Determine target resolution
        if aspect_ratio == AspectRatioOption.V_9_16:
            target_w, target_h = 1080, 1920
        elif aspect_ratio == AspectRatioOption.H_16_9:
            target_w, target_h = 1920, 1080
        elif aspect_ratio == AspectRatioOption.S_1_1:
            target_w, target_h = 1080, 1080
        else:
            target_w, target_h = 1080, 1920

        logger.info(f"[AspectRatioService] Transforming aspect ratio ({aspect_ratio.value}, {target_w}x{target_h}) on {clip_path.name} with 16-thread ultrafast preset...")

        if padding_mode == PaddingMode.BLACK_BARS:
            filter_complex = f"scale={target_w}:{target_h}:force_original_aspect_ratio=decrease,pad={target_w}:{target_h}:(ow-iw)/2:(oh-ih)/2:black"
        else:
            # BLURRED background padding
            filter_complex = (
                f"[0:v]scale={target_w}:{target_h}:force_original_aspect_ratio=increase,crop={target_w}:{target_h},boxblur=20:5[bg];"
                f"[0:v]scale={target_w}:{target_h}:force_original_aspect_ratio=decrease[fg];"
                f"[bg][fg]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2"
            )

        cmd = [
            self.ffmpeg_bin, "-y",
            "-i", str(clip_path.resolve()),
            "-filter_complex", filter_complex,
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-threads", "0",
            "-tune", "fastdecode",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "192k",
            str(output_path.resolve())
        ]

        returncode, _, err = await asyncio.to_thread(_exec_subprocess, cmd)
        if returncode != 0:
            raise RuntimeError(f"Aspect ratio transformation failed: {err[-300:]}")

        return output_path
