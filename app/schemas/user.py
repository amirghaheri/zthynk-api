from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    name: str
    email: str
    organization_id: UUID


class UserResponse(BaseModel):
    id: UUID
    name: str
    email: str
    organization_id: UUID

    model_config = ConfigDict(from_attributes=True)
