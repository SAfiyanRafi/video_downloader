import asyncio
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timezone
from app.models.job import JobStatus, AspectRatioOption, ExportPreset, PaddingMode, NamingTemplate, SegmentInfo
from app.models.workflow import WorkflowProfile
from app.services.branding.workflow_service import workflow_service
from app.services.storage.project_manager import project_manager, ProjectDirectoryStructure
from app.services.validation.quality_validator import quality_validator
from app.services.metadata.inspector import metadata_inspector
from app.services.reporting.summary_reporter import summary_reporter, ProcessingReport
from app.services.thumbnail.thumbnail_service import thumbnail_service
from app.services.download.youtube import YouTubeDownloader
from app.services.split.equal_split_service import EqualSplitService
from app.services.processing.ffmpeg_service import FFmpegService
from app.services.branding.branding_service import BrandingService
from app.services.branding.channel_service import channel_service
from app.services.zip.zip_service import ZipService

logger = logging.getLogger("yt_splitter")

class WorkflowStep:
    def __init__(self, name: str, description: str, enabled: bool = True):
        self.name = name
        self.description = description
        self.enabled = enabled

class WorkflowExecutionEngine:
    """
    Dynamic Workflow Execution Engine:
    Executes workflow steps dynamically in a configurable pipeline.
    Supports optional, conditional, and future custom step processors.
    """
    def __init__(self):
        self.downloader = YouTubeDownloader()
        self.equal_splitter = EqualSplitService()
        self.ffmpeg = FFmpegService()
        self.branding_service = BrandingService()
        self.zipper = ZipService()

    async def execute_job_pipeline(
        self,
        state,  # JobState instance
        update_progress_cb
    ) -> ProjectDirectoryStructure:
        start_time = time.time()
        job_id = state.job_id
        wf_id = getattr(state, "workflow_id", "shorts" if state.aspect_ratio == AspectRatioOption.V_9_16 else "longform")
        
        # Load workflow profile
        try:
            wf_profile = workflow_service.get_workflow(wf_id)
        except Exception:
            wf_profile = workflow_service.get_workflow("shorts")

        proj = project_manager.get_temp_project(job_id)

        # Build dynamic execution steps
        steps = [
            WorkflowStep("Pre-flight Validation", "Verifying system requirements and asset access"),
            WorkflowStep("Download", "Fetching highest quality source video streams"),
            WorkflowStep("Metadata Inspection", "Extracting video codecs, resolution, and fps"),
            WorkflowStep("Stream Split", "Losslessly splitting video into equal parts"),
            WorkflowStep("Channel Branding", "Applying intro & outro branding", enabled=wf_profile.allow_intro_outro and bool(state.channel)),
            WorkflowStep("Thumbnails", "Generating smart thumbnail candidates", enabled=wf_profile.enable_thumbnails),
            WorkflowStep("Quality Validation", "Verifying playability, audio, and duration"),
            WorkflowStep("ZIP Packaging", "Creating downloadable ZIP archive"),
            WorkflowStep("Summary Report", "Generating processing summary report"),
            WorkflowStep("Desktop Export", "Auto-exporting structured project to desktop")
        ]

        active_steps = [s for s in steps if s.enabled]
        total_steps = len(active_steps)

        # ----------------------------------------------------
        # Step 1: Pre-flight Validation
        # ----------------------------------------------------
        update_progress_cb(5.0, "Pre-flight asset & system validation...")
        startup_val = await quality_validator.validate_startup()
        if not startup_val.ffmpeg_available:
            raise RuntimeError(f"Pre-flight validation failed: {startup_val.issues}")

        # ----------------------------------------------------
        # Step 2: Download Source Video
        # ----------------------------------------------------
        update_progress_cb(15.0, "Downloading source video...")
        downloaded_video = proj.original / "original_video.mp4"

        def _dl_progress(percent: float, speed: str, eta: str):
            p = 15.0 + (percent * 0.35)
            update_progress_cb(p, f"Downloading: {percent:.1f}% ({speed})")

        meta = await self.downloader.download_video(
            url=state.url,
            output_path=downloaded_video,
            quality=state.quality,
            progress_callback=_dl_progress
        )
        state.metadata = meta

        # ----------------------------------------------------
        # Step 3: Metadata Inspection
        # ----------------------------------------------------
        update_progress_cb(50.0, "Inspecting video metadata...")
        inspection = await metadata_inspector.inspect_file(downloaded_video)
        logger.info(f"[Job {job_id}] Inspected video: {inspection.resolution}, {inspection.fps}fps, {inspection.video_codec}")

        # ----------------------------------------------------
        # Step 4: Stream-Copy Equal Splitting
        # ----------------------------------------------------
        update_progress_cb(55.0, f"Splitting video into {state.parts} equal parts...")
        segments = self.equal_splitter.calculate_split_points(meta.duration, state.parts)
        state.segments = segments

        def _split_cb(done: int, tot: int):
            frac = done / tot
            update_progress_cb(55.0 + (frac * 15.0), f"Splitting part {done}/{tot}...")

        generated_clip_paths = await self.ffmpeg.split_video(
            input_file=downloaded_video,
            output_dir=proj.split,
            segments=segments,
            progress_callback=_split_cb
        )
        final_clip_paths = generated_clip_paths

        # ----------------------------------------------------
        # Step 5: Channel Branding (If enabled)
        # ----------------------------------------------------
        if wf_profile.allow_intro_outro and state.channel:
            update_progress_cb(70.0, "Applying channel intro/outro branding...")
            profile = channel_service.get_channel(state.channel)
            root_dir = channel_service.root_dir

            intro_path = (root_dir / profile.intro) if profile.intro else None
            outro_path = (root_dir / profile.outro) if profile.outro else None
            prefix = profile.filename_prefix or profile.id

            branded_clip_paths = []
            total_clips = len(generated_clip_paths)
            today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

            for idx, raw_clip in enumerate(generated_clip_paths):
                part_num = idx + 1
                if state.naming_template == NamingTemplate.ORIGINAL_CLIP:
                    branded_filename = f"Clip_{part_num:02d}.mp4"
                elif state.naming_template == NamingTemplate.DATE_CHANNEL_PART:
                    branded_filename = f"{today_str}_{prefix}_Part_{part_num:02d}.mp4"
                else:
                    branded_filename = f"{prefix}_Part_{part_num:02d}.mp4"

                branded_output = proj.branded / branded_filename
                await self.branding_service.add_intro_outro(
                    clip_path=raw_clip,
                    output_path=branded_output,
                    intro_path=intro_path,
                    outro_path=outro_path,
                    aspect_ratio=state.aspect_ratio,
                    export_preset=state.export_preset,
                    padding_mode=state.padding_mode,
                    crop_fill=state.crop_fill
                )
                branded_clip_paths.append(branded_output)
                if idx < len(state.segments):
                    state.segments[idx].filename = f"Branded/{branded_filename}"

            final_clip_paths = branded_clip_paths
        else:
            # Copy to exports / update relative path
            for idx, raw_clip in enumerate(generated_clip_paths):
                exp_clip = proj.exports / raw_clip.name
                shutil.copy2(raw_clip, exp_clip)
                if idx < len(state.segments):
                    state.segments[idx].filename = f"Exports/{raw_clip.name}"

        # Copy final clips into Exports folder
        final_export_paths = []
        for clip in final_clip_paths:
            dst = proj.exports / clip.name
            if clip != dst:
                shutil.copy2(clip, dst)
            final_export_paths.append(dst)

        # ----------------------------------------------------
        # Step 6: Thumbnails (If enabled)
        # ----------------------------------------------------
        thumbnail_paths = []
        if wf_profile.enable_thumbnails and final_export_paths:
            update_progress_cb(85.0, "Generating smart thumbnail candidates...")
            try:
                thumbnail_paths = await thumbnail_service.generate_thumbnails(
                    video_path=final_export_paths[0],
                    output_dir=proj.thumbnails,
                    count=3
                )
            except Exception as te:
                logger.warning(f"[Job {job_id}] Thumbnail generation warning: {te}")

        # ----------------------------------------------------
        # Step 7: Quality Validation
        # ----------------------------------------------------
        update_progress_cb(90.0, "Verifying post-processing clip quality...")
        all_valid = True
        for clip in final_export_paths:
            v_res = await quality_validator.validate_exported_clip(clip)
            if not v_res.is_valid:
                all_valid = False
                logger.warning(f"[Job {job_id}] Quality validation warning for {clip.name}: {v_res.errors}")

        # ----------------------------------------------------
        # Step 8: ZIP Packaging
        # ----------------------------------------------------
        update_progress_cb(93.0, "Creating ZIP archive...")
        zip_output_path = proj.zip_dir / "video_parts.zip"
        await self.zipper.create_zip_archive(final_export_paths, zip_output_path)
        state.zip_filename = "ZIP/video_parts.zip"

        # ----------------------------------------------------
        # Step 9: Summary Report Generation
        # ----------------------------------------------------
        update_progress_cb(96.0, "Generating summary report...")
        total_exec_time = time.time() - start_time
        rep = ProcessingReport(
            job_id=job_id,
            workflow_id=wf_profile.id,
            channel_id=state.channel,
            url_or_file=state.url,
            total_duration_seconds=meta.duration,
            parts_count=state.parts,
            download_resolution=inspection.resolution,
            export_aspect_ratio=state.aspect_ratio.value,
            branding_applied=bool(state.channel and wf_profile.allow_intro_outro),
            subtitles_applied=wf_profile.enable_subtitles,
            thumbnails_generated_count=len(thumbnail_paths),
            zip_created=zip_output_path.exists(),
            quality_validated=all_valid,
            processing_time_seconds=total_exec_time,
            created_at=datetime.now(timezone.utc)
        )
        summary_reporter.generate_report(rep, proj.logs)

        # ----------------------------------------------------
        # Step 10: Auto-Export to Desktop Project Folder
        # ----------------------------------------------------
        update_progress_cb(98.0, "Auto-exporting project to desktop...")
        desktop_proj = project_manager.export_to_desktop(job_id)

        update_progress_cb(100.0, "Completed successfully!")
        return proj

workflow_execution_engine = WorkflowExecutionEngine()
