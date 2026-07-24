import asyncio
import logging
from pathlib import Path
from typing import Optional
from app.services.processing.ffmpeg_service import get_ffmpeg_executable
from app.services.metadata.ffprobe_service import FFprobeService

logger = logging.getLogger("yt_splitter")

class BrandingService:
    """
    Independent service responsible for prepending an Intro and appending an Outro
    to a video clip using FFmpeg complex filter concatenation.
    """
    def __init__(self):
        self.ffmpeg_bin = get_ffmpeg_executable()
        self.ffprobe_service = FFprobeService()

    async def _has_audio(self, video_path: Path) -> bool:
        try:
            meta = await self.ffprobe_service.get_metadata(video_path)
            return meta.audio_codec is not None
        except Exception:
            return True

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
            
            # Video stream filter
            filter_parts.append(
                f"[{idx}:v]scale=1920:1080:force_original_aspect_ratio=decrease,"
                f"pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[{v_tag}];"
            )

            # Audio stream filter with robust fallback
            has_audio = await self._has_audio(inputs[idx])
            if has_audio:
                filter_parts.append(
                    f"[{idx}:a]aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo[{a_tag}];"
                )
            else:
                # Generate silent audio track if input lacks audio stream
                filter_parts.append(
                    f"anullsrc=r=44100:cl=stereo[{a_tag}];"
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
