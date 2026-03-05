from fastapi import APIRouter

from app.api.routes.teams import router as teams_router

api_router = APIRouter()
api_router.include_router(teams_router)
