from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ServiceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None

    model_config = ConfigDict(extra="forbid")


class ServiceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None

    model_config = ConfigDict(extra="forbid")


class ServiceResponse(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    description: str | None

    model_config = ConfigDict(from_attributes=True)
