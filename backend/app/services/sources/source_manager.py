import logging
from pathlib import Path
from typing import List, Tuple, Optional, Callable
from app.models.source import MediaMetadata, SourceType, ImportResult
from app.services.sources.base_adapter import BaseSourceAdapter
from app.services.sources.adapters.youtube_adapter import YouTubeAdapter
from app.services.sources.adapters.local_adapter import LocalAdapter
from app.services.sources.adapters.direct_url_adapter import DirectUrlAdapter
from app.services.sources.adapters.hls_adapter import HlsAdapter
from app.services.sources.adapters.dash_adapter import DashAdapter
from app.services.sources.adapters.browser_adapter import BrowserAdapter

logger = logging.getLogger("yt_splitter")

class SourceManager:
    """
    Source Manager Registry for Universal Media Ingestion Architecture:
    Auto-detects media sources and routes requests to registered plugin adapters.
    """
    def __init__(self):
        self.adapters: List[BaseSourceAdapter] = [
            YouTubeAdapter(),
            HlsAdapter(),
            DashAdapter(),
            DirectUrlAdapter(),
            LocalAdapter(),
            BrowserAdapter(),
        ]

    def register_adapter(self, adapter: BaseSourceAdapter):
        self.adapters.insert(0, adapter)
        logger.info(f"[SourceManager] Registered custom adapter: {adapter.__class__.__name__}")

    def get_adapter(self, source: str) -> BaseSourceAdapter:
        clean_source = source.strip()
        for adapter in self.adapters:
            if adapter.supports(clean_source):
                return adapter
        raise ValueError(f"Unsupported media source input: '{source}'. Please enter a valid YouTube URL, Direct Video Link, HLS .m3u8, DASH .mpd, or Local File path.")

    def detect_source_type(self, source: str) -> SourceType:
        adapter = self.get_adapter(source)
        return adapter.source_type

    def validate_source(self, source: str) -> Tuple[bool, Optional[str]]:
        try:
            adapter = self.get_adapter(source)
            return adapter.validate(source)
        except ValueError as e:
            return False, str(e)

    async def import_source(
        self,
        source: str,
        target_dir: Path,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> ImportResult:
        adapter = self.get_adapter(source)
        logger.info(f"[SourceManager] Selected adapter '{adapter.__class__.__name__}' for source: {source}")

        valid, err = adapter.validate(source)
        if not valid:
            raise ValueError(f"Source validation failed: {err}")

        local_file = await adapter.import_media(source, target_dir, progress_callback=progress_callback)
        meta = await adapter.probe(source)

        return ImportResult(
            local_path=str(local_file.resolve()),
            metadata=meta
        )

source_manager = SourceManager()
