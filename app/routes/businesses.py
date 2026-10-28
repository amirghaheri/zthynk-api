from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import get_current_user
from app.db_models.user import User
from app.services.business import BusinessService, get_business_service
from app.schemas.business import (
    BusinessCreate,
    BusinessResponse,
    BusinessUpdate,
)

router = APIRouter(
    prefix="/businesses",
    tags=["Businesses"],
)


@router.post(
    "/",
    response_model=BusinessResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_business_endpoint(
    business_data: BusinessCreate,
    current_user: User = Depends(get_current_user),
    service: BusinessService = Depends(get_business_service),
) -> BusinessResponse:
    return service.create_business(
        business_data,
        current_user.organization_id,
    )


@router.get(
    "/{business_id}",
    response_model=BusinessResponse,
)
def get_business_endpoint(
    business_id: UUID,
    current_user: User = Depends(get_current_user),
    service: BusinessService = Depends(get_business_service),
) -> BusinessResponse:
    business = service.get_business(
        business_id,
        current_user.organization_id,
    )

    if business is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found",
        )

    return business


@router.get(
    "/",
    response_model=list[BusinessResponse],
)
def get_businesses_endpoint(
    current_user: User = Depends(get_current_user),
    service: BusinessService = Depends(get_business_service),
) -> list[BusinessResponse]:
    return service.get_businesses(current_user.organization_id)


@router.patch(
    "/{business_id}",
    response_model=BusinessResponse,
)
def update_business_endpoint(
    business_id: UUID,
    business_data: BusinessUpdate,
    current_user: User = Depends(get_current_user),
    service: BusinessService = Depends(get_business_service),
) -> BusinessResponse:
    business = service.update_business(
        business_id,
        current_user.organization_id,
        business_data,
    )

    if business is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found",
        )

    return business


@router.delete(
    "/{business_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_business_endpoint(
    business_id: UUID,
    current_user: User = Depends(get_current_user),
    service: BusinessService = Depends(get_business_service),
) -> None:
    deleted = service.delete_business(
        business_id,
        current_user.organization_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found",
        )
