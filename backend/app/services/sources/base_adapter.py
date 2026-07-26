from abc import ABC, abstractmethod
from pathlib import Path
from typing import Tuple, Optional, Callable
from app.models.source import MediaMetadata, SourceType

class BaseSourceAdapter(ABC):
    """
    Abstract Source Adapter Interface for Universal Media Ingestion Architecture.
    Every source adapter must implement these methods.
    """
    @property
    @abstractmethod
    def source_type(self) -> SourceType:
        pass

    @abstractmethod
    def supports(self, source: str) -> bool:
        """Returns True if this adapter supports the given input string."""
        pass

    @abstractmethod
    def validate(self, source: str) -> Tuple[bool, Optional[str]]:
        """Validates if the source is accessible and well-formed."""
        pass

    @abstractmethod
    async def probe(self, source: str) -> MediaMetadata:
        """Extracts standardized MediaMetadata for the source."""
        pass

    @abstractmethod
    async def import_media(
        self,
        source: str,
        target_dir: Path,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> Path:
        """Imports or downloads the source into a local playable video file."""
        pass
