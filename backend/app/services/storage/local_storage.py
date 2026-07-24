import shutil
import logging
from pathlib import Path
from app.services.storage.base import BaseStorageProvider
from app.core.config import settings

logger = logging.getLogger("yt_splitter")

class LocalStorageProvider(BaseStorageProvider):
    """Local filesystem implementation of storage provider."""

    def __init__(self, temp_base_dir: Path = settings.TEMP_DIR):
        self.base_dir = temp_base_dir / "jobs"
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def get_job_directory(self, job_id: str) -> Path:
        job_dir = self.base_dir / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        return job_dir

    def get_download_url(self, job_id: str, relative_filename: str) -> str:
        return f"/api/v1/jobs/{job_id}/files/{relative_filename}"

    def cleanup_job(self, job_id: str) -> bool:
        job_dir = self.base_dir / job_id
        if job_dir.exists():
            try:
                shutil.rmtree(job_dir)
                logger.info(f"Successfully cleaned up job directory: {job_dir}")
                return True
            except Exception as e:
                logger.error(f"Failed to clean up job directory {job_dir}: {e}")
                return False
        return False
