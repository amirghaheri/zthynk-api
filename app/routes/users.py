from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.user import UserCreate, UserResponse
from app.services.user import UserService, get_user_service
from app.db_models.user import User

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post("/", response_model=UserResponse)
def create_user_endpoint(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserResponse:

    user = User(
        name=user_data.name,
        email=user_data.email,
        organization_id=user_data.organization_id,
    )

    return service.create_user(user)


@router.get("/{user_id}", response_model=UserResponse)
def get_user_endpoint(
    user_id: UUID,
    service: UserService = Depends(get_user_service),
) -> UserResponse:

    user = service.get_user(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@router.get("/", response_model=list[UserResponse])
def get_users_endpoint(
    service: UserService = Depends(get_user_service),
) -> list[UserResponse]:

    return service.get_users()
