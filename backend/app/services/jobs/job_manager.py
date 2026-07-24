import asyncio
import uuid
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

from app.models.job import JobStatus, JobResponse, JobDownloadsResponse, QualityOption, AspectRatioOption
from app.models.video import VideoMetadata, SegmentInfo
from app.services.download.youtube import YouTubeDownloader
from app.services.metadata.ffprobe_service import FFprobeService
from app.services.split.equal_split_service import EqualSplitService
from app.services.processing.ffmpeg_service import FFmpegService
from app.services.branding.channel_service import ChannelService
from app.services.branding.branding_service import BrandingService
from app.services.storage.local_storage import LocalStorageProvider
from app.services.zip.zip_service import ZipService
from app.core.config import settings

logger = logging.getLogger("yt_splitter")

class JobState:
    def __init__(
        self,
        job_id: str,
        url: str,
        parts: int,
        quality: QualityOption,
        aspect_ratio: AspectRatioOption = AspectRatioOption.ORIGINAL,
        channel: Optional[str] = None
    ):
        self.job_id = job_id
        self.url = url
        self.parts = parts
        self.quality = quality
        self.aspect_ratio = aspect_ratio
        self.channel = channel
        self.status = JobStatus.PENDING
        self.progress = 0.0
        self.message = "Job queued"
        self.error: Optional[str] = None
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
        self.metadata: Optional[VideoMetadata] = None
        self.segments: list[SegmentInfo] = []
        self.zip_filename: Optional[str] = None
        self.task: Optional[asyncio.Task] = None

class JobManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(JobManager, cls).__new__(cls)
            cls._instance._init_manager()
        return cls._instance

    def _init_manager(self):
        self.jobs: Dict[str, JobState] = {}
        self.storage = LocalStorageProvider()
        self.downloader = YouTubeDownloader()
        self.ffprobe = FFprobeService()
        self.splitter = EqualSplitService()
        self.ffmpeg = FFmpegService()
        self.channel_service = ChannelService()
        self.branding_service = BrandingService()
        self.zipper = ZipService()

    def create_job(
        self,
        url: str,
        parts: int,
        quality: QualityOption,
        aspect_ratio: AspectRatioOption = AspectRatioOption.ORIGINAL,
        channel: Optional[str] = None
    ) -> JobResponse:
        # Validate channel profile if specified
        if channel:
            self.channel_service.validate_channel_assets(channel)

        job_id = str(uuid.uuid4())[:8]
        state = JobState(job_id, url, parts, quality, aspect_ratio, channel)
        self.jobs[job_id] = state

        # Schedule background processing task and store task reference
        state.task = asyncio.create_task(self._process_job(job_id))

        return self.get_job_response(job_id)

    def cancel_job(self, job_id: str) -> JobResponse:
        state = self.jobs.get(job_id)
        if not state:
            raise KeyError(f"Job ID {job_id} not found")

        if state.task and not state.task.done():
            state.task.cancel()

        state.status = JobStatus.FAILED
        state.error = "Job cancelled by user"
        state.message = "Cancelled by user"
        state.updated_at = datetime.now(timezone.utc)

        # Purge temporary files
        self.storage.cleanup_job(job_id)
        logger.info(f"Job {job_id} was cancelled by user and cleaned up.")

        return self.get_job_response(job_id)

    def get_job_state(self, job_id: str) -> Optional[JobState]:
        return self.jobs.get(job_id)

    def get_job_response(self, job_id: str) -> JobResponse:
        state = self.jobs.get(job_id)
        if not state:
            raise KeyError(f"Job ID {job_id} not found")
        return JobResponse(
            job_id=state.job_id,
            status=state.status,
            progress=round(state.progress, 1),
            message=state.message,
            created_at=state.created_at,
            updated_at=state.updated_at,
            error=state.error,
            metadata=state.metadata
        )

    def get_job_downloads(self, job_id: str) -> JobDownloadsResponse:
        state = self.jobs.get(job_id)
        if not state:
            raise KeyError(f"Job ID {job_id} not found")

        zip_url = None
        if state.zip_filename:
            zip_url = self.storage.get_download_url(job_id, state.zip_filename)

        clips_with_urls: list[SegmentInfo] = []
        for seg in state.segments:
            seg_copy = seg.model_copy()
            seg_copy.download_url = self.storage.get_download_url(job_id, seg.filename)
            clips_with_urls.append(seg_copy)

        return JobDownloadsResponse(
            job_id=state.job_id,
            status=state.status,
            zip_url=zip_url,
            clips=clips_with_urls,
            metadata=state.metadata
        )

    async def _process_job(self, job_id: str):
        state = self.jobs.get(job_id)
        if not state:
            return

        job_dir = self.storage.get_job_directory(job_id)

        try:
            # 1. DOWNLOADING STAGE (0% -> 40%)
            state.status = JobStatus.DOWNLOADING
            state.message = "Downloading video from YouTube..."
            state.updated_at = datetime.now(timezone.utc)

            def _download_progress(pct: float):
                # Scale download progress into 0-40% total job progress
                state.progress = (pct / 100.0) * 40.0
                state.updated_at = datetime.now(timezone.utc)

            downloaded_video = await self.downloader.download(
                source=state.url,
                output_dir=job_dir,
                quality=state.quality,
                progress_callback=_download_progress
            )
            state.progress = 40.0

            # 2. ANALYZING METADATA STAGE (40% -> 50%)
            state.status = JobStatus.ANALYZING
            state.message = "Analyzing video metadata and split markers..."
            state.progress = 45.0
            state.updated_at = datetime.now(timezone.utc)

            metadata = await self.ffprobe.get_metadata(downloaded_video)
            state.metadata = metadata

            if metadata.duration <= 0:
                raise ValueError("Could not determine valid video duration")

            if metadata.duration > settings.MAX_VIDEO_DURATION_SECONDS:
                raise ValueError(f"Video duration ({metadata.duration:.0f}s) exceeds maximum allowed ({settings.MAX_VIDEO_DURATION_SECONDS}s)")

            # 3. CALCULATE SPLITS & SPLITTING STAGE (50% -> 85%)
            state.status = JobStatus.SPLITTING
            state.message = f"Splitting video into {state.parts} equal segments..."
            state.progress = 50.0
            state.updated_at = datetime.now(timezone.utc)

            segments = self.splitter.calculate_splits(metadata.duration, state.parts)
            state.segments = segments

            def _split_progress(done: int, total: int):
                # Scale splitting progress into 50% -> 85% range
                frac = done / total
                state.progress = 50.0 + (frac * 35.0)
                state.message = f"Splitting clip {done}/{total}..."
                state.updated_at = datetime.now(timezone.utc)

            clips_dir = job_dir / "clips"
            generated_clip_paths = await self.ffmpeg.split_video(
                input_file=downloaded_video,
                output_dir=clips_dir,
                segments=segments,
                progress_callback=_split_progress
            )

            final_clip_paths = generated_clip_paths

            # 4. BRANDING & DIMENSION TRANSFORMATION STAGE (70% -> 85%)
            if state.channel or state.aspect_ratio != AspectRatioOption.ORIGINAL:
                state.status = JobStatus.BRANDING
                state.message = f"Applying aspect ratio ({state.aspect_ratio.value}) and branding..."
                state.progress = 70.0
                state.updated_at = datetime.now(timezone.utc)

                intro_path = None
                outro_path = None
                prefix = "Clip"

                if state.channel:
                    profile = self.channel_service.get_channel(state.channel)
                    root_dir = self.channel_service.root_dir
                    intro_path = (root_dir / profile.intro) if profile.intro else None
                    outro_path = (root_dir / profile.outro) if profile.outro else None
                    prefix = profile.filename_prefix or profile.id

                branded_dir = job_dir / "branded"
                branded_clip_paths = []
                total_clips = len(generated_clip_paths)

                for idx, raw_clip in enumerate(generated_clip_paths):
                    part_num = idx + 1
                    branded_filename = f"{prefix}_Part_{part_num:02d}.mp4"
                    branded_output = branded_dir / branded_filename

                    await self.branding_service.add_intro_outro(
                        clip_path=raw_clip,
                        output_path=branded_output,
                        intro_path=intro_path,
                        outro_path=outro_path,
                        aspect_ratio=state.aspect_ratio
                    )
                    branded_clip_paths.append(branded_output)

                    # Update SegmentInfo records
                    if idx < len(state.segments):
                        state.segments[idx].filename = f"branded/{branded_filename}"

                    # Update progress
                    frac = part_num / total_clips
                    state.progress = 70.0 + (frac * 15.0)
                    state.message = f"Processing clip {part_num}/{total_clips} ({state.aspect_ratio.value})..."
                    state.updated_at = datetime.now(timezone.utc)

                # Cleanup intermediate raw split clips to save disk space
                try:
                    for raw_c in generated_clip_paths:
                        if raw_c.exists():
                            raw_c.unlink()
                except Exception as clean_err:
                    logger.warning(f"Failed to cleanup intermediate split clips: {clean_err}")

                final_clip_paths = branded_clip_paths
            else:
                # Update segment filenames relative to job directory
                for seg in state.segments:
                    seg.filename = f"clips/{seg.filename}"

            # 5. ZIPPING STAGE (85% -> 99%)
            state.status = JobStatus.ZIPPING
            state.message = "Creating ZIP archive of video parts..."
            state.progress = 90.0
            state.updated_at = datetime.now(timezone.utc)

            zip_output_path = job_dir / "video_parts.zip"
            await self.zipper.create_zip_archive(final_clip_paths, zip_output_path)
            state.zip_filename = "video_parts.zip"

            # 6. COMPLETED
            state.status = JobStatus.COMPLETED
            state.progress = 100.0
            state.message = "Video splitting and branding completed successfully"
            state.updated_at = datetime.now(timezone.utc)
            logger.info(f"Job {job_id} successfully completed.")

        except Exception as e:
            raw_err = str(e)
            # Strip ANSI terminal codes (e.g. \x1b[0;31m)
            clean_err = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', raw_err).strip()
            
            # Humanize common YouTube / yt-dlp error patterns
            if "This video is not available" in clean_err or "Video unavailable" in clean_err:
                friendly_err = "The requested YouTube video is unavailable (it may be private, deleted, or region-restricted)."
            elif "Private video" in clean_err:
                friendly_err = "This YouTube video is private and cannot be accessed."
            elif "Sign in to confirm your age" in clean_err:
                friendly_err = "This YouTube video is age-restricted and requires authentication."
            elif "is not a valid URL" in clean_err:
                friendly_err = "Invalid YouTube URL format."
            else:
                friendly_err = clean_err if clean_err else f"{type(e).__name__}: {str(e)}"

            logger.error(f"Job {job_id} failed: {clean_err or repr(e)}", exc_info=True)
            state.status = JobStatus.FAILED
            state.error = friendly_err
            state.message = f"Failed: {friendly_err}"
            state.updated_at = datetime.now(timezone.utc)

    async def auto_cleanup_loop(self):
        """Periodic background task that cleans up expired job directories."""
        while True:
            await asyncio.sleep(settings.CLEANUP_INTERVAL_MINUTES * 60)
            now = datetime.now(timezone.utc)
            to_delete = []
            for j_id, state in list(self.jobs.items()):
                age_minutes = (now - state.created_at).total_seconds() / 60.0
                if age_minutes >= settings.JOB_EXPIRATION_MINUTES:
                    to_delete.append(j_id)

            for j_id in to_delete:
                logger.info(f"Auto-cleaning expired job: {j_id}")
                self.storage.cleanup_job(j_id)
                self.jobs.pop(j_id, None)

job_manager = JobManager()
