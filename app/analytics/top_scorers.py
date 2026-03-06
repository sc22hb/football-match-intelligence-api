"""top scorer analytics calculations from goal events."""

from app.models.event import Event



def calculate_top_scorers(events: list[Event]) -> list[dict[str, int]]:
    scorers: dict[int, dict[str, int]] = {}

    for event in events:
        row = scorers.setdefault(
            event.player_id,
            {
                "player_id": event.player_id,
                "team_id": event.team_id,
                "goals": 0,
            },
        )
        row["goals"] += 1

    rows = list(scorers.values())
    rows.sort(key=lambda r: (-r["goals"], r["player_id"]))

    for idx, row in enumerate(rows, start=1):
        row["rank"] = idx

    return rows
