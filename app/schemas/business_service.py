from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BusinessServiceCreate(BaseModel):
    service_id: UUID
    price: Decimal | None = Field(default=None, ge=0)
    duration_minutes: int | None = Field(default=None, gt=0)
    active: bool = True

    model_config = ConfigDict(extra="forbid")


class BusinessServiceUpdate(BaseModel):
    price: Decimal | None = Field(default=None, ge=0)
    duration_minutes: int | None = Field(default=None, gt=0)
    active: bool | None = None

    model_config = ConfigDict(extra="forbid")


class BusinessServiceResponse(BaseModel):
    id: UUID
    business_id: UUID
    service_id: UUID
    price: Decimal | None
    duration_minutes: int | None
    active: bool

    model_config = ConfigDict(from_attributes=True)
