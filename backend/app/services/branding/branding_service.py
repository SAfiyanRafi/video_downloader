import asyncio
import logging
import subprocess
from pathlib import Path
from typing import Optional, List
from app.services.processing.ffmpeg_service import get_ffmpeg_executable
from app.services.metadata.ffprobe_service import FFprobeService

logger = logging.getLogger("yt_splitter")

class BrandingService:
    """
    Independent service responsible for prepending an Intro and appending an Outro
    to a video clip using FFmpeg complex filter concatenation and robust fallback.
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

        inputs: List[Path] = []
        if intro_path and intro_path.exists():
            inputs.append(intro_path)
        
        inputs.append(clip_path)

        if outro_path and outro_path.exists():
            inputs.append(outro_path)

        count = len(inputs)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Primary approach: FFmpeg complex filter concatenation
        cmd = [self.ffmpeg_bin, "-y"]
        for inp in inputs:
            cmd.extend(["-i", str(inp)])

        filter_parts = []
        concat_inputs = []

        for idx in range(count):
            v_tag = f"v{idx}"
            a_tag = f"a{idx}"
            
            filter_parts.append(
                f"[{idx}:v]scale=1280:720:force_original_aspect_ratio=decrease,"
                f"pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[{v_tag}];"
            )

            has_audio = await self._has_audio(inputs[idx])
            if has_audio:
                filter_parts.append(
                    f"[{idx}:a]aresample=44100,aformat=channel_layouts=stereo[{a_tag}];"
                )
            else:
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
            "-preset", "ultrafast",
            "-tune", "fastdecode",
            "-crf", "22",
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

        if process.returncode == 0 and output_path.exists() and output_path.stat().st_size > 0:
            return output_path

        err_msg = stderr.decode('utf-8', errors='ignore')
        logger.warning(f"Complex filter concatenation failed for {clip_path.name}: {err_msg[:300]}. Attempting fallback re-encode method...")

        # Fallback method: Pre-normalize inputs into temporary files then concat
        return await self._fallback_concat(inputs, output_path)

    async def _fallback_concat(self, inputs: List[Path], output_path: Path) -> Path:
        """
        Fallback concatenation method for unusual video formats.
        Normalizes inputs individually to temp TS files and concats.
        """
        temp_dir = output_path.parent / "_temp_branding"
        temp_dir.mkdir(parents=True, exist_ok=True)
        ts_files = []

        try:
            for idx, inp in enumerate(inputs):
                ts_file = temp_dir / f"temp_{idx}.ts"
                has_audio = await self._has_audio(inp)

                cmd = [
                    self.ffmpeg_bin, "-y",
                    "-i", str(inp)
                ]

                if not has_audio:
                    cmd.extend(["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo"])

                cmd.extend([
                    "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30",
                    "-c:v", "libx264", "-preset", "ultrafast",
                    "-c:a", "aac", "-ar", "44100", "-ac", "2",
                    "-f", "mpegts",
                    str(ts_file)
                ])

                proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
                await proc.communicate()
                ts_files.append(ts_file)

            # Concat demuxer string
            concat_str = "|".join([str(f) for f in ts_files])
            final_cmd = [
                self.ffmpeg_bin, "-y",
                "-i", f"concat:{concat_str}",
                "-c", "copy",
                str(output_path)
            ]

            proc = await asyncio.create_subprocess_exec(*final_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            _, err = await proc.communicate()

            if proc.returncode != 0:
                raise RuntimeError(f"Fallback branding failed: {err.decode('utf-8', errors='ignore')[:300]}")

            return output_path
        finally:
            # Cleanup temp files
            for f in ts_files:
                if f.exists():
                    f.unlink(missing_ok=True)
            if temp_dir.exists():
                try:
                    temp_dir.rmdir()
                except Exception:
                    pass
