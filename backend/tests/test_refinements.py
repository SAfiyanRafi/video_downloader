import pytest
from pathlib import Path
from app.services.validation.quality_validator import quality_validator
from app.services.storage.project_manager import project_manager
from app.services.metadata.inspector import metadata_inspector
from app.services.reporting.summary_reporter import summary_reporter, ProcessingReport
from datetime import datetime, timezone

@pytest.mark.anyio
async def test_startup_validation():
    val = await quality_validator.validate_startup()
    assert val.ffmpeg_available is True
    assert val.channels_valid is True
    assert val.workflows_valid is True

def test_project_manager(tmp_path):
    proj = project_manager.get_temp_project("test_job_123")
    assert proj.original.exists()
    assert proj.split.exists()
    assert proj.branded.exists()
    assert proj.studio.exists()
    assert proj.exports.exists()
    assert proj.thumbnails.exists()
    assert proj.logs.exists()

def test_summary_reporter(tmp_path):
    rep = ProcessingReport(
        job_id="test_job_123",
        workflow_id="shorts",
        channel_id="rhymes4ever",
        url_or_file="https://www.youtube.com/watch?v=test",
        total_duration_seconds=120.0,
        parts_count=4,
        download_resolution="1080p",
        export_aspect_ratio="9:16",
        branding_applied=True,
        subtitles_applied=True,
        thumbnails_generated_count=3,
        zip_created=True,
        quality_validated=True,
        processing_time_seconds=15.2,
        created_at=datetime.now(timezone.utc)
    )
    json_path = summary_reporter.generate_report(rep, tmp_path)
    assert json_path.exists()
    assert (tmp_path / "processing_report.md").exists()
