"""collects and registers all api route modules."""

from fastapi import APIRouter

from app.api.routes.analytics import router as analytics_router
from app.api.routes.events import router as events_router
from app.api.routes.fixtures import router as fixtures_router
from app.api.routes.matches import router as matches_router
from app.api.routes.players import router as players_router
from app.api.routes.teams import router as teams_router

api_router = APIRouter()
api_router.include_router(teams_router)
api_router.include_router(players_router)
api_router.include_router(matches_router)
api_router.include_router(events_router)
api_router.include_router(fixtures_router)
api_router.include_router(analytics_router)
