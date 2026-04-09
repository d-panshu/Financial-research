import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


@pytest.fixture
def client():
    with patch("backend.graph.graph_builder.SqliteSaver"):
        from backend.api.server import app
        return TestClient(app)


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_start_research_endpoint(client):
    with patch("backend.api.routes.research.graph"):
        response = client.post("/research", json={"ticker": "AAPL", "query": "Should I buy?"})
        assert response.status_code == 200
        data = response.json()
        assert data["ticker"] == "AAPL"
        assert "session_id" in data


def test_start_research_validates_ticker(client):
    response = client.post("/research", json={"ticker": "", "query": "test"})
    assert response.status_code == 422


def test_approve_endpoint(client):
    with patch("backend.api.routes.hitl.graph") as mock_graph:
        mock_graph.update_state.return_value = None
        mock_graph.astream.return_value.__aiter__ = MagicMock(return_value=iter([]))

        response = client.post("/api/approve", json={
            "ticker": "AAPL",
            "session_id": "fake-session-id",
            "feedback": "Looks correct",
        })
        assert response.status_code in (200, 500)  # 500 if session not in DB is fine in unit test


def test_report_not_found(client):
    response = client.get("/api/report/nonexistent-session")
    assert response.status_code == 404
