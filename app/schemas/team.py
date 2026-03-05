"""pydantic schemas for team create/read/update/list payloads."""

from pydantic import BaseModel, ConfigDict, Field


class TeamBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    league: str = Field(min_length=1, max_length=120)
    country: str = Field(min_length=1, max_length=120)


class TeamCreate(TeamBase):
    pass


class TeamUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    league: str | None = Field(default=None, min_length=1, max_length=120)
    country: str | None = Field(default=None, min_length=1, max_length=120)


class TeamRead(TeamBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class TeamListResponse(BaseModel):
    items: list[TeamRead]
    total: int
    skip: int
    limit: int
