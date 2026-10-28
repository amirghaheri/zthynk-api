from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    tenant_id: str

    name: str = Field(
        min_length=1,
        max_length=200,
    )

    email: EmailStr
    role: str = "sales"


class UserUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    email: EmailStr | None = None

    role: str | None = None

    status: str | None = None


class UserResponse(BaseModel):
    id: str
    tenant_id: str

    name: str
    email: EmailStr
    role: str

    status: str
    created_at: datetime