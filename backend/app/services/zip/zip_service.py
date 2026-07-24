import asyncio
import zipfile
import logging
from pathlib import Path
from typing import List

logger = logging.getLogger("yt_splitter")

class ZipService:
    """
    Creates ZIP archives of processed video clips.
    """

    async def create_zip_archive(self, clip_paths: List[Path], output_zip_path: Path) -> Path:
        if not clip_paths:
            raise ValueError("No clip paths provided to ZIP service")

        loop = asyncio.get_running_loop()

        def _zip_files():
            with zipfile.ZipFile(output_zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for clip in clip_paths:
                    if clip.exists():
                        zf.write(clip, arcname=clip.name)
            return output_zip_path

        return await loop.run_in_executor(None, _zip_files)
