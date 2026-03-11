"""analytics endpoint tests for team form, league table, and top scorers."""

from fastapi.testclient import TestClient



def _assert_metadata(body: dict[str, object]) -> None:
    metadata = body["metadata"]
    assert metadata["data_source"] == "Fantasy Premier League API"
    assert metadata["dataset_name"] == "Premier League 2025/26"
    assert metadata["dataset_version"] == "fpl-element-summary-live"
    assert "computed_at" in metadata


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
    assert "Form score is based on 3 recent matches" in body["explanation_summary"]
    assert len(body["recent_results"]) == 3
    assert body["recent_results"][0]["match_date"] == "2025-08-15"
    assert body["recent_results"][0]["result"] == "L"
    assert body["recent_results"][0]["points_awarded"] == 0
    assert body["recent_results"][0]["explanation"] == "Loss contributes 0 points."
    _assert_metadata(body)



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
    _assert_metadata(body)



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
    _assert_metadata(body)


def test_most_assists_endpoint_returns_ranked_players(client: TestClient) -> None:
    home_team = _create_team(client, "Assist Home")
    away_team = _create_team(client, "Assist Away")

    playmaker = _create_player(client, "Playmaker", home_team["id"], "AM")
    winger = _create_player(client, "Creator", away_team["id"], "RW")

    match = _create_match(client, home_team["id"], away_team["id"], 2, 2, "2025-10-08")

    _create_event(client, match["id"], home_team["id"], playmaker["id"], 25, "assist", "Cross")
    _create_event(client, match["id"], home_team["id"], playmaker["id"], 60, "assist", "Through ball")
    _create_event(client, match["id"], away_team["id"], winger["id"], 72, "assist", "Cutback")

    response = client.get("/analytics/most-assists", params={"season": "2025/26", "limit": 2})

    assert response.status_code == 200
    body = response.json()
    assert body["season"] == "2025/26"
    assert body["events_considered"] == 3
    assert len(body["most_assists"]) == 2
    assert body["most_assists"][0]["player_name"] == "Playmaker"
    assert body["most_assists"][0]["assists"] == 2
    assert body["most_assists"][1]["player_name"] == "Creator"
    assert body["most_assists"][1]["assists"] == 1
    _assert_metadata(body)


def test_team_strength_endpoint_returns_ranked_ratings(client: TestClient) -> None:
    team_a = _create_team(client, "Strength A")
    team_b = _create_team(client, "Strength B")
    team_c = _create_team(client, "Strength C")

    _create_match(client, team_a["id"], team_b["id"], 2, 0, "2025-07-01")
    _create_match(client, team_b["id"], team_c["id"], 1, 0, "2025-07-08")
    _create_match(client, team_a["id"], team_c["id"], 1, 1, "2025-07-15")

    response = client.get("/analytics/team-strength", params={"season": "2025/26"})

    assert response.status_code == 200
    body = response.json()
    assert body["season"] == "2025/26"
    assert body["base_rating"] == 1500.0
    assert body["k_factor"] == 32.0
    assert len(body["teams"]) == 3
    assert body["teams"][0]["rank"] == 1
    assert "rating" in body["teams"][0]
    _assert_metadata(body)


def test_player_impact_endpoint_returns_ranked_scores(client: TestClient) -> None:
    team_home = _create_team(client, "Impact Home")
    team_away = _create_team(client, "Impact Away")

    player_one = _create_player(client, "Impact One", team_home["id"], "FW")
    player_two = _create_player(client, "Impact Two", team_away["id"], "FW")

    match = _create_match(client, team_home["id"], team_away["id"], 2, 1, "2025-11-01")

    _create_event(client, match["id"], team_home["id"], player_one["id"], 10, "goal", "Goal")
    _create_event(client, match["id"], team_home["id"], player_one["id"], 20, "assist", "Assist")
    _create_event(client, match["id"], team_home["id"], player_one["id"], 30, "shot_on_target", "Shot OT")

    _create_event(client, match["id"], team_away["id"], player_two["id"], 40, "goal", "Goal")
    _create_event(client, match["id"], team_away["id"], player_two["id"], 50, "yellow_card", "Yellow")

    response = client.get("/analytics/player-impact", params={"season": "2025/26", "limit": 5})

    assert response.status_code == 200
    body = response.json()
    assert body["season"] == "2025/26"
    assert body["events_considered"] == 5
    assert len(body["players"]) == 2
    assert body["players"][0]["player_name"] == "Impact One"
    assert body["players"][0]["impact_score"] == 9.0
    assert body["players"][1]["player_name"] == "Impact Two"
    assert body["players"][1]["impact_score"] == 4.5
    _assert_metadata(body)


def test_clutch_impact_endpoint_returns_explainable_ranking(client: TestClient) -> None:
    team_home = _create_team(client, "Clutch Home")
    team_away = _create_team(client, "Clutch Away")

    player_home = _create_player(client, "Clutch Home Player", team_home["id"], "FW")
    player_away = _create_player(client, "Clutch Away Player", team_away["id"], "FW")

    match = _create_match(
        client,
        team_home["id"],
        team_away["id"],
        home_score=1,
        away_score=2,
        match_date="2025-12-01",
    )

    _create_event(client, match["id"], team_home["id"], player_home["id"], 88, "goal", "Late goal")
    _create_event(client, match["id"], team_away["id"], player_away["id"], 20, "goal", "Early goal")

    response = client.get("/analytics/clutch-impact", params={"season": "2025/26", "limit": 5})

    assert response.status_code == 200
    body = response.json()
    assert body["season"] == "2025/26"
    assert body["events_considered"] == 2
    assert "points won from goal and assist contributions only" in body["methodology"]
    assert len(body["players"]) == 1
    assert body["players"][0]["player_name"] == "Clutch Away Player"
    assert len(body["players"][0]["top_contributions"]) >= 1
    assert body["players"][0]["top_contributions"][0]["points_awarded"] == 3
    assert body["players"][0]["top_contributions"][0]["event_type"] == "goal"
    assert "reason" in body["players"][0]["top_contributions"][0]
    _assert_metadata(body)
