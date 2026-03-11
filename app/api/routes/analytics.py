"""analytics http endpoints and response handling."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

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


@router.get("/team-form/{team_id}", response_model=TeamFormResponse)
def get_team_form(team_id: int, db: Session = Depends(get_db)) -> TeamFormResponse:
    try:
        return service.get_team_form(db=db, team_id=team_id)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_error_payload("TEAM_NOT_FOUND", str(exc)),
        ) from exc


@router.get("/team-strength", response_model=TeamStrengthResponse)
def get_team_strength(
    season: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> TeamStrengthResponse:
    return service.get_team_strength(db=db, season=season)


@router.get("/league-table", response_model=LeagueTableResponse)
def get_league_table(
    season: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> LeagueTableResponse:
    return service.get_league_table(db=db, season=season)


@router.get("/top-scorers", response_model=TopScorersResponse)
def get_top_scorers(
    season: str | None = Query(default=None),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
) -> TopScorersResponse:
    return service.get_top_scorers(db=db, season=season, limit=limit)


@router.get("/most-assists", response_model=MostAssistsResponse)
def get_most_assists(
    season: str | None = Query(default=None),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
) -> MostAssistsResponse:
    return service.get_most_assists(db=db, season=season, limit=limit)


@router.get("/player-impact", response_model=PlayerImpactResponse)
def get_player_impact(
    season: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> PlayerImpactResponse:
    return service.get_player_impact(db=db, season=season, limit=limit)


@router.get("/clutch-impact", response_model=ClutchImpactResponse)
def get_clutch_impact(
    season: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> ClutchImpactResponse:
    return service.get_clutch_impact(db=db, season=season, limit=limit)


@router.get("/fixture-predictions", response_model=FixturePredictionsResponse)
def get_fixture_predictions(
    season: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> FixturePredictionsResponse:
    return service.get_fixture_predictions(db=db, season=season, limit=limit)
