"""health endpoint tests."""

from fastapi.testclient import TestClient



def test_health_endpoint_returns_service_status(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "football-match-intelligence-api"
    assert "timestamp" in payload
