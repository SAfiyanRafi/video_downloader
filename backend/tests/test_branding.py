import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
from app.services.branding.channel_service import ChannelService
from app.services.branding.branding_service import BrandingService

client = TestClient(app)

def test_list_channels_endpoint():
    response = client.get("/api/v1/channels")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    channel_ids = [c["id"] for c in data]
    assert "rhymes4ever" in channel_ids
    assert "cut_clips" in channel_ids

def test_channel_service_validation():
    service = ChannelService()
    profile = service.validate_channel_assets("rhymes4ever")
    assert profile.id == "rhymes4ever"
    assert profile.filename_prefix == "Rhymes4ever"

def test_create_job_invalid_channel():
    response = client.post(
        "/api/v1/jobs",
        json={
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "parts": 4,
            "channel": "nonexistent_channel_123"
        }
    )
    assert response.status_code == 400
    assert "nonexistent_channel_123" in response.json()["detail"]

def test_branding_service_concat(tmp_path: Path):
    import asyncio
    service = BrandingService()
    channel_service = ChannelService()
    profile = channel_service.get_channel("rhymes4ever")
    
    root_dir = channel_service.root_dir
    intro_path = root_dir / profile.intro
    outro_path = root_dir / profile.outro

    # Create a dummy test clip using FFmpeg
    from app.services.processing.ffmpeg_service import get_ffmpeg_executable
    import subprocess
    
    test_clip = tmp_path / "test_segment.mp4"
    output_branded = tmp_path / "branded_output.mp4"

    ffmpeg_bin = get_ffmpeg_executable()
    subprocess.run([
        ffmpeg_bin, "-y",
        "-f", "lavfi", "-i", "color=c=black:s=1280x720:d=2",
        "-f", "lavfi", "-i", "sine=f=1000:d=2",
        "-c:v", "libx264", "-c:a", "aac", "-shortest", str(test_clip)
    ], check=True)

    result_path = asyncio.run(service.add_intro_outro(
        clip_path=test_clip,
        output_path=output_branded,
        intro_path=intro_path,
        outro_path=outro_path
    ))

    assert result_path.exists()
    assert result_path.stat().st_size > 0
