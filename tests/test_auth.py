"""auth tests for API key protected write endpoints."""

from fastapi.testclient import TestClient


def test_create_team_requires_api_key(client: TestClient) -> None:
    client.headers.pop("X-API-Key", None)

    response = client.post(
        "/teams",
        json={"name": "No Key", "league": "Premier League", "country": "England"},
    )

    assert response.status_code == 401
    body = response.json()
    assert body["detail"]["error"]["code"] == "API_KEY_MISSING"


def test_create_team_rejects_invalid_api_key(client: TestClient) -> None:
    response = client.post(
        "/teams",
        json={"name": "Wrong Key", "league": "Premier League", "country": "England"},
        headers={"X-API-Key": "invalid-key"},
    )

    assert response.status_code == 403
    body = response.json()
    assert body["detail"]["error"]["code"] == "API_KEY_INVALID"


def test_create_team_accepts_valid_api_key(client: TestClient) -> None:
    response = client.post(
        "/teams",
        json={"name": "Valid Key", "league": "Premier League", "country": "England"},
        headers={"X-API-Key": "dev-api-key"},
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Valid Key"
