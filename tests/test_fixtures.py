"""fixtures and prediction endpoint tests."""

from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.fixture import Fixture


def _create_team(client: TestClient, name: str) -> dict[str, object]:
    response = client.post(
        "/teams",
        json={"name": name, "league": "Premier League", "country": "England"},
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


def test_list_fixtures_returns_upcoming_rows(client: TestClient, db_session: Session) -> None:
    team_a = _create_team(client, "Fixture A")
    team_b = _create_team(client, "Fixture B")

    db_session.add(
        Fixture(
            home_team_id=team_a["id"],
            away_team_id=team_b["id"],
            fixture_date=date(2026, 3, 14),
            season="2025/26",
        )
    )
    db_session.commit()

    response = client.get("/fixtures", params={"season": "2025/26"})
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["fixture_date"] == "2026-03-14"


def test_fixture_predictions_returns_probabilities(client: TestClient, db_session: Session) -> None:
    team_a = _create_team(client, "Prediction A")
    team_b = _create_team(client, "Prediction B")
    team_c = _create_team(client, "Prediction C")

    _create_match(client, team_a["id"], team_b["id"], 2, 0, "2025-08-01")
    _create_match(client, team_a["id"], team_c["id"], 1, 0, "2025-08-08")
    _create_match(client, team_b["id"], team_c["id"], 0, 0, "2025-08-15")

    db_session.add(
        Fixture(
            home_team_id=team_a["id"],
            away_team_id=team_b["id"],
            fixture_date=date(2026, 3, 14),
            season="2025/26",
        )
    )
    db_session.commit()

    response = client.get("/analytics/fixture-predictions", params={"season": "2025/26", "limit": 5})
    assert response.status_code == 200
    body = response.json()
    assert body["fixtures_considered"] == 1
    row = body["predictions"][0]
    assert row["home_team_name"] == "Prediction A"
    assert row["away_team_name"] == "Prediction B"
    assert row["home_win_probability"] > row["away_win_probability"]
    assert round(row["home_win_probability"] + row["draw_probability"] + row["away_win_probability"], 3) == 1.0
