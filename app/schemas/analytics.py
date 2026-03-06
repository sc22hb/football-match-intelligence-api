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


class LeagueTableRow(BaseModel):
    position: int
    team_id: int
    team_name: str
    played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    goal_difference: int
    points: int


class LeagueTableResponse(BaseModel):
    season: str | None
    matches_considered: int
    table: list[LeagueTableRow]


class TopScorerRow(BaseModel):
    rank: int
    player_id: int
    player_name: str
    team_id: int
    team_name: str
    goals: int


class TopScorersResponse(BaseModel):
    season: str | None
    events_considered: int
    top_scorers: list[TopScorerRow]


class TeamStrengthRow(BaseModel):
    rank: int
    team_id: int
    team_name: str
    rating: float
    matches_played: int


class TeamStrengthResponse(BaseModel):
    season: str | None
    base_rating: float
    k_factor: float
    teams: list[TeamStrengthRow]
