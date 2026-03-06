"""analytics endpoint tests for team form, league table, and top scorers."""

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



def _create_match(
    client: TestClient,
    home_team_id: int,
    away_team_id: int,
    home_score: int,
    away_score: int,
    match_date: str,
    season: str = "2025/26",
) -> dict[str, object]:
    response = client.post(
        "/matches",
        json={
            "home_team_id": home_team_id,
            "away_team_id": away_team_id,
            "home_score": home_score,
            "away_score": away_score,
            "match_date": match_date,
            "season": season,
        },
    )
    assert response.status_code == 201
    return response.json()



def _create_event(
    client: TestClient,
    match_id: int,
    team_id: int,
    player_id: int,
    minute: int,
    event_type: str,
    event_detail: str,
) -> dict[str, object]:
    response = client.post(
        "/events",
        json={
            "match_id": match_id,
            "team_id": team_id,
            "player_id": player_id,
            "minute": minute,
            "event_type": event_type,
            "event_detail": event_detail,
        },
    )
    assert response.status_code == 201
    return response.json()



def test_team_form_endpoint_returns_expected_metrics(client: TestClient) -> None:
    team_a = _create_team(client, "Arsenal")
    team_b = _create_team(client, "Chelsea")
    team_c = _create_team(client, "Liverpool")

    _create_match(client, team_a["id"], team_b["id"], 2, 1, "2025-08-01")
    _create_match(client, team_c["id"], team_a["id"], 1, 1, "2025-08-08")
    _create_match(client, team_a["id"], team_c["id"], 0, 3, "2025-08-15")

    response = client.get(f"/analytics/team-form/{team_a['id']}")

    assert response.status_code == 200
    body = response.json()
    assert body["team_id"] == team_a["id"]
    assert body["matches_considered"] == 3
    assert body["wins"] == 1
    assert body["draws"] == 1
    assert body["losses"] == 1
    assert body["points"] == 4
    assert body["form_score"] == 44.44
    assert len(body["recent_results"]) == 3
    assert body["recent_results"][0]["match_date"] == "2025-08-15"
    assert body["recent_results"][0]["result"] == "L"



def test_league_table_endpoint_returns_ranked_table(client: TestClient) -> None:
    team_a = _create_team(client, "Team A")
    team_b = _create_team(client, "Team B")
    team_c = _create_team(client, "Team C")

    _create_match(client, team_a["id"], team_b["id"], 2, 0, "2025-09-01")
    _create_match(client, team_b["id"], team_c["id"], 1, 0, "2025-09-08")
    _create_match(client, team_a["id"], team_c["id"], 1, 1, "2025-09-15")

    response = client.get("/analytics/league-table", params={"season": "2025/26"})

    assert response.status_code == 200
    body = response.json()
    assert body["season"] == "2025/26"
    assert body["matches_considered"] == 3
    assert len(body["table"]) == 3

    assert body["table"][0]["team_name"] == "Team A"
    assert body["table"][0]["points"] == 4
    assert body["table"][1]["team_name"] == "Team B"
    assert body["table"][1]["points"] == 3
    assert body["table"][2]["team_name"] == "Team C"
    assert body["table"][2]["points"] == 1



def test_top_scorers_endpoint_returns_ranked_players(client: TestClient) -> None:
    home_team = _create_team(client, "Home")
    away_team = _create_team(client, "Away")

    striker = _create_player(client, "Striker", home_team["id"], "ST")
    winger = _create_player(client, "Winger", home_team["id"], "RW")
    away_player = _create_player(client, "Away ST", away_team["id"], "ST")

    match = _create_match(client, home_team["id"], away_team["id"], 3, 1, "2025-10-01")

    _create_event(client, match["id"], home_team["id"], striker["id"], 15, "goal", "Header")
    _create_event(client, match["id"], home_team["id"], striker["id"], 58, "goal", "Penalty")
    _create_event(client, match["id"], home_team["id"], winger["id"], 70, "goal", "Left foot")
    _create_event(client, match["id"], away_team["id"], away_player["id"], 80, "shot", "On target")

    response = client.get("/analytics/top-scorers", params={"season": "2025/26", "limit": 2})

    assert response.status_code == 200
    body = response.json()
    assert body["season"] == "2025/26"
    assert body["events_considered"] == 3
    assert len(body["top_scorers"]) == 2

    assert body["top_scorers"][0]["player_name"] == "Striker"
    assert body["top_scorers"][0]["goals"] == 2
    assert body["top_scorers"][1]["player_name"] == "Winger"
    assert body["top_scorers"][1]["goals"] == 1
