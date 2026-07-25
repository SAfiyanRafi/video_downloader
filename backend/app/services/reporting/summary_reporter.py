import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel

logger = logging.getLogger("yt_splitter")

class ProcessingReport(BaseModel):
    job_id: str
    workflow_id: str
    channel_id: Optional[str] = None
    url_or_file: str
    total_duration_seconds: float
    parts_count: int
    download_resolution: Optional[str] = None
    export_aspect_ratio: str
    branding_applied: bool
    subtitles_applied: bool
    thumbnails_generated_count: int
    zip_created: bool
    quality_validated: bool
    processing_time_seconds: float
    created_at: datetime

class SummaryReporter:
    """
    Processing Summary Reporter:
    Generates processing_report.json and human-readable Markdown summaries.
    """
    def generate_report(self, report_data: ProcessingReport, logs_dir: Path) -> Path:
        logs_dir.mkdir(parents=True, exist_ok=True)
        report_json_path = logs_dir / "processing_report.json"
        report_md_path = logs_dir / "processing_report.md"

        # 1. Export JSON Report
        report_dict = report_data.model_dump(mode="json")
        report_json_path.write_text(json.dumps(report_dict, indent=2), encoding="utf-8")

        # 2. Export Markdown Report
        md_text = f"""# Processing Summary Report — Job {report_data.job_id}

- **Job ID**: `{report_data.job_id}`
- **Workflow Profile**: `{report_data.workflow_id}`
- **Channel Branding**: `{report_data.channel_id or 'None'}`
- **Source**: `{report_data.url_or_file}`
- **Total Duration**: `{report_data.total_duration_seconds:.2f} seconds`
- **Parts Count**: `{report_data.parts_count} equal clips`
- **Download Resolution**: `{report_data.download_resolution or 'Source Best'}`
- **Export Aspect Ratio**: `{report_data.export_aspect_ratio}`
- **Branding Status**: `{'Applied' if report_data.branding_applied else 'None'}`
- **Subtitles Status**: `{'Generated & Burned' if report_data.subtitles_applied else 'None'}`
- **Thumbnails Generated**: `{report_data.thumbnails_generated_count} candidates`
- **ZIP Created**: `{'Yes' if report_data.zip_created else 'No'}`
- **Quality Verified**: `{'PASSED (Playable, Audio Present)' if report_data.quality_validated else 'FAILED'}`
- **Total Execution Time**: `{report_data.processing_time_seconds:.2f} seconds`
- **Completed At**: `{report_data.created_at.isoformat()}`
"""
        report_md_path.write_text(md_text, encoding="utf-8")
        logger.info(f"[Job {report_data.job_id}] Processing summary report generated at {report_json_path.name}")
        return report_json_path

summary_reporter = SummaryReporter()
