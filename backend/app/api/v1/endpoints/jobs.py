from pathlib import Path
from fastapi import APIRouter, HTTPException, status, Path as FastAPIPath
from fastapi.responses import FileResponse

from app.models.job import JobCreateRequest, JobResponse, JobDownloadsResponse
from app.services.jobs.job_manager import job_manager
from app.utils.validators import validate_youtube_url
from app.core.config import settings

router = APIRouter()

@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(request: JobCreateRequest):
    """
    Submits a new YouTube video splitting job.
    Accepts YouTube URL, desired split parts (2 to 50), quality option, and optional channel profile ID.
    """
    clean_url = validate_youtube_url(request.url)
    
    if request.parts < settings.MIN_SPLIT_PARTS or request.parts > settings.MAX_SPLIT_PARTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Parts must be between {settings.MIN_SPLIT_PARTS} and {settings.MAX_SPLIT_PARTS}"
        )

    try:
        return job_manager.create_job(
            url=clean_url,
            parts=request.parts,
            quality=request.quality,
            channel=request.channel
        )
    except (KeyError, FileNotFoundError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create job: {str(e)}"
        )

@router.get("/{job_id}", response_model=JobResponse)
async def get_job_status(job_id: str):
    """
    Retrieves status and progress percentage of a split job.
    """
    try:
        return job_manager.get_job_response(job_id)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job ID '{job_id}' not found"
        )

@router.delete("/{job_id}", response_model=JobResponse)
async def cancel_job(job_id: str):
    """
    Cancels an ongoing split job and cleans up any temporary files.
    """
    try:
        return job_manager.cancel_job(job_id)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job ID '{job_id}' not found"
        )

@router.get("/{job_id}/downloads", response_model=JobDownloadsResponse)
async def get_job_downloads(job_id: str):
    """
    Retrieves download URLs for split clips and ZIP archive once complete.
    """
    try:
        return job_manager.get_job_downloads(job_id)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job ID '{job_id}' not found"
        )

@router.get("/{job_id}/files/{file_path:path}")
async def download_job_file(job_id: str, file_path: str):
    """
    Serves individual clip files or ZIP archives for a specific job.
    Includes security checks against path traversal.
    """
    job_dir = job_manager.storage.get_job_directory(job_id)
    target_file = (job_dir / file_path).resolve()

    # Path traversal protection
    if not str(target_file).startswith(str(job_dir.resolve())):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    if not target_file.exists() or not target_file.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    filename = target_file.name
    media_type = "application/octet-stream"
    if filename.endswith(".zip"):
        media_type = "application/zip"
    elif filename.endswith(".mp4"):
        media_type = "video/mp4"

    return FileResponse(
        path=target_file,
        filename=filename,
        media_type=media_type
    )
