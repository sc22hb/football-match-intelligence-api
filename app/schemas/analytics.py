"""pydantic schemas for analytics endpoints."""

from datetime import date, datetime

from pydantic import BaseModel


class AnalyticsMetadata(BaseModel):
    data_source: str
    dataset_name: str
    dataset_version: str
    computed_at: datetime


class TeamFormMatchResult(BaseModel):
    match_id: int
    match_date: date
    opponent_team_id: int
    goals_for: int
    goals_against: int
    result: str
    points_awarded: int
    explanation: str


class TeamFormResponse(BaseModel):
    team_id: int
    matches_considered: int
    wins: int
    draws: int
    losses: int
    points: int
    form_score: float
    explanation_summary: str
    recent_results: list[TeamFormMatchResult]
    metadata: AnalyticsMetadata


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
    metadata: AnalyticsMetadata


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
    metadata: AnalyticsMetadata


class MostAssistsRow(BaseModel):
    rank: int
    player_id: int
    player_name: str
    team_id: int
    team_name: str
    assists: int


class MostAssistsResponse(BaseModel):
    season: str | None
    events_considered: int
    most_assists: list[MostAssistsRow]
    metadata: AnalyticsMetadata


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
    metadata: AnalyticsMetadata


class PlayerImpactRow(BaseModel):
    rank: int
    player_id: int
    player_name: str
    team_id: int
    team_name: str
    goals: int
    assists: int
    shots_on_target: int
    saves: int
    yellow_cards: int
    red_cards: int
    impact_score: float


class PlayerImpactResponse(BaseModel):
    season: str | None
    events_considered: int
    players: list[PlayerImpactRow]
    metadata: AnalyticsMetadata


class ClutchImpactContribution(BaseModel):
    match_id: int
    event_type: str
    weight: float
    points_awarded: int
    contribution: float
    reason: str


class ClutchImpactRow(BaseModel):
    rank: int
    player_id: int
    player_name: str
    team_id: int
    team_name: str
    events_count: int
    clutch_impact_score: float
    top_contributions: list[ClutchImpactContribution]


class ClutchImpactResponse(BaseModel):
    season: str | None
    events_considered: int
    methodology: str
    players: list[ClutchImpactRow]
    metadata: AnalyticsMetadata
