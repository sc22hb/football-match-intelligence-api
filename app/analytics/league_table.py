"""league table analytics calculations from match results."""

from app.models.match import Match



def calculate_league_table(matches: list[Match]) -> list[dict[str, int]]:
    table: dict[int, dict[str, int]] = {}

    for match in matches:
        home = table.setdefault(
            match.home_team_id,
            {
                "team_id": match.home_team_id,
                "played": 0,
                "wins": 0,
                "draws": 0,
                "losses": 0,
                "goals_for": 0,
                "goals_against": 0,
                "goal_difference": 0,
                "points": 0,
            },
        )
        away = table.setdefault(
            match.away_team_id,
            {
                "team_id": match.away_team_id,
                "played": 0,
                "wins": 0,
                "draws": 0,
                "losses": 0,
                "goals_for": 0,
                "goals_against": 0,
                "goal_difference": 0,
                "points": 0,
            },
        )

        home["played"] += 1
        away["played"] += 1

        home["goals_for"] += match.home_score
        home["goals_against"] += match.away_score
        away["goals_for"] += match.away_score
        away["goals_against"] += match.home_score

        if match.home_score > match.away_score:
            home["wins"] += 1
            home["points"] += 3
            away["losses"] += 1
        elif match.home_score < match.away_score:
            away["wins"] += 1
            away["points"] += 3
            home["losses"] += 1
        else:
            home["draws"] += 1
            away["draws"] += 1
            home["points"] += 1
            away["points"] += 1

    rows = list(table.values())
    for row in rows:
        row["goal_difference"] = row["goals_for"] - row["goals_against"]

    rows.sort(
        key=lambda r: (
            -r["points"],
            -r["goal_difference"],
            -r["goals_for"],
            r["team_id"],
        )
    )

    for idx, row in enumerate(rows, start=1):
        row["position"] = idx

    return rows
