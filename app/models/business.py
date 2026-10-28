from datetime import datetime

from pydantic import BaseModel, Field


class BusinessCreate(BaseModel):
    tenant_id: str

    name: str = Field(
        min_length=1,
        max_length=200,
    )

    website: str | None = None
    phone: str | None = None
    email: str | None = None

    address: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None

    timezone: str = "America/Chicago"

    services: list[str] = Field(
        default_factory=list
    )

    sales_rep_id: str | None = None


class BusinessUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    website: str | None = None
    phone: str | None = None
    email: str | None = None

    address: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None

    timezone: str | None = None

    services: list[str] | None = None

    sales_rep_id: str | None = None


class BusinessResponse(BaseModel):
    id: str
    tenant_id: str

    name: str
    website: str | None = None
    phone: str | None = None
    email: str | None = None

    address: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None

    timezone: str
    services: list[str]

    sales_rep_id: str | None = None

    status: str
    created_at: datetime
