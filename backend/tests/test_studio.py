import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
from app.services.studio.subtitle_service import SubtitleService, SubtitleSegment
from app.models.studio import SubtitleStylePreset

client = TestClient(app)

def test_watch_folder_endpoint():
    response = client.get("/api/v1/studio/watch-folder")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_subtitle_ass_generation(tmp_path: Path):
    service = SubtitleService()
    segments = [
        SubtitleSegment(0.0, 3.5, "Welcome to Creator Studio!"),
        SubtitleSegment(3.5, 7.0, "AI Subtitles with custom styling.")
    ]
    output_ass = tmp_path / "test.ass"
    res = service.export_ass(segments, SubtitleStylePreset.TIKTOK, output_ass)
    assert res.exists()
    content = res.read_text(encoding="utf-8")
    assert "[Script Info]" in content
    assert "Dialogue: 0,0:00:00.00,0:00:03.50,Default,,0,0,0,,Welcome to Creator Studio!" in content
