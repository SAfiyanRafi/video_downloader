import uuid
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timezone
from app.models.studio import StudioJobRequest, StudioJobResponse, SubtitleMode
from app.services.studio.subtitle_service import SubtitleService
from app.services.studio.audio_service import AudioProcessingService
from app.services.processing.ffmpeg_service import get_ffmpeg_executable
from app.utils.process_utils import _exec_subprocess
from app.core.config import settings

logger = logging.getLogger("yt_splitter")

class StudioJobState:
    def __init__(self, job_id: str, request: StudioJobRequest):
        self.job_id = job_id
        self.request = request
        self.video_name = Path(request.video_path).name
        self.status = "PENDING"
        self.progress = 0.0
        self.message = "Job queued in Creator Studio"
        self.output_video_path: Optional[str] = None
        self.srt_path: Optional[str] = None
        self.error: Optional[str] = None
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
        self.task: Optional[asyncio.Task] = None

class StudioManager:
    def __init__(self):
        self.jobs: Dict[str, StudioJobState] = {}
        self.subtitle_service = SubtitleService()
        self.audio_service = AudioProcessingService()
        self.ffmpeg_bin = get_ffmpeg_executable()
        self.export_dir = settings.DEFAULT_DOWNLOAD_DIR / "CreatorStudio_Exports"
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def create_studio_job(self, request: StudioJobRequest) -> StudioJobResponse:
        input_file = Path(request.video_path)
        if not input_file.exists():
            raise FileNotFoundError(f"Input video file not found at {input_file}")

        job_id = str(uuid.uuid4())[:8]
        state = StudioJobState(job_id, request)
        self.jobs[job_id] = state

        # Launch background processing worker
        state.task = asyncio.create_task(self._process_studio_job(job_id))
        return self._to_response(state)

    def get_studio_job(self, job_id: str) -> StudioJobResponse:
        state = self.jobs.get(job_id)
        if not state:
            raise KeyError(f"Studio Job '{job_id}' not found")
        return self._to_response(state)

    def list_studio_jobs(self) -> List[StudioJobResponse]:
        return [self._to_response(s) for s in self.jobs.values()]

    def scan_watch_folder(self) -> List[str]:
        """Scans the default download directory for supported video files."""
        watch_dir = settings.DEFAULT_DOWNLOAD_DIR
        found = []
        if watch_dir.exists():
            for p in watch_dir.glob("**/*"):
                if p.is_file() and p.suffix.lower() in [".mp4", ".mov", ".mkv"]:
                    # Skip files already in CreatorStudio_Exports
                    if "CreatorStudio_Exports" not in p.parts:
                        found.append(str(p.resolve()))
        return sorted(found)

    async def _process_studio_job(self, job_id: str):
        state = self.jobs.get(job_id)
        if not state:
            return

        req = state.request
        input_video = Path(req.video_path)
        job_dir = settings.TEMP_DIR / "studio" / job_id
        job_dir.mkdir(parents=True, exist_ok=True)

        try:
            input_video = Path(req.video_path).resolve()
            if not input_video.exists():
                raise FileNotFoundError(f"Input video file not found at {input_video}")

            # 1. AUDIO EXTRACTION & SUBTITLE GENERATION (0% -> 40%)
            state.status = "PROCESSING"
            state.progress = 10.0
            state.message = "Extracting audio track for AI transcription..."
            state.updated_at = datetime.now(timezone.utc)

            wav_path = job_dir / "audio.wav"
            await self.subtitle_service.extract_audio(input_video, wav_path)

            ass_path = None
            srt_path = None

            if req.enable_subtitles:
                state.progress = 25.0
                state.message = f"Running Whisper AI transcription ({req.whisper_model})..."
                state.updated_at = datetime.now(timezone.utc)

                segments = await self.subtitle_service.generate_subtitles(wav_path, model_size=req.whisper_model)
                
                # Generate SRT
                srt_file = job_dir / f"{input_video.stem}.srt"
                self.subtitle_service.export_srt(segments, srt_file)
                srt_path = srt_file

                # Copy SRT to Export directory
                export_srt = self.export_dir / f"{input_video.stem}_subtitles.srt"
                export_srt.write_bytes(srt_file.read_bytes())
                state.srt_path = str(export_srt.resolve())

                # Generate ASS for burning in
                ass_file = job_dir / "subtitles.ass"
                self.subtitle_service.export_ass(segments, req.subtitle_preset, ass_file)
                ass_path = ass_file

            # 2. AUDIO ENHANCEMENT & NORMALIZATION (40% -> 60%)
            state.progress = 50.0
            state.message = "Applying audio loudness normalization & pitch adjustment..."
            state.updated_at = datetime.now(timezone.utc)

            audio_filter = self.audio_service.get_audio_filter_graph(
                normalize=req.normalize_audio,
                target_lufs=req.target_lufs,
                pitch_semitones=req.pitch_semitones
            )

            # 3. VIDEO RENDERING & SUBTITLE BURN-IN (60% -> 95%)
            state.progress = 65.0
            state.message = "Rendering enhanced video with styled subtitles..."
            state.updated_at = datetime.now(timezone.utc)

            output_filename = f"{input_video.stem}_Enhanced.mp4"
            output_video = self.export_dir / output_filename

            cmd = [self.ffmpeg_bin, "-y", "-i", str(input_video)]

            vf_filters = []
            if req.enable_subtitles and req.subtitle_mode in [SubtitleMode.BURNED_IN, SubtitleMode.BOTH] and ass_path:
                # Escape Windows path backslashes and colon for FFmpeg ass filter
                clean_ass_path = str(ass_path.resolve()).replace("\\", "/").replace(":", "\\:")
                vf_filters.append(f"ass='{clean_ass_path}'")

            if vf_filters:
                cmd.extend(["-vf", ",".join(vf_filters)])

            if audio_filter:
                cmd.extend(["-af", audio_filter])

            cmd.extend([
                "-map", "0:v:0",
                "-map", "0:a:0?",
                "-c:v", "libx264",
                "-preset", "veryfast",
                "-crf", "18",
                "-pix_fmt", "yuv420p",
                "-c:a", "aac",
                "-b:a", "256k",
                "-movflags", "+faststart",
                str(output_video)
            ])

            logger.info(f"[Studio Job {job_id}] Rendering enhanced video -> {output_video.name}...")
            returncode, _, err = await asyncio.to_thread(_exec_subprocess, cmd)

            if returncode != 0:
                err_lines = [line for line in err.splitlines() if line.strip()]
                tail_err = "\n".join(err_lines[-10:]) if err_lines else err[:300]
                raise RuntimeError(f"FFmpeg render failed:\n{tail_err}")

            state.output_video_path = str(output_video.resolve())

            # 4. COMPLETED (100%)
            state.status = "COMPLETED"
            state.progress = 100.0
            state.message = f"Creator Studio processing completed! Saved to {output_video.name}"
            state.updated_at = datetime.now(timezone.utc)
            logger.info(f"[Studio Job {job_id}] Successfully completed.")

        except Exception as e:
            logger.error(f"[Studio Job {job_id}] Failed: {e}", exc_info=True)
            state.status = "FAILED"
            state.error = str(e)
            state.message = f"Processing failed: {e}"
            state.updated_at = datetime.now(timezone.utc)

    def _to_response(self, state: StudioJobState) -> StudioJobResponse:
        return StudioJobResponse(
            job_id=state.job_id,
            video_name=state.video_name,
            status=state.status,
            progress=round(state.progress, 1),
            message=state.message,
            output_video_path=state.output_video_path,
            srt_path=state.srt_path,
            created_at=state.created_at,
            updated_at=state.updated_at,
            error=state.error
        )

studio_manager = StudioManager()
