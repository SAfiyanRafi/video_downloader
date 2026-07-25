import asyncio
import uuid
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

from app.models.job import (
    JobStatus, JobResponse, JobDownloadsResponse, QualityOption, AspectRatioOption,
    ExportPreset, PaddingMode, NamingTemplate
)
from app.models.video import VideoMetadata, SegmentInfo
from app.services.download.youtube import YouTubeDownloader
from app.services.metadata.ffprobe_service import FFprobeService
from app.services.split.equal_split_service import EqualSplitService
from app.services.processing.ffmpeg_service import FFmpegService
from app.services.branding.channel_service import ChannelService
from app.services.branding.branding_service import BrandingService
from app.services.storage.local_storage import LocalStorageProvider
from app.services.zip.zip_service import ZipService
from app.services.workflow.workflow_executor import workflow_execution_engine
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
        export_preset: ExportPreset = ExportPreset.HIGH,
        padding_mode: PaddingMode = PaddingMode.BLACK_BARS,
        naming_template: NamingTemplate = NamingTemplate.CHANNEL_PART,
        crop_fill: bool = False,
        channel: Optional[str] = None
    ):
        self.job_id = job_id
        self.url = url
        self.parts = parts
        self.quality = quality
        self.aspect_ratio = aspect_ratio
        self.export_preset = export_preset
        self.padding_mode = padding_mode
        self.naming_template = naming_template
        self.crop_fill = crop_fill
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
        export_preset: ExportPreset = ExportPreset.HIGH,
        padding_mode: PaddingMode = PaddingMode.BLACK_BARS,
        naming_template: NamingTemplate = NamingTemplate.CHANNEL_PART,
        crop_fill: bool = False,
        channel: Optional[str] = None
    ) -> JobResponse:
        # Validate channel profile if specified
        if channel:
            self.channel_service.validate_channel_assets(channel)

        job_id = str(uuid.uuid4())[:8]
        state = JobState(
            job_id, url, parts, quality, aspect_ratio,
            export_preset, padding_mode, naming_template, crop_fill, channel
        )
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
            metadata=state.metadata,
            url=state.url,
            parts=state.parts,
            channel=state.channel
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

        def _update_cb(pct: float, msg: str):
            state.progress = pct
            state.message = msg
            if pct < 15.0:
                state.status = JobStatus.DOWNLOADING
            elif pct < 50.0:
                state.status = JobStatus.ANALYZING
            elif pct < 70.0:
                state.status = JobStatus.SPLITTING
            elif pct < 85.0:
                state.status = JobStatus.BRANDING
            elif pct < 95.0:
                state.status = JobStatus.ZIPPING
            else:
                state.status = JobStatus.COMPLETED
            state.updated_at = datetime.now(timezone.utc)

        try:
            state.status = JobStatus.DOWNLOADING
            state.message = "Initializing dynamic workflow engine..."
            state.updated_at = datetime.now(timezone.utc)

            proj = await workflow_execution_engine.execute_job_pipeline(
                state=state,
                update_progress_cb=_update_cb
            )

            state.status = JobStatus.COMPLETED
            state.progress = 100.0
            state.message = "Workflow pipeline processing completed successfully"
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
