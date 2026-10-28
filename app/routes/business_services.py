from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.auth.dependencies import get_current_user
from app.db_models.user import User
from app.schemas.business_service import (
    BusinessServiceCreate,
    BusinessServiceResponse,
    BusinessServiceUpdate,
)
from app.services.business_catalog_service import (
    BusinessCatalogService,
    get_business_catalog_service,
)

router = APIRouter(
    prefix="/businesses/{business_id}/services",
    tags=["Business Services"],
)


@router.get("/", response_model=list[BusinessServiceResponse])
def list_business_services(
    business_id: UUID,
    current_user: User = Depends(get_current_user),
    catalog: BusinessCatalogService = Depends(get_business_catalog_service),
):
    if not catalog.business_exists(
        current_user.organization_id,
        business_id,
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found",
        )

    return catalog.list_services(
        current_user.organization_id,
        business_id,
    )


@router.post(
    "/",
    response_model=BusinessServiceResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_business_service(
    business_id: UUID,
    association_data: BusinessServiceCreate,
    current_user: User = Depends(get_current_user),
    catalog: BusinessCatalogService = Depends(get_business_catalog_service),
):
    try:
        association = catalog.add_service(
            current_user.organization_id,
            business_id,
            association_data,
        )
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This service is already associated with this business.",
        ) from exc

    if association is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business or service not found",
        )

    return association


@router.patch(
    "/{association_id}",
    response_model=BusinessServiceResponse,
)
def update_business_service(
    business_id: UUID,
    association_id: UUID,
    update_data: BusinessServiceUpdate,
    current_user: User = Depends(get_current_user),
    catalog: BusinessCatalogService = Depends(get_business_catalog_service),
):
    association = catalog.update_service(
        current_user.organization_id,
        business_id,
        association_id,
        update_data,
    )

    if association is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business service not found",
        )

    return association


@router.delete(
    "/{association_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_business_service(
    business_id: UUID,
    association_id: UUID,
    current_user: User = Depends(get_current_user),
    catalog: BusinessCatalogService = Depends(get_business_catalog_service),
):
    deleted = catalog.remove_service(
        current_user.organization_id,
        business_id,
        association_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business service not found",
        )

    return None
