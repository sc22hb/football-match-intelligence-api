from datetime import UTC, datetime

from fastapi import FastAPI

app = FastAPI(
    title="Football Match Intelligence API",
    version="0.1.0",
    description="Data-driven football analytics API",
)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "football-match-intelligence-api",
        "timestamp": datetime.now(UTC).isoformat(),
    }
