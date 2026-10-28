from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.dependencies import get_db
from app.db_models.user import User
from app.schemas.service import (
    ServiceCreate,
    ServiceResponse,
    ServiceUpdate,
)
from app.services.catalog_service import CatalogService

router = APIRouter(
    prefix="/services",
    tags=["Services"],
)


def get_catalog_service(
    db: Session = Depends(get_db),
) -> CatalogService:
    return CatalogService(db)


@router.get("/", response_model=list[ServiceResponse])
def list_services(
    current_user: User = Depends(get_current_user),
    catalog: CatalogService = Depends(get_catalog_service),
):
    return catalog.list_services(current_user.organization_id)


@router.post(
    "/",
    response_model=ServiceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_service(
    service_data: ServiceCreate,
    current_user: User = Depends(get_current_user),
    catalog: CatalogService = Depends(get_catalog_service),
):
    try:
        return catalog.create_service(
            current_user.organization_id,
            service_data,
        )
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A service with this name already exists in your organization.",
        ) from exc


@router.get("/{service_id}", response_model=ServiceResponse)
def get_service(
    service_id: UUID,
    current_user: User = Depends(get_current_user),
    catalog: CatalogService = Depends(get_catalog_service),
):
    service = catalog.get_service(
        current_user.organization_id,
        service_id,
    )

    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found",
        )

    return service


@router.patch("/{service_id}", response_model=ServiceResponse)
def update_service(
    service_id: UUID,
    service_data: ServiceUpdate,
    current_user: User = Depends(get_current_user),
    catalog: CatalogService = Depends(get_catalog_service),
):
    try:
        service = catalog.update_service(
            current_user.organization_id,
            service_id,
            service_data,
        )
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A service with this name already exists in your organization.",
        ) from exc

    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found",
        )

    return service


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(
    service_id: UUID,
    current_user: User = Depends(get_current_user),
    catalog: CatalogService = Depends(get_catalog_service),
):
    deleted = catalog.delete_service(
        current_user.organization_id,
        service_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found",
        )

    return None
