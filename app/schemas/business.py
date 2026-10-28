from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BusinessCreate(BaseModel):
    name: str
    website: str | None = None
    phone: str | None = None
    email: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None

    model_config = ConfigDict(extra="forbid")


class BusinessUpdate(BaseModel):
    name: str | None = None
    website: str | None = None
    phone: str | None = None
    email: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None

    model_config = ConfigDict(extra="forbid")


class BusinessResponse(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    website: str | None = None
    phone: str | None = None
    email: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None

    model_config = ConfigDict(from_attributes=True)
