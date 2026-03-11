"""clutch impact analytics based on points won by goals and assists."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ClutchEventContext:
    player_id: int
    team_id: int
    match_id: int
    minute: int
    event_type: str
    points_awarded: int


def _normalize_event_type(value: str) -> str:
    return value.strip().lower().replace(" ", "_").replace("-", "_")


def _event_weight(event_type: str) -> float | None:
    weights = {
        "goal": 1.0,
        "assist": 0.65,
    }
    return weights.get(_normalize_event_type(event_type))


def calculate_clutch_impact(
    event_contexts: list[ClutchEventContext],
) -> list[dict[str, object]]:
    events_by_match_team: dict[tuple[int, int], list[ClutchEventContext]] = {}
    for event in event_contexts:
        weight = _event_weight(event.event_type)
        if weight is None or event.points_awarded <= 0:
            continue
        events_by_match_team.setdefault((event.match_id, event.team_id), []).append(event)

    grouped: dict[int, dict[str, object]] = {}

    for (match_id, team_id), events in events_by_match_team.items():
        total_weight = sum(_event_weight(event.event_type) or 0.0 for event in events)
        if total_weight <= 0:
            continue

        points_awarded = events[0].points_awarded
        for event in events:
            normalized_event = _normalize_event_type(event.event_type)
            event_weight = _event_weight(event.event_type) or 0.0
            contribution = points_awarded * (event_weight / total_weight)

            row = grouped.setdefault(
                event.player_id,
                {
                    "player_id": event.player_id,
                    "team_id": team_id,
                    "events_count": 0,
                    "clutch_impact_score": 0.0,
                    "contributions": [],
                },
            )
            row["events_count"] += 1
            row["clutch_impact_score"] += contribution
            row["contributions"].append(
                {
                    "match_id": match_id,
                    "event_type": normalized_event,
                    "weight": round(event_weight, 3),
                    "points_awarded": points_awarded,
                    "contribution": round(contribution, 3),
                    "reason": (
                        f"{normalized_event} contributed a weighted share of the team's "
                        f"{points_awarded} point result."
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
