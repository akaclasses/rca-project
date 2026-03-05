import pytest
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    response = client.get("/health")
    # Even if DB is not mocked, it should return a JSON with status ok (and database might be error or ok)
    assert response.status_code == 200
    data = response.get_json()
    assert "status" in data
    assert data["status"] == "ok"
    assert "database" in data

def test_api_404(client):
    response = client.get("/api/notfoundroute")
    assert response.status_code == 404
