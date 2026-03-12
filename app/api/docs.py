"""Reusable OpenAPI docs metadata for routes."""

ERROR_SCHEMA = {
    "type": "object",
    "properties": {
        "detail": {
            "type": "object",
            "properties": {
                "error": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "example": "TEAM_NOT_FOUND"},
                        "message": {
                            "type": "string",
                            "example": "Team with id 999 not found",
                        },
                    },
                    "required": ["code", "message"],
                }
            },
            "required": ["error"],
        }
    },
    "required": ["detail"],
}


def error_response(status_text: str, code: str, message: str) -> dict[str, object]:
    return {
        "description": status_text,
        "content": {
            "application/json": {
                "schema": ERROR_SCHEMA,
                "example": {"detail": {"error": {"code": code, "message": message}}},
            }
        },
    }


AUTH_ERROR_RESPONSES = {
    401: error_response("Missing API key.", "API_KEY_MISSING", "Missing X-API-Key header."),
    403: error_response("Invalid API key.", "API_KEY_INVALID", "Invalid API key."),
    429: error_response(
        "Write rate limit exceeded.",
        "RATE_LIMIT_EXCEEDED",
        "Too many requests. Try again later.",
    ),
}


TEAM_NOT_FOUND_RESPONSE = error_response("Team not found.", "TEAM_NOT_FOUND", "Team with id 999 not found")
PLAYER_NOT_FOUND_RESPONSE = error_response(
    "Player not found.", "PLAYER_NOT_FOUND", "Player with id 999 not found"
)
MATCH_NOT_FOUND_RESPONSE = error_response(
    "Match not found.", "MATCH_NOT_FOUND", "Match with id 999 not found"
)
TEAM_CONFLICT_RESPONSE = error_response(
    "Duplicate team.", "TEAM_ALREADY_EXISTS", "Team 'Arsenal' already exists"
)
PLAYER_CONFLICT_RESPONSE = error_response(
    "Duplicate player.", "PLAYER_ALREADY_EXISTS", "Player 'Bukayo Saka' already exists"
)
INVALID_MATCH_RESPONSE = error_response(
    "Invalid match payload.",
    "INVALID_MATCH_TEAMS",
    "Home team and away team must be different.",
)
INVALID_EVENT_RESPONSE = error_response(
    "Invalid event payload.",
    "INVALID_EVENT_RELATION",
    "Event team and player team do not match for this fixture.",
)
