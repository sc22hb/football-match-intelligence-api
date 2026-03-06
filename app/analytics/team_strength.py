"""team strength (elo-style) analytics calculations."""

from app.models.match import Match



def calculate_team_strength(
    matches: list[Match],
    team_ids: set[int],
    base_rating: float = 1500.0,
    k_factor: float = 32.0,
) -> dict[int, dict[str, float]]:
    ratings = {team_id: base_rating for team_id in team_ids}
    played = {team_id: 0 for team_id in team_ids}

    ordered_matches = sorted(matches, key=lambda m: (m.match_date, m.id))

    for match in ordered_matches:
        home_id = match.home_team_id
        away_id = match.away_team_id

        home_rating = ratings.get(home_id, base_rating)
        away_rating = ratings.get(away_id, base_rating)

        expected_home = 1.0 / (1.0 + 10 ** ((away_rating - home_rating) / 400))
        expected_away = 1.0 / (1.0 + 10 ** ((home_rating - away_rating) / 400))

        if match.home_score > match.away_score:
            actual_home = 1.0
            actual_away = 0.0
        elif match.home_score < match.away_score:
            actual_home = 0.0
            actual_away = 1.0
        else:
            actual_home = 0.5
            actual_away = 0.5

        ratings[home_id] = home_rating + k_factor * (actual_home - expected_home)
        ratings[away_id] = away_rating + k_factor * (actual_away - expected_away)

        played[home_id] = played.get(home_id, 0) + 1
        played[away_id] = played.get(away_id, 0) + 1

    return {
        team_id: {
            "rating": round(ratings.get(team_id, base_rating), 2),
            "matches_played": int(played.get(team_id, 0)),
        }
        for team_id in team_ids
    }
