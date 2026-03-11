"""player impact analytics calculations from event-level data."""

from app.models.event import Event



def _normalize_event_type(value: str) -> str:
    return value.strip().lower().replace(" ", "_").replace("-", "_")



def calculate_player_impact(events: list[Event]) -> list[dict[str, float]]:
    metrics: dict[int, dict[str, float]] = {}

    for event in events:
        row = metrics.setdefault(
            event.player_id,
            {
                "player_id": event.player_id,
                "team_id": event.team_id,
                "goals": 0,
                "assists": 0,
                "shots_on_target": 0,
                "saves": 0,
                "yellow_cards": 0,
                "red_cards": 0,
            },
        )

        event_type = _normalize_event_type(event.event_type)
        if event_type == "goal":
            row["goals"] += 1
        elif event_type == "assist":
            row["assists"] += 1
        elif event_type in {"shot_on_target", "shotontarget"}:
            row["shots_on_target"] += 1
        elif event_type == "save":
            row["saves"] += 1
        elif event_type == "yellow_card":
            row["yellow_cards"] += 1
        elif event_type == "red_card":
            row["red_cards"] += 1

    rows = list(metrics.values())
    for row in rows:
        impact_score = (
            (row["goals"] * 5)
            + (row["assists"] * 3)
            + (row["shots_on_target"] * 1)
            + (row["saves"] * 0.2)
            - (row["yellow_cards"] * 0.5)
            - (row["red_cards"] * 2)
        )
        row["impact_score"] = round(impact_score, 2)

    rows.sort(key=lambda r: (-r["impact_score"], r["player_id"]))
    for idx, row in enumerate(rows, start=1):
        row["rank"] = idx

    return rows
