"""players http endpoints and response handling."""

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.player import PlayerCreate, PlayerListResponse, PlayerRead, PlayerUpdate
from app.services.errors import ConflictError, NotFoundError
from app.services.player_service import PlayerService

router = APIRouter(prefix="/players", tags=["players"])
service = PlayerService()



def _error_payload(code: str, message: str) -> dict[str, dict[str, str]]:
    return {"error": {"code": code, "message": message}}


@router.post("", response_model=PlayerRead, status_code=status.HTTP_201_CREATED)
def create_player(payload: PlayerCreate, db: Session = Depends(get_db)) -> PlayerRead:
    try:
        player = service.create_player(db=db, payload=payload)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_error_payload("TEAM_NOT_FOUND", str(exc)),
        ) from exc
    except ConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=_error_payload("PLAYER_ALREADY_EXISTS", str(exc)),
        ) from exc

    return PlayerRead.model_validate(player)


@router.get("", response_model=PlayerListResponse)
def list_players(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> PlayerListResponse:
    players, total = service.list_players(db=db, skip=skip, limit=limit)
    return PlayerListResponse(
        items=[PlayerRead.model_validate(player) for player in players],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{player_id}", response_model=PlayerRead)
def get_player(player_id: int, db: Session = Depends(get_db)) -> PlayerRead:
    try:
        player = service.get_player(db=db, player_id=player_id)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_error_payload("PLAYER_NOT_FOUND", str(exc)),
        ) from exc

    return PlayerRead.model_validate(player)


@router.put("/{player_id}", response_model=PlayerRead)
def update_player(
    player_id: int,
    payload: PlayerUpdate,
    db: Session = Depends(get_db),
) -> PlayerRead:
    try:
        player = service.update_player(db=db, player_id=player_id, payload=payload)
    except NotFoundError as exc:
        message = str(exc)
        code = "TEAM_NOT_FOUND" if "Team" in message else "PLAYER_NOT_FOUND"
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_error_payload(code, message),
        ) from exc
    except ConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=_error_payload("PLAYER_ALREADY_EXISTS", str(exc)),
        ) from exc

    return PlayerRead.model_validate(player)


@router.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_player(player_id: int, db: Session = Depends(get_db)) -> Response:
    try:
        service.delete_player(db=db, player_id=player_id)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_error_payload("PLAYER_NOT_FOUND", str(exc)),
        ) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)
