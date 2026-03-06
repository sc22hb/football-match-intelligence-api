"""events endpoint tests for create/list and validation errors."""

from fastapi.testclient import TestClient



def _create_team(client: TestClient, name: str, league: str = "Premier League") -> dict[str, object]:
    response = client.post(
        "/teams",
        json={"name": name, "league": league, "country": "England"},
    )
    assert response.status_code == 201
    return response.json()



def _create_player(client: TestClient, name: str, team_id: int, position: str = "FW") -> dict[str, object]:
    response = client.post(
        "/players",
        json={"name": name, "team_id": team_id, "position": position},
    )
    assert response.status_code == 201
    return response.json()



def _create_match(client: TestClient, home_team_id: int, away_team_id: int) -> dict[str, object]:
    response = client.post(
        "/matches",
        json={
            "home_team_id": home_team_id,
            "away_team_id": away_team_id,
            "home_score": 0,
            "away_score": 0,
            "match_date": "2025-09-10",
            "season": "2025/26",
        },
    )
    assert response.status_code == 201
    return response.json()



def test_create_event_returns_201(client: TestClient) -> None:
    home_team = _create_team(client, "Arsenal")
    away_team = _create_team(client, "Chelsea")
    player = _create_player(client, "Saka", home_team["id"], "RW")
    match = _create_match(client, home_team["id"], away_team["id"])

    response = client.post(
        "/events",
        json={
            "match_id": match["id"],
            "team_id": home_team["id"],
            "player_id": player["id"],
            "minute": 72,
            "event_type": "goal",
            "event_detail": "Right-foot shot from inside the box",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["match_id"] == match["id"]
    assert body["team_id"] == home_team["id"]
    assert body["player_id"] == player["id"]
    assert body["minute"] == 72
    assert body["event_type"] == "goal"



def test_list_events_supports_pagination(client: TestClient) -> None:
    home_team = _create_team(client, "Liverpool")
    away_team = _create_team(client, "Everton")
    player = _create_player(client, "Salah", home_team["id"], "RW")
    match = _create_match(client, home_team["id"], away_team["id"])

    events = [
        {
            "match_id": match["id"],
            "team_id": home_team["id"],
            "player_id": player["id"],
            "minute": 10,
            "event_type": "shot",
            "event_detail": "Shot on target",
        },
        {
            "match_id": match["id"],
            "team_id": home_team["id"],
            "player_id": player["id"],
            "minute": 35,
            "event_type": "assist",
            "event_detail": "Through pass",
        },
        {
            "match_id": match["id"],
            "team_id": home_team["id"],
            "player_id": player["id"],
            "minute": 76,
            "event_type": "goal",
            "event_detail": "Header from close range",
        },
    ]

    for event in events:
        create_response = client.post("/events", json=event)
        assert create_response.status_code == 201

    response = client.get("/events", params={"skip": 1, "limit": 1})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 3
    assert body["skip"] == 1
    assert body["limit"] == 1
    assert len(body["items"]) == 1
    assert body["items"][0]["minute"] == 35



def test_create_event_returns_404_when_match_missing(client: TestClient) -> None:
    team = _create_team(client, "Spurs")
    player = _create_player(client, "Son", team["id"], "LW")

    response = client.post(
        "/events",
        json={
            "match_id": 999,
            "team_id": team["id"],
            "player_id": player["id"],
            "minute": 22,
            "event_type": "goal",
            "event_detail": "Low finish",
        },
    )

    assert response.status_code == 404
    body = response.json()
    assert body["detail"]["error"]["code"] == "MATCH_NOT_FOUND"



def test_create_event_returns_422_when_player_not_in_team(client: TestClient) -> None:
    home_team = _create_team(client, "City")
    away_team = _create_team(client, "United")
    player = _create_player(client, "Haaland", home_team["id"], "ST")
    match = _create_match(client, home_team["id"], away_team["id"])

    response = client.post(
        "/events",
        json={
            "match_id": match["id"],
            "team_id": away_team["id"],
            "player_id": player["id"],
            "minute": 45,
            "event_type": "shot",
            "event_detail": "Long-range attempt",
        },
    )

    assert response.status_code == 422
    body = response.json()
    assert body["detail"]["error"]["code"] == "INVALID_EVENT_RELATION"



def test_create_event_returns_422_when_team_not_in_match(client: TestClient) -> None:
    home_team = _create_team(client, "Leeds")
    away_team = _create_team(client, "Leicester")
    other_team = _create_team(client, "Burnley")
    player = _create_player(client, "Benson", other_team["id"], "CM")
    match = _create_match(client, home_team["id"], away_team["id"])

    response = client.post(
        "/events",
        json={
            "match_id": match["id"],
            "team_id": other_team["id"],
            "player_id": player["id"],
            "minute": 15,
            "event_type": "pass",
            "event_detail": "Key pass",
        },
    )

    assert response.status_code == 422
    body = response.json()
    assert body["detail"]["error"]["code"] == "INVALID_EVENT_RELATION"
