"""pydantic schemas for analytics endpoints."""

from datetime import date

from pydantic import BaseModel


class TeamFormMatchResult(BaseModel):
    match_id: int
    match_date: date
    opponent_team_id: int
    goals_for: int
    goals_against: int
    result: str


class TeamFormResponse(BaseModel):
    team_id: int
    matches_considered: int
    wins: int
    draws: int
    losses: int
    points: int
    form_score: float
    recent_results: list[TeamFormMatchResult]
