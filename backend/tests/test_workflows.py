import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.branding.workflow_service import WorkflowService

client = TestClient(app)

def test_list_workflows_endpoint():
    response = client.get("/api/v1/workflows")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    wf_ids = [w["id"] for w in data]
    assert "shorts" in wf_ids
    assert "longform" in wf_ids

def test_workflow_service():
    service = WorkflowService()
    shorts = service.get_workflow("shorts")
    assert shorts.id == "shorts"
    assert shorts.allow_intro_outro is False
    assert shorts.aspect_ratio == "9:16"

def test_ai_suggestions_endpoint():
    response = client.post("/api/v1/workflows/ai-suggestions?title=Rhymes4ever_Part_01")
    assert response.status_code == 200
    data = response.json()
    assert "titles" in data
    assert len(data["titles"]) >= 3
    assert "#Shorts" in data["hashtags"]
