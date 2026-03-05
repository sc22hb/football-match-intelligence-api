"""pydantic schemas for player create/read/update/list payloads."""

from pydantic import BaseModel, ConfigDict, Field


class PlayerBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    team_id: int = Field(ge=1)
    position: str = Field(min_length=1, max_length=60)


class PlayerCreate(PlayerBase):
    pass


class PlayerUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    team_id: int | None = Field(default=None, ge=1)
    position: str | None = Field(default=None, min_length=1, max_length=60)


class PlayerRead(PlayerBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class PlayerListResponse(BaseModel):
    items: list[PlayerRead]
    total: int
    skip: int
    limit: int
