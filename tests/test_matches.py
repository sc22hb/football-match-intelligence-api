"""matches endpoint tests for crud, pagination, and errors."""

from datetime import date

from fastapi.testclient import TestClient



def _create_team(client: TestClient, name: str, league: str = "Premier League") -> dict[str, object]:
    response = client.post(
        "/teams",
        json={"name": name, "league": league, "country": "England"},
    )
    assert response.status_code == 201
    return response.json()



def test_create_match_returns_201(client: TestClient) -> None:
    home_team = _create_team(client, "Arsenal")
    away_team = _create_team(client, "Chelsea")

    payload = {
        "home_team_id": home_team["id"],
        "away_team_id": away_team["id"],
        "home_score": 2,
        "away_score": 1,
        "match_date": "2025-08-17",
        "season": "2025/26",
    }

    response = client.post("/matches", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["home_team_id"] == home_team["id"]
    assert body["away_team_id"] == away_team["id"]
    assert body["home_score"] == 2
    assert body["away_score"] == 1
    assert body["match_date"] == "2025-08-17"
    assert body["season"] == "2025/26"



def test_create_match_returns_404_when_team_missing(client: TestClient) -> None:
    home_team = _create_team(client, "Spurs")

    payload = {
        "home_team_id": home_team["id"],
        "away_team_id": 999,
        "home_score": 0,
        "away_score": 0,
        "match_date": "2025-09-01",
        "season": "2025/26",
    }

    response = client.post("/matches", json=payload)

    assert response.status_code == 404
    body = response.json()
    assert body["detail"]["error"]["code"] == "TEAM_NOT_FOUND"



def test_list_matches_supports_pagination(client: TestClient) -> None:
    home_team = _create_team(client, "Liverpool")
    away_team = _create_team(client, "Everton")

    matches = [
        {
            "home_team_id": home_team["id"],
            "away_team_id": away_team["id"],
            "home_score": 1,
            "away_score": 0,
            "match_date": "2025-08-01",
            "season": "2025/26",
        },
        {
            "home_team_id": away_team["id"],
            "away_team_id": home_team["id"],
            "home_score": 0,
            "away_score": 0,
            "match_date": "2025-08-15",
            "season": "2025/26",
        },
        {
            "home_team_id": home_team["id"],
            "away_team_id": away_team["id"],
            "home_score": 3,
            "away_score": 2,
            "match_date": "2025-09-01",
            "season": "2025/26",
        },
    ]

    for match in matches:
        response = client.post("/matches", json=match)
        assert response.status_code == 201

    response = client.get("/matches", params={"skip": 1, "limit": 1})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 3
    assert body["skip"] == 1
    assert body["limit"] == 1
    assert len(body["items"]) == 1
    assert body["items"][0]["match_date"] == "2025-08-15"



def test_get_match_returns_404_when_missing(client: TestClient) -> None:
    response = client.get("/matches/999")

    assert response.status_code == 404
    body = response.json()
    assert body["detail"]["error"]["code"] == "MATCH_NOT_FOUND"



def test_update_match_returns_200(client: TestClient) -> None:
    home_team = _create_team(client, "Newcastle")
    away_team = _create_team(client, "Aston Villa")

    created = client.post(
        "/matches",
        json={
            "home_team_id": home_team["id"],
            "away_team_id": away_team["id"],
            "home_score": 1,
            "away_score": 1,
            "match_date": "2025-10-01",
            "season": "2025/26",
        },
    ).json()

    response = client.put(
        f"/matches/{created['id']}",
        json={"home_score": 2, "away_score": 1},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == created["id"]
    assert body["home_score"] == 2
    assert body["away_score"] == 1



def test_update_match_returns_422_for_same_teams(client: TestClient) -> None:
    home_team = _create_team(client, "Leeds")
    away_team = _create_team(client, "Leicester")

    created = client.post(
        "/matches",
        json={
            "home_team_id": home_team["id"],
            "away_team_id": away_team["id"],
            "home_score": 0,
            "away_score": 0,
            "match_date": "2025-11-01",
            "season": "2025/26",
        },
    ).json()

    response = client.put(
        f"/matches/{created['id']}",
        json={"away_team_id": home_team["id"]},
    )

    assert response.status_code == 422
    body = response.json()
    assert body["detail"]["error"]["code"] == "INVALID_MATCH_TEAMS"



def test_delete_match_returns_204(client: TestClient) -> None:
    home_team = _create_team(client, "West Ham")
    away_team = _create_team(client, "Brentford")

    created = client.post(
        "/matches",
        json={
            "home_team_id": home_team["id"],
            "away_team_id": away_team["id"],
            "home_score": 1,
            "away_score": 0,
            "match_date": date(2025, 12, 1).isoformat(),
            "season": "2025/26",
        },
    ).json()

    response = client.delete(f"/matches/{created['id']}")
    assert response.status_code == 204

    get_response = client.get(f"/matches/{created['id']}")
    assert get_response.status_code == 404
