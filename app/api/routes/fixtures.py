"""fixtures http endpoints and response handling."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.fixture import FixtureListResponse, FixtureRead
from app.services.fixture_service import FixtureService

router = APIRouter(prefix="/fixtures", tags=["fixtures"])
service = FixtureService()


@router.get("", response_model=FixtureListResponse)
def list_fixtures(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    season: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> FixtureListResponse:
    fixtures, total = service.list_fixtures(db=db, skip=skip, limit=limit, season=season)
    return FixtureListResponse(
        items=[FixtureRead.model_validate(fixture) for fixture in fixtures],
        total=total,
        skip=skip,
        limit=limit,
    )
