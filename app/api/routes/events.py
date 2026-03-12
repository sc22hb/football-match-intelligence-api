"""events http endpoints and response handling."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.docs import (
    AUTH_ERROR_RESPONSES,
    INVALID_EVENT_RESPONSE,
    MATCH_NOT_FOUND_RESPONSE,
)
from app.core.security import require_write_access
from app.db.session import get_db
from app.schemas.event import EventCreate, EventListResponse, EventRead
from app.services.errors import NotFoundError, ServiceValidationError
from app.services.event_service import EventService

router = APIRouter(prefix="/events", tags=["events"])
service = EventService()



def _error_payload(code: str, message: str) -> dict[str, dict[str, str]]:
    return {"error": {"code": code, "message": message}}


@router.post(
    "",
    response_model=EventRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create event",
    description="Creates a new event row linked to a match, team, and player. Requires the `X-API-Key` header.",
    responses={
        404: MATCH_NOT_FOUND_RESPONSE,
        422: INVALID_EVENT_RESPONSE,
        **AUTH_ERROR_RESPONSES,
    },
)
def create_event(
    payload: EventCreate,
    db: Session = Depends(get_db),
    _: None = Depends(require_write_access),
) -> EventRead:
    try:
        event = service.create_event(db=db, payload=payload)
    except NotFoundError as exc:
        message = str(exc)
        if "Match" in message:
            code = "MATCH_NOT_FOUND"
        elif "Team" in message:
            code = "TEAM_NOT_FOUND"
        else:
            code = "PLAYER_NOT_FOUND"

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_error_payload(code, message),
        ) from exc
    except ServiceValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=_error_payload("INVALID_EVENT_RELATION", str(exc)),
        ) from exc

    return EventRead.model_validate(event)


@router.get(
    "",
    response_model=EventListResponse,
    summary="List events",
    description="Returns a paginated list of events.",
)
def list_events(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> EventListResponse:
    events, total = service.list_events(db=db, skip=skip, limit=limit)
    return EventListResponse(
        items=[EventRead.model_validate(event) for event in events],
        total=total,
        skip=skip,
        limit=limit,
    )
