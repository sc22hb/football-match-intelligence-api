"""matches http endpoints and response handling."""

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.core.security import require_write_access
from app.db.session import get_db
from app.schemas.match import MatchCreate, MatchListResponse, MatchRead, MatchUpdate
from app.services.errors import NotFoundError, ServiceValidationError
from app.services.match_service import MatchService

router = APIRouter(prefix="/matches", tags=["matches"])
service = MatchService()



def _error_payload(code: str, message: str) -> dict[str, dict[str, str]]:
    return {"error": {"code": code, "message": message}}


@router.post("", response_model=MatchRead, status_code=status.HTTP_201_CREATED)
def create_match(
    payload: MatchCreate,
    db: Session = Depends(get_db),
    _: None = Depends(require_write_access),
) -> MatchRead:
    try:
        match = service.create_match(db=db, payload=payload)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_error_payload("TEAM_NOT_FOUND", str(exc)),
        ) from exc
    except ServiceValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=_error_payload("INVALID_MATCH_TEAMS", str(exc)),
        ) from exc

    return MatchRead.model_validate(match)


@router.get("", response_model=MatchListResponse)
def list_matches(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> MatchListResponse:
    matches, total = service.list_matches(db=db, skip=skip, limit=limit)
    return MatchListResponse(
        items=[MatchRead.model_validate(match) for match in matches],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{match_id}", response_model=MatchRead)
def get_match(match_id: int, db: Session = Depends(get_db)) -> MatchRead:
    try:
        match = service.get_match(db=db, match_id=match_id)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_error_payload("MATCH_NOT_FOUND", str(exc)),
        ) from exc

    return MatchRead.model_validate(match)


@router.put("/{match_id}", response_model=MatchRead)
def update_match(
    match_id: int,
    payload: MatchUpdate,
    db: Session = Depends(get_db),
    _: None = Depends(require_write_access),
) -> MatchRead:
    try:
        match = service.update_match(db=db, match_id=match_id, payload=payload)
    except NotFoundError as exc:
        message = str(exc)
        code = "TEAM_NOT_FOUND" if "Team" in message else "MATCH_NOT_FOUND"
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_error_payload(code, message),
        ) from exc
    except ServiceValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=_error_payload("INVALID_MATCH_TEAMS", str(exc)),
        ) from exc

    return MatchRead.model_validate(match)


@router.delete("/{match_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_match(
    match_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_write_access),
) -> Response:
    try:
        service.delete_match(db=db, match_id=match_id)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_error_payload("MATCH_NOT_FOUND", str(exc)),
        ) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)
