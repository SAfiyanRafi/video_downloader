import asyncio
import logging
from pathlib import Path
from typing import Optional
from app.models.job import AspectRatioOption, ExportPreset, PaddingMode
from app.services.processing.ffmpeg_service import get_ffmpeg_executable
from app.utils.process_utils import _exec_subprocess

logger = logging.getLogger("yt_splitter")

def get_video_filter(
    aspect_ratio: AspectRatioOption,
    padding_mode: PaddingMode = PaddingMode.BLACK_BARS,
    crop_fill: bool = False
) -> str:
    val = aspect_ratio.value if isinstance(aspect_ratio, AspectRatioOption) else str(aspect_ratio)
    p_mode = padding_mode.value if isinstance(padding_mode, PaddingMode) else str(padding_mode)

    dim_map = {
        "9:16": (1080, 1920),
        "16:9": (1920, 1080),
        "1:1": (1080, 1080),
        "4:5": (1080, 1350),
    }

    tw, th = dim_map.get(val, (1280, 720))

    if crop_fill:
        return f"scale={tw}:{th}:force_original_aspect_ratio=increase,crop={tw}:{th},setsar=1"

    if p_mode == "blurred" and val != "original":
        return (
            f"split[vfg][vbg];"
            f"[vbg]scale={tw}:{th}:force_original_aspect_ratio=increase,crop={tw}:{th},boxblur=15:5[bg];"
            f"[vfg]scale={tw}:{th}:force_original_aspect_ratio=decrease[fg];"
            f"[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1"
        )
    else:
        return f"scale={tw}:{th}:force_original_aspect_ratio=decrease,pad={tw}:{th}:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1"

class AspectService:
    """
    High-speed ultra-fast aspect ratio transformation service.
    Uses -preset ultrafast, -tune zerolatency, and multi-threading for maximum processing speed.
    """
    def __init__(self):
        self.ffmpeg_bin = get_ffmpeg_executable()

    async def transform_aspect_ratio(
        self,
        clip_path: Path,
        output_path: Path,
        aspect_ratio: AspectRatioOption = AspectRatioOption.ORIGINAL,
        padding_mode: PaddingMode = PaddingMode.BLACK_BARS,
        crop_fill: bool = False
    ) -> Path:
        if not clip_path.exists():
            raise FileNotFoundError(f"Input clip file not found: {clip_path}")

        # If aspect ratio is original and no crop fill, copy lossless clip instantly (0.01 sec)
        if aspect_ratio == AspectRatioOption.ORIGINAL and not crop_fill:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(clip_path.read_bytes())
            return output_path

        output_path.parent.mkdir(parents=True, exist_ok=True)
        v_filter = get_video_filter(aspect_ratio, padding_mode, crop_fill)

        cmd = [
            self.ffmpeg_bin, "-y",
            "-i", str(clip_path),
            "-vf", v_filter,
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-tune", "zerolatency",
            "-threads", "0",
            "-crf", "23",
            "-c:a", "copy",
            str(output_path)
        ]

        logger.info(f"[AspectService] Fast transform ({aspect_ratio.value}) -> {output_path.name}")
        returncode, _, stderr = await asyncio.to_thread(_exec_subprocess, cmd)

        if returncode == 0 and output_path.exists() and output_path.stat().st_size > 0:
            return output_path

        raise RuntimeError(f"Aspect ratio transformation failed: {stderr[:300]}")
