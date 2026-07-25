import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
from app.services.hooks.hook_engine import HookEngine

client = TestClient(app)

def test_hook_settings_endpoint():
    response = client.get("/api/v1/hooks/settings")
    assert response.status_code == 200
    data = response.json()
    assert "curiosity_keywords" in data
    assert "wait" in data["curiosity_keywords"]

def test_hook_engine_initialization():
    engine = HookEngine()
    assert len(engine.curiosity_keywords) > 0
    assert "watch this" in engine.curiosity_keywords
