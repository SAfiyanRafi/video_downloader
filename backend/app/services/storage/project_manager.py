import shutil
import logging
from pathlib import Path
from typing import Dict, Optional
from app.core.config import settings

logger = logging.getLogger("yt_splitter")

class ProjectDirectoryStructure:
    def __init__(self, base_path: Path):
        self.root = base_path
        self.original = base_path / "Original"
        self.split = base_path / "Split"
        self.branded = base_path / "Branded"
        self.studio = base_path / "Studio"
        self.exports = base_path / "Exports"
        self.thumbnails = base_path / "Thumbnails"
        self.zip_dir = base_path / "ZIP"
        self.logs = base_path / "Logs"
        self.create_all()

    def create_all(self):
        for d in [
            self.root, self.original, self.split, self.branded,
            self.studio, self.exports, self.thumbnails, self.zip_dir, self.logs
        ]:
            d.mkdir(parents=True, exist_ok=True)

class ProjectManager:
    """
    Structured Project Storage Manager:
    Organizes all job assets cleanly into structured subdirectories.
    Never overwrites original files.
    """
    def __init__(self):
        self.base_temp = settings.TEMP_DIR / "projects"
        self.base_desktop = settings.DEFAULT_DOWNLOAD_DIR

    def get_temp_project(self, job_id: str) -> ProjectDirectoryStructure:
        return ProjectDirectoryStructure(self.base_temp / job_id)

    def export_to_desktop(self, job_id: str) -> ProjectDirectoryStructure:
        desktop_proj = ProjectDirectoryStructure(self.base_desktop / f"Project_{job_id}")
        temp_proj = self.get_temp_project(job_id)

        # Copy temp assets to Desktop project directory
        try:
            for src_dir, dst_dir in [
                (temp_proj.exports, desktop_proj.exports),
                (temp_proj.thumbnails, desktop_proj.thumbnails),
                (temp_proj.zip_dir, desktop_proj.zip_dir),
                (temp_proj.logs, desktop_proj.logs),
            ]:
                if src_dir.exists():
                    for f in src_dir.glob("*"):
                        if f.is_file():
                            shutil.copy2(f, dst_dir / f.name)
            logger.info(f"[Project {job_id}] Successfully exported structured project to desktop: {desktop_proj.root}")
        except Exception as e:
            logger.warning(f"[Project {job_id}] Desktop export failed: {e}")

        return desktop_proj

project_manager = ProjectManager()
