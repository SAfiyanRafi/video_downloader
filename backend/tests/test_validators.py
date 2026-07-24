import pytest
from fastapi import HTTPException
from app.utils.validators import validate_youtube_url

def test_valid_youtube_urls():
    valid_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "http://youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "https://www.youtube.com/shorts/dQw4w9WgXcQ",
        "https://youtube.com/embed/dQw4w9WgXcQ"
    ]
    for url in valid_urls:
        cleaned = validate_youtube_url(url)
        assert cleaned == url

def test_invalid_youtube_urls():
    invalid_urls = [
        "https://vimeo.com/123456",
        "https://google.com",
        "not_a_url",
        "",
        "https://youtube.com/watch?v=invalid_short_id"
    ]
    for url in invalid_urls:
        with pytest.raises(HTTPException) as exc_info:
            validate_youtube_url(url)
        assert exc_info.value.status_code == 400
