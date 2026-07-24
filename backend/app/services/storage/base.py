from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict

class BaseStorageProvider(ABC):
    """Abstract interface for storage providers (Local, AWS S3, Cloudflare R2, Supabase)."""

    @abstractmethod
    def get_job_directory(self, job_id: str) -> Path:
        pass

    @abstractmethod
    def get_download_url(self, job_id: str, relative_path: str) -> str:
        pass

    @abstractmethod
    def cleanup_job(self, job_id: str) -> bool:
        pass
