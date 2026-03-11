"""teams http endpoints and response handling."""

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.core.security import require_write_access
from app.db.session import get_db
from app.schemas.team import TeamCreate, TeamListResponse, TeamRead, TeamUpdate
from app.services.errors import ConflictError, NotFoundError
from app.services.team_service import TeamService

router = APIRouter(prefix="/teams", tags=["teams"])
service = TeamService()



def _error_payload(code: str, message: str) -> dict[str, dict[str, str]]:
    return {"error": {"code": code, "message": message}}


@router.post("", response_model=TeamRead, status_code=status.HTTP_201_CREATED)
def create_team(
    payload: TeamCreate,
    db: Session = Depends(get_db),
    _: None = Depends(require_write_access),
) -> TeamRead:
    try:
        team = service.create_team(db=db, payload=payload)
    except ConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=_error_payload("TEAM_ALREADY_EXISTS", str(exc)),
        ) from exc

    return TeamRead.model_validate(team)


@router.get("", response_model=TeamListResponse)
def list_teams(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> TeamListResponse:
    teams, total = service.list_teams(db=db, skip=skip, limit=limit)
    return TeamListResponse(
        items=[TeamRead.model_validate(team) for team in teams],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{team_id}", response_model=TeamRead)
def get_team(team_id: int, db: Session = Depends(get_db)) -> TeamRead:
    try:
        team = service.get_team(db=db, team_id=team_id)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_error_payload("TEAM_NOT_FOUND", str(exc)),
        ) from exc

    return TeamRead.model_validate(team)


@router.put("/{team_id}", response_model=TeamRead)
def update_team(
    team_id: int,
    payload: TeamUpdate,
    db: Session = Depends(get_db),
    _: None = Depends(require_write_access),
) -> TeamRead:
    try:
        team = service.update_team(db=db, team_id=team_id, payload=payload)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_error_payload("TEAM_NOT_FOUND", str(exc)),
        ) from exc
    except ConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=_error_payload("TEAM_ALREADY_EXISTS", str(exc)),
        ) from exc

    return TeamRead.model_validate(team)


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_team(
    team_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_write_access),
) -> Response:
    try:
        service.delete_team(db=db, team_id=team_id)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_error_payload("TEAM_NOT_FOUND", str(exc)),
        ) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)
