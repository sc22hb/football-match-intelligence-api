"""exports pydantic schema classes."""

from app.schemas.analytics import (
    AnalyticsMetadata,
    FixturePredictionsResponse,
    LeagueTableResponse,
    LeagueTableRow,
    MostAssistsResponse,
    PlayerImpactResponse,
    PlayerImpactRow,
    TeamFormMatchResult,
    TeamFormResponse,
    TeamStrengthResponse,
    TeamStrengthRow,
    TopScorerRow,
    TopScorersResponse,
)
from app.schemas.fixture import FixtureListResponse, FixtureRead
from app.schemas.event import EventCreate, EventListResponse, EventRead
from app.schemas.match import MatchCreate, MatchListResponse, MatchRead, MatchUpdate
from app.schemas.player import PlayerCreate, PlayerListResponse, PlayerRead, PlayerUpdate
from app.schemas.team import TeamCreate, TeamListResponse, TeamRead, TeamUpdate

__all__ = [
    "TeamCreate",
    "TeamListResponse",
    "TeamRead",
    "TeamUpdate",
    "PlayerCreate",
    "PlayerListResponse",
    "PlayerRead",
    "PlayerUpdate",
    "MatchCreate",
    "MatchListResponse",
    "MatchRead",
    "MatchUpdate",
    "EventCreate",
    "EventListResponse",
    "EventRead",
    "AnalyticsMetadata",
    "FixturePredictionsResponse",
    "FixtureRead",
    "FixtureListResponse",
    "LeagueTableRow",
    "LeagueTableResponse",
    "MostAssistsResponse",
    "PlayerImpactRow",
    "PlayerImpactResponse",
    "TeamFormMatchResult",
    "TeamFormResponse",
    "TeamStrengthRow",
    "TeamStrengthResponse",
    "TopScorerRow",
    "TopScorersResponse",
]
