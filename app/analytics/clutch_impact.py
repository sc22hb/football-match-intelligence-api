"""clutch impact analytics using event context and opponent strength."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ClutchEventContext:
    player_id: int
    team_id: int
    match_id: int
    minute: int
    event_type: str
    opponent_team_id: int
    game_state: str


def _normalize_event_type(value: str) -> str:
    return value.strip().lower().replace(" ", "_").replace("-", "_")


def _minute_weight(minute: int) -> float:
    if minute <= 60:
        return 1.0
    if minute <= 80:
        return 1.2
    return 1.5


def _game_state_weight(game_state: str) -> float:
    normalized = game_state.strip().lower()
    if normalized == "losing":
        return 1.5
    if normalized == "drawing":
        return 1.2
    return 1.0


def _opponent_strength_weight(opponent_rating: float) -> float:
    raw = 1 + ((opponent_rating - 1500.0) / 1000.0)
    return max(0.8, min(1.2, raw))


def calculate_clutch_impact(
    event_contexts: list[ClutchEventContext],
    team_ratings: dict[int, float],
) -> list[dict[str, object]]:
    base_values: dict[str, float] = {
        "goal": 5.0,
        "assist": 3.0,
        "shot_on_target": 1.0,
        "shotontarget": 1.0,
        "yellow_card": -0.5,
        "red_card": -2.0,
    }

    grouped: dict[int, dict[str, object]] = {}

    for event in event_contexts:
        normalized_event = _normalize_event_type(event.event_type)
        base_value = base_values.get(normalized_event)
        if base_value is None:
            continue

        minute_weight = _minute_weight(event.minute)
        game_state_weight = _game_state_weight(event.game_state)
        opponent_rating = team_ratings.get(event.opponent_team_id, 1500.0)
        opponent_weight = _opponent_strength_weight(opponent_rating)

        contribution = base_value * minute_weight * game_state_weight * opponent_weight

        row = grouped.setdefault(
            event.player_id,
            {
                "player_id": event.player_id,
                "team_id": event.team_id,
                "events_count": 0,
                "clutch_impact_score": 0.0,
                "contributions": [],
            },
        )
        row["events_count"] += 1
        row["clutch_impact_score"] += contribution
        row["contributions"].append(
            {
                "match_id": event.match_id,
                "minute": event.minute,
                "event_type": normalized_event,
                "base_value": base_value,
                "minute_weight": minute_weight,
                "game_state_weight": game_state_weight,
                "opponent_strength_weight": round(opponent_weight, 3),
                "contribution": round(contribution, 3),
                "reason": (
                    f"{normalized_event} at {event.minute}' with "
                    f"minute={minute_weight}, game_state={game_state_weight}, "
                    f"opponent_strength={round(opponent_weight, 3)}."
                ),
            }
        )

    rows = list(grouped.values())
    for row in rows:
        row["clutch_impact_score"] = round(row["clutch_impact_score"], 3)
        contributions = row["contributions"]
        contributions.sort(key=lambda item: abs(item["contribution"]), reverse=True)
        row["top_contributions"] = contributions[:3]
        del row["contributions"]

    rows.sort(key=lambda item: (-item["clutch_impact_score"], item["player_id"]))
    for idx, row in enumerate(rows, start=1):
        row["rank"] = idx

    return rows
