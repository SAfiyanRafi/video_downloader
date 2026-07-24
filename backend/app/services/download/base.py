from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable, Optional
from app.models.job import QualityOption

class BaseDownloader(ABC):
    """
    Abstract interface for video downloaders.
    Allows easy extension for Youtube, Google Drive, Dropbox, Uploads, etc.
    """
    
    @abstractmethod
    async def download(
        self,
        source: str,
        output_dir: Path,
        quality: QualityOption = QualityOption.BEST,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> Path:
        """
        Downloads video from source and saves it in output_dir.
        Returns the Path to the downloaded local video file.
        """
        pass
