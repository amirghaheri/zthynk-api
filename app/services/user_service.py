from datetime import datetime, timezone
from uuid import uuid4

from app.models.user import UserCreate, UserResponse
from app.repositories.user_repository import UserRepository


repository = UserRepository()


def create_user(user: UserCreate) -> UserResponse:
    user_response = UserResponse(
        id=str(uuid4()),
        tenant_id=user.tenant_id,
        name=user.name,
        email=user.email,
        role=user.role,
        status="active",
        created_at=datetime.now(timezone.utc),
    )

    return repository.create(user_response)


def get_user(user_id: str) -> UserResponse | None:
    return repository.get_by_id(user_id)

def update_user(
    user_id: str,
    updates: dict
) -> UserResponse | None:
    return repository.update(user_id, updates)