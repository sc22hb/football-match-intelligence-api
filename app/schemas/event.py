"""pydantic schemas for event create/read/list payloads."""

from pydantic import BaseModel, ConfigDict, Field


class EventBase(BaseModel):
    match_id: int = Field(ge=1)
    team_id: int = Field(ge=1)
    player_id: int = Field(ge=1)
    minute: int = Field(ge=0)
    event_type: str = Field(min_length=1, max_length=50)
    event_detail: str = Field(min_length=1, max_length=255)


class EventCreate(EventBase):
    pass


class EventRead(EventBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class EventListResponse(BaseModel):
    items: list[EventRead]
    total: int
    skip: int
    limit: int
