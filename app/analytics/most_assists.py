"""most assists analytics calculations from assist events."""

from app.models.event import Event


def calculate_most_assists(events: list[Event]) -> list[dict[str, int]]:
    assists: dict[int, dict[str, int]] = {}

    for event in events:
        row = assists.setdefault(
            event.player_id,
            {
                "player_id": event.player_id,
                "team_id": event.team_id,
                "assists": 0,
            },
        )
        row["assists"] += 1

    rows = list(assists.values())
    rows.sort(key=lambda r: (-r["assists"], r["player_id"]))

    for idx, row in enumerate(rows, start=1):
        row["rank"] = idx

    return rows
