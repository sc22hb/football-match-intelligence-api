"""team form analytics calculations based on recent matches."""

from datetime import date

from app.models.match import Match



def calculate_team_form(matches: list[Match], team_id: int) -> dict[str, object]:
    wins = 0
    draws = 0
    losses = 0
    points = 0
    recent_results: list[dict[str, object]] = []

    for match in matches:
        is_home = match.home_team_id == team_id
        goals_for = match.home_score if is_home else match.away_score
        goals_against = match.away_score if is_home else match.home_score
        opponent_team_id = match.away_team_id if is_home else match.home_team_id

        if goals_for > goals_against:
            result = "W"
            wins += 1
            points += 3
            points_awarded = 3
            explanation = "Win contributes 3 points."
        elif goals_for == goals_against:
            result = "D"
            draws += 1
            points += 1
            points_awarded = 1
            explanation = "Draw contributes 1 point."
        else:
            result = "L"
            losses += 1
            points_awarded = 0
            explanation = "Loss contributes 0 points."

        recent_results.append(
            {
                "match_id": match.id,
                "match_date": match.match_date,
                "opponent_team_id": opponent_team_id,
                "goals_for": goals_for,
                "goals_against": goals_against,
                "result": result,
                "points_awarded": points_awarded,
                "explanation": explanation,
            }
        )

    match_count = len(matches)
    form_score = round((points / (match_count * 3)) * 100, 2) if match_count else 0.0

    return {
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "points": points,
        "matches_considered": match_count,
        "form_score": form_score,
        "explanation_summary": (
            f"Form score is based on {match_count} recent matches: "
            f"{wins}W-{draws}D-{losses}L, {points} points from a maximum of {match_count * 3}."
            if match_count
            else "No recent matches found. Form score is 0."
        ),
        "recent_results": recent_results,
    }
