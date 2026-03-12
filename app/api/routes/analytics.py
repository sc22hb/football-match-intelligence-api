"""analytics http endpoints and response handling."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.docs import TEAM_NOT_FOUND_RESPONSE
from app.db.session import get_db
from app.schemas.analytics import (
    ClutchImpactResponse,
    FixturePredictionsResponse,
    LeagueTableResponse,
    MostAssistsResponse,
    PlayerImpactResponse,
    TeamFormResponse,
    TeamStrengthResponse,
    TopScorersResponse,
)
from app.services.analytics_service import AnalyticsService
from app.services.errors import NotFoundError

router = APIRouter(prefix="/analytics", tags=["analytics"])
service = AnalyticsService()



def _error_payload(code: str, message: str) -> dict[str, dict[str, str]]:
    return {"error": {"code": code, "message": message}}


@router.get(
    "/team-form/{team_id}",
    response_model=TeamFormResponse,
    summary="Get team form",
    description="Returns an explainable recent-form score for a specific team.",
    responses={404: TEAM_NOT_FOUND_RESPONSE},
)
def get_team_form(team_id: int, db: Session = Depends(get_db)) -> TeamFormResponse:
    try:
        return service.get_team_form(db=db, team_id=team_id)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_error_payload("TEAM_NOT_FOUND", str(exc)),
        ) from exc


@router.get(
    "/team-strength",
    response_model=TeamStrengthResponse,
    summary="Get team strength table",
    description="Returns an ELO-style ranking of teams for the selected season.",
)
def get_team_strength(
    season: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> TeamStrengthResponse:
    return service.get_team_strength(db=db, season=season)


@router.get(
    "/league-table",
    response_model=LeagueTableResponse,
    summary="Get league table",
    description="Returns a computed league table for the selected season.",
)
def get_league_table(
    season: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> LeagueTableResponse:
    return service.get_league_table(db=db, season=season)


@router.get(
    "/top-scorers",
    response_model=TopScorersResponse,
    summary="Get top scorers",
    description="Returns the highest-scoring players in the selected season.",
)
def get_top_scorers(
    season: str | None = Query(default=None),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
) -> TopScorersResponse:
    return service.get_top_scorers(db=db, season=season, limit=limit)


@router.get(
    "/most-assists",
    response_model=MostAssistsResponse,
    summary="Get most assists",
    description="Returns the leading assist providers in the selected season.",
)
def get_most_assists(
    season: str | None = Query(default=None),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
) -> MostAssistsResponse:
    return service.get_most_assists(db=db, season=season, limit=limit)


@router.get(
    "/player-impact",
    response_model=PlayerImpactResponse,
    summary="Get player impact ranking",
    description="Returns a weighted player impact ranking based on goals, assists, saves, and discipline.",
)
def get_player_impact(
    season: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> PlayerImpactResponse:
    return service.get_player_impact(db=db, season=season, limit=limit)


@router.get(
    "/clutch-impact",
    response_model=ClutchImpactResponse,
    summary="Get clutch impact ranking",
    description="Returns player rankings based on weighted points won by decisive goals and assists.",
)
def get_clutch_impact(
    season: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> ClutchImpactResponse:
    return service.get_clutch_impact(db=db, season=season, limit=limit)


@router.get(
    "/fixture-predictions",
    response_model=FixturePredictionsResponse,
    summary="Get fixture predictions",
    description="Returns upcoming fixture win probabilities and expected goals using strength, form, and home advantage.",
)
def get_fixture_predictions(
    season: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> FixturePredictionsResponse:
    return service.get_fixture_predictions(db=db, season=season, limit=limit)
