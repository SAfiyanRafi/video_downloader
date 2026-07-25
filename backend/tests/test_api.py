from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"

def test_mcp_tools_endpoint():
    response = client.get("/api/v1/mcp/tools")
    assert response.status_code == 200
    data = response.json()
    assert "tools" in data
    assert data["tools"][0]["name"] == "split_video"

def test_create_job_invalid_url():
    response = client.post(
        "/api/v1/jobs",
        json={"url": "ftp://invalidurl.com", "parts": 4}
    )
    assert response.status_code == 400

def test_create_job_invalid_parts():
    response = client.post(
        "/api/v1/jobs",
        json={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "parts": 100}
    )
    assert response.status_code == 422 or response.status_code == 400

def test_cancel_nonexistent_job():
    response = client.delete("/api/v1/jobs/invalid_id_999")
    assert response.status_code == 404
