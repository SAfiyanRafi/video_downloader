import pytest
from pathlib import Path
from app.services.sources.source_manager import SourceManager
from app.models.source import SourceType

def test_source_manager_detection():
    manager = SourceManager()

    # YouTube URL
    yt_type = manager.detect_source_type("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    assert yt_type == SourceType.YOUTUBE

    # HLS Stream .m3u8
    hls_type = manager.detect_source_type("https://example.com/live/playlist.m3u8")
    assert hls_type == SourceType.HLS

    # DASH Stream .mpd
    dash_type = manager.detect_source_type("https://example.com/live/manifest.mpd")
    assert dash_type == SourceType.DASH

    # Direct Video Link
    direct_type = manager.detect_source_type("https://example.com/videos/sample.mp4")
    assert direct_type == SourceType.DIRECT_URL

def test_source_validation():
    manager = SourceManager()
    valid_yt, _ = manager.validate_source("https://youtu.be/dQw4w9WgXcQ")
    assert valid_yt is True

    valid_direct, _ = manager.validate_source("https://example.com/clip.mov")
    assert valid_direct is True
