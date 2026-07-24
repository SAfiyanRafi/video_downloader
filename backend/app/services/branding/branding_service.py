import asyncio
import logging
from pathlib import Path
from typing import Optional
from app.services.processing.ffmpeg_service import get_ffmpeg_executable

logger = logging.getLogger("yt_splitter")

class BrandingService:
    """
    Independent service responsible for prepending an Intro and appending an Outro
    to a video clip using FFmpeg complex filter concatenation.
    """
    def __init__(self):
        self.ffmpeg_bin = get_ffmpeg_executable()

    async def add_intro_outro(
        self,
        clip_path: Path,
        output_path: Path,
        intro_path: Optional[Path] = None,
        outro_path: Optional[Path] = None
    ) -> Path:
        """
        Concatenates [Intro (if present)] + [Clip] + [Outro (if present)] into output_path.
        """
        if not clip_path.exists():
            raise FileNotFoundError(f"Input clip file not found: {clip_path}")

        # If no intro and no outro provided, simply copy clip to output_path
        if not intro_path and not outro_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(clip_path.read_bytes())
            return output_path

        inputs = []
        if intro_path and intro_path.exists():
            inputs.append(intro_path)
        
        inputs.append(clip_path)

        if outro_path and outro_path.exists():
            inputs.append(outro_path)

        count = len(inputs)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        cmd = [self.ffmpeg_bin, "-y"]
        for inp in inputs:
            cmd.extend(["-i", str(inp)])

        # Construct complex filter graph to standardize resolution, fps, and audio channels before concat
        filter_parts = []
        concat_inputs = []

        for idx in range(count):
            v_tag = f"v{idx}"
            a_tag = f"a{idx}"
            filter_parts.append(
                f"[{idx}:v]scale=1920:1080:force_original_aspect_ratio=decrease,"
                f"pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[{v_tag}];"
            )
            filter_parts.append(
                f"[{idx}:a]aformat=sample_rates=44100:channel_layouts=stereo[{a_tag}];"
            )
            concat_inputs.append(f"[{v_tag}][{a_tag}]")

        filter_graph = " ".join(filter_parts) + f" {''.join(concat_inputs)}concat=n={count}:v=1:a=1[outv][outa]"

        cmd.extend([
            "-filter_complex", filter_graph,
            "-map", "[outv]",
            "-map", "[outa]",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "128k",
            str(output_path)
        ])

        logger.info(f"Applying branding (Intro/Outro) to {clip_path.name} -> {output_path.name}")
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            err_msg = stderr.decode('utf-8', errors='ignore')
            logger.error(f"FFmpeg branding concatenation failed: {err_msg}")
            raise RuntimeError(f"Branding concatenation failed for clip '{clip_path.name}': {err_msg[:300]}")

        return output_path
