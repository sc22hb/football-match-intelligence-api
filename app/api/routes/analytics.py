"""analytics http endpoints and response handling."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.analytics import LeagueTableResponse, TeamFormResponse
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


@router.get("/league-table", response_model=LeagueTableResponse)
def get_league_table(
    season: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> LeagueTableResponse:
    return service.get_league_table(db=db, season=season)
