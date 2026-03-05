"""collects and registers all api route modules."""

from fastapi import APIRouter

from app.api.routes.players import router as players_router
from app.api.routes.teams import router as teams_router

api_router = APIRouter()
api_router.include_router(teams_router)
api_router.include_router(players_router)
