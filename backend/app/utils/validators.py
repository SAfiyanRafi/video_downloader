import re
from urllib.parse import urlparse, parse_qs
from fastapi import HTTPException, status

YOUTUBE_URL_REGEX = re.compile(
    r'^(https?://)?(www\.|m\.)?(youtube\.com/(watch\?v=|embed/|v/|shorts/)|youtu\.be/)([a-zA-Z0-9_-]{11})($|[?&#/])'
)

def validate_youtube_url(url: str) -> str:
    """
    Validates YouTube URL format and extracts standard video ID.
    Raises HTTPException 400 if invalid.
    """
    if not url or not isinstance(url, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL must be a non-empty string"
        )

    clean_url = url.strip()
    match = YOUTUBE_URL_REGEX.match(clean_url)
    
    if not match:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid YouTube URL format. Supported formats: youtube.com/watch?v=ID, youtu.be/ID, youtube.com/shorts/ID"
        )
    
    return clean_url
