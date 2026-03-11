"""fixture win-probability predictions based on team strength and recent form."""

from __future__ import annotations

from math import exp

from app.models.fixture import Fixture
from app.models.match import Match


def _recent_form_points(matches: list[Match], team_id: int) -> int:
    points = 0
    for match in matches:
        if match.home_team_id == team_id:
            if match.home_score > match.away_score:
                points += 3
            elif match.home_score == match.away_score:
                points += 1
        elif match.away_team_id == team_id:
            if match.away_score > match.home_score:
                points += 3
            elif match.away_score == match.home_score:
                points += 1
    return points


def _sigmoid(value: float) -> float:
    return 1 / (1 + exp(-value))


def predict_fixture(
    fixture: Fixture,
    ratings: dict[int, float],
    recent_matches_by_team: dict[int, list[Match]],
) -> dict[str, float | int | str]:
    home_rating = ratings.get(fixture.home_team_id, 1500.0)
    away_rating = ratings.get(fixture.away_team_id, 1500.0)

    home_form_points = _recent_form_points(recent_matches_by_team.get(fixture.home_team_id, []), fixture.home_team_id)
    away_form_points = _recent_form_points(recent_matches_by_team.get(fixture.away_team_id, []), fixture.away_team_id)

    rating_edge = (home_rating - away_rating) / 100.0
    form_edge = (home_form_points - away_form_points) / 6.0
    home_advantage = 0.35
    strength_score = rating_edge + form_edge + home_advantage

    draw_probability = max(0.16, 0.28 - (abs(strength_score) * 0.03))
    decisive_probability = 1.0 - draw_probability
    home_share = _sigmoid(strength_score)

    home_win_probability = round(decisive_probability * home_share, 3)
    draw_probability = round(draw_probability, 3)
    away_win_probability = round(max(0.0, 1.0 - home_win_probability - draw_probability), 3)

    predicted_home_goals = round(max(0.2, 1.35 + (strength_score * 0.45)), 2)
    predicted_away_goals = round(max(0.2, 1.15 - (strength_score * 0.35)), 2)

    return {
        "fixture_id": fixture.id,
        "fixture_date": fixture.fixture_date,
        "home_team_id": fixture.home_team_id,
        "away_team_id": fixture.away_team_id,
        "home_win_probability": home_win_probability,
        "draw_probability": draw_probability,
        "away_win_probability": away_win_probability,
        "predicted_home_goals": predicted_home_goals,
        "predicted_away_goals": predicted_away_goals,
        "explanation": (
            f"Prediction blends team strength, last-five form, and a home advantage boost. "
            f"Home form points={home_form_points}, away form points={away_form_points}."
        ),
    }
