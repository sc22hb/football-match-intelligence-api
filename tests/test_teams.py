"""teams endpoint tests for crud, pagination, and errors."""

from fastapi.testclient import TestClient



def test_create_team_returns_201(client: TestClient) -> None:
    payload = {"name": "Arsenal", "league": "Premier League", "country": "England"}

    response = client.post("/teams", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["name"] == payload["name"]
    assert body["league"] == payload["league"]
    assert body["country"] == payload["country"]



def test_list_teams_supports_pagination(client: TestClient) -> None:
    teams = [
        {"name": "Arsenal", "league": "Premier League", "country": "England"},
        {"name": "Barcelona", "league": "La Liga", "country": "Spain"},
        {"name": "Bayern", "league": "Bundesliga", "country": "Germany"},
    ]

    for team in teams:
        client.post("/teams", json=team)

    response = client.get("/teams", params={"skip": 1, "limit": 1})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 3
    assert body["skip"] == 1
    assert body["limit"] == 1
    assert len(body["items"]) == 1
    assert body["items"][0]["name"] == "Barcelona"



def test_get_team_returns_404_when_missing(client: TestClient) -> None:
    response = client.get("/teams/999")

    assert response.status_code == 404
    body = response.json()
    assert body["detail"]["error"]["code"] == "TEAM_NOT_FOUND"



def test_update_team_updates_fields(client: TestClient) -> None:
    created = client.post(
        "/teams",
        json={"name": "Juventus", "league": "Serie A", "country": "Italy"},
    ).json()

    response = client.put(
        f"/teams/{created['id']}",
        json={"league": "Serie A TIM"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == created["id"]
    assert body["league"] == "Serie A TIM"



def test_delete_team_returns_204(client: TestClient) -> None:
    created = client.post(
        "/teams",
        json={"name": "PSG", "league": "Ligue 1", "country": "France"},
    ).json()

    response = client.delete(f"/teams/{created['id']}")
    assert response.status_code == 204

    get_response = client.get(f"/teams/{created['id']}")
    assert get_response.status_code == 404



def test_create_team_returns_409_on_duplicate_name(client: TestClient) -> None:
    payload = {"name": "Liverpool", "league": "Premier League", "country": "England"}

    first = client.post("/teams", json=payload)
    second = client.post("/teams", json=payload)

    assert first.status_code == 201
    assert second.status_code == 409
    body = second.json()
    assert body["detail"]["error"]["code"] == "TEAM_ALREADY_EXISTS"
