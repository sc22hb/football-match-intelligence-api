"""fastapi app entrypoint, frontend, and shared health endpoint."""

from datetime import UTC, datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(
    title="Football Match Intelligence API",
    version="0.1.0",
    description=(
        "Data-driven football analytics API with CRUD endpoints, explainable analytics, "
        "API-key protected write operations, and auto-generated OpenAPI documentation."
    ),
)

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
app.include_router(api_router)


@app.get("/", include_in_schema=False)
def frontend() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "football-match-intelligence-api",
        "timestamp": datetime.now(UTC).isoformat(),
    }
