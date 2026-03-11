"""rate limiting tests for authenticated write endpoints."""

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.security import reset_rate_limiter_state


def test_rate_limit_blocks_excess_write_requests(client: TestClient) -> None:
    settings = get_settings()
    original_window = settings.rate_limit_window_seconds
    original_max = settings.rate_limit_max_requests

    try:
        settings.rate_limit_window_seconds = 60
        settings.rate_limit_max_requests = 2
        reset_rate_limiter_state()

        response_one = client.post(
            "/teams",
            json={"name": "Rate Team 1", "league": "Premier League", "country": "England"},
        )
        response_two = client.post(
            "/teams",
            json={"name": "Rate Team 2", "league": "Premier League", "country": "England"},
        )
        response_three = client.post(
            "/teams",
            json={"name": "Rate Team 3", "league": "Premier League", "country": "England"},
        )

        assert response_one.status_code == 201
        assert response_two.status_code == 201
        assert response_three.status_code == 429
        assert response_three.json()["detail"]["error"]["code"] == "RATE_LIMIT_EXCEEDED"
        assert "retry-after" in response_three.headers
    finally:
        settings.rate_limit_window_seconds = original_window
        settings.rate_limit_max_requests = original_max
        reset_rate_limiter_state()
