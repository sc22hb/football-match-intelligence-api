"""players endpoint tests for crud, pagination, and errors."""

from fastapi.testclient import TestClient



def _create_team(client: TestClient, name: str = "Arsenal") -> dict[str, object]:
    response = client.post(
        "/teams",
        json={"name": name, "league": "Premier League", "country": "England"},
    )
    assert response.status_code == 201
    return response.json()



def test_create_player_returns_201(client: TestClient) -> None:
    team = _create_team(client)

    response = client.post(
        "/players",
        json={"name": "Bukayo Saka", "team_id": team["id"], "position": "RW"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["name"] == "Bukayo Saka"
    assert body["team_id"] == team["id"]
    assert body["position"] == "RW"



def test_create_player_returns_404_when_team_missing(client: TestClient) -> None:
    response = client.post(
        "/players",
        json={"name": "No Team Player", "team_id": 999, "position": "CM"},
    )

    assert response.status_code == 404
    body = response.json()
    assert body["detail"]["error"]["code"] == "TEAM_NOT_FOUND"



def test_list_players_supports_pagination(client: TestClient) -> None:
    team = _create_team(client)

    players = [
        {"name": "Player A", "team_id": team["id"], "position": "GK"},
        {"name": "Player B", "team_id": team["id"], "position": "CB"},
        {"name": "Player C", "team_id": team["id"], "position": "CM"},
    ]

    for player in players:
        client.post("/players", json=player)

    response = client.get("/players", params={"skip": 1, "limit": 1})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 3
    assert body["skip"] == 1
    assert body["limit"] == 1
    assert len(body["items"]) == 1
    assert body["items"][0]["name"] == "Player B"



def test_get_player_returns_404_when_missing(client: TestClient) -> None:
    response = client.get("/players/999")

    assert response.status_code == 404
    body = response.json()
    assert body["detail"]["error"]["code"] == "PLAYER_NOT_FOUND"



def test_update_player_returns_200(client: TestClient) -> None:
    team = _create_team(client, name="Chelsea")
    player = client.post(
        "/players",
        json={"name": "Cole Palmer", "team_id": team["id"], "position": "AM"},
    ).json()

    response = client.put(
        f"/players/{player['id']}",
        json={"position": "RW"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == player["id"]
    assert body["position"] == "RW"



def test_delete_player_returns_204(client: TestClient) -> None:
    team = _create_team(client, name="Spurs")
    player = client.post(
        "/players",
        json={"name": "Son", "team_id": team["id"], "position": "LW"},
    ).json()

    response = client.delete(f"/players/{player['id']}")
    assert response.status_code == 204

    get_response = client.get(f"/players/{player['id']}")
    assert get_response.status_code == 404



def test_create_player_returns_409_for_duplicate_name_in_same_team(client: TestClient) -> None:
    team = _create_team(client, name="Liverpool")
    payload = {"name": "Salah", "team_id": team["id"], "position": "RW"}

    first = client.post("/players", json=payload)
    second = client.post("/players", json=payload)

    assert first.status_code == 201
    assert second.status_code == 409
    body = second.json()
    assert body["detail"]["error"]["code"] == "PLAYER_ALREADY_EXISTS"
