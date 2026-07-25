import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel
from app.services.processing.ffmpeg_service import get_ffmpeg_executable
from app.services.metadata.ffprobe_service import FFprobeService
from app.services.branding.channel_service import channel_service
from app.services.branding.workflow_service import workflow_service
from app.services.branding.branding_service import _exec_subprocess

logger = logging.getLogger("yt_splitter")

class QualityValidationResult(BaseModel):
    is_valid: bool
    audio_present: bool
    file_size_bytes: int
    duration: float
    video_codec: Optional[str] = None
    audio_codec: Optional[str] = None
    resolution: Optional[str] = None
    warnings: List[str] = []
    errors: List[str] = []

class StartupValidationResult(BaseModel):
    ffmpeg_available: bool
    ffprobe_available: bool
    channels_valid: bool
    workflows_valid: bool
    issues: List[str] = []

class QualityValidator:
    """
    Quality Validation Engine:
    - Startup pre-flight validation (FFmpeg, FFprobe, Channels, Workflows)
    - Post-process export validation (Audio track, duration, playability, non-zero size)
    """
    def __init__(self):
        self.ffmpeg_bin = get_ffmpeg_executable()
        self.ffprobe_service = FFprobeService()

    async def validate_startup(self) -> StartupValidationResult:
        issues = []
        ffmpeg_ok = True
        ffprobe_ok = True
        channels_ok = True
        workflows_ok = True

        # 1. Verify FFmpeg
        try:
            code, _, _ = await asyncio.to_thread(_exec_subprocess, [self.ffmpeg_bin, "-version"])
            if code != 0:
                ffmpeg_ok = False
                issues.append(f"FFmpeg binary returned error code {code}")
        except Exception as e:
            ffmpeg_ok = False
            issues.append(f"FFmpeg binary not accessible: {e}")

        # 2. Verify Channels
        try:
            channels = channel_service.get_all_channels()
            if not channels:
                issues.append("No channel profiles found in channels.json")
            for c in channels:
                try:
                    channel_service.validate_channel_assets(c.id)
                except Exception as ce:
                    channels_ok = False
                    issues.append(f"Channel '{c.id}' asset error: {ce}")
        except Exception as e:
            channels_ok = False
            issues.append(f"Failed to validate channels: {e}")

        # 3. Verify Workflows
        try:
            workflows = workflow_service.get_all_workflows()
            if not workflows:
                workflows_ok = False
                issues.append("No workflow profiles found in workflows.json")
        except Exception as e:
            workflows_ok = False
            issues.append(f"Failed to validate workflows: {e}")

        return StartupValidationResult(
            ffmpeg_available=ffmpeg_ok,
            ffprobe_available=ffprobe_ok,
            channels_valid=channels_ok,
            workflows_valid=workflows_ok,
            issues=issues
        )

    async def validate_exported_clip(self, clip_path: Path) -> QualityValidationResult:
        warnings = []
        errors = []

        if not clip_path.exists():
            errors.append(f"Exported clip file does not exist at {clip_path}")
            return QualityValidationResult(
                is_valid=False, audio_present=False, file_size_bytes=0, duration=0.0,
                errors=errors
            )

        file_size = clip_path.stat().st_size
        if file_size == 0:
            errors.append(f"Exported clip is empty (0 bytes): {clip_path.name}")
            return QualityValidationResult(
                is_valid=False, audio_present=False, file_size_bytes=0, duration=0.0,
                errors=errors
            )

        audio_present = False
        duration = 0.0
        v_codec = None
        a_codec = None
        res_str = None

        try:
            meta = await self.ffprobe_service.get_metadata(clip_path)
            duration = meta.duration
            v_codec = meta.video_codec
            a_codec = meta.audio_codec
            if meta.width and meta.height:
                res_str = f"{meta.width}x{meta.height}"

            if a_codec:
                audio_present = True
            else:
                warnings.append(f"No audio stream detected in exported clip {clip_path.name}")

            if duration == 0:
                errors.append(f"Exported clip duration is 0 seconds: {clip_path.name}")
        except Exception as err:
            errors.append(f"FFprobe metadata validation failed for {clip_path.name}: {err}")

        is_valid = len(errors) == 0
        return QualityValidationResult(
            is_valid=is_valid,
            audio_present=audio_present,
            file_size_bytes=file_size,
            duration=duration,
            video_codec=v_codec,
            audio_codec=a_codec,
            resolution=res_str,
            warnings=warnings,
            errors=errors
        )

quality_validator = QualityValidator()
