from uuid import UUID

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.repositories import business_service as business_service_repository
from app.schemas.business_service import (
    BusinessServiceCreate,
    BusinessServiceUpdate,
)


class BusinessCatalogService:
    def __init__(self, db: Session):
        self.db = db

    def list_services(
        self,
        organization_id: UUID,
        business_id: UUID,
    ):
        return business_service_repository.get_business_services(
            self.db,
            organization_id,
            business_id,
        )

    def add_service(
        self,
        organization_id: UUID,
        business_id: UUID,
        association_data: BusinessServiceCreate,
    ):
        return business_service_repository.create_business_service(
            self.db,
            organization_id,
            business_id,
            association_data,
        )

    def business_exists(
        self,
        organization_id: UUID,
        business_id: UUID,
    ) -> bool:
        return business_service_repository.business_belongs_to_organization(
            self.db,
            organization_id,
            business_id,
        )

    def update_service(
        self,
        organization_id: UUID,
        business_id: UUID,
        association_id: UUID,
        update_data: BusinessServiceUpdate,
    ):
        return business_service_repository.update_business_service(
            self.db,
            organization_id,
            business_id,
            association_id,
            update_data,
        )

    def remove_service(
        self,
        organization_id: UUID,
        business_id: UUID,
        association_id: UUID,
    ) -> bool:
        return business_service_repository.delete_business_service(
            self.db,
            organization_id,
            business_id,
            association_id,
        )


def get_business_catalog_service(
    db: Session = Depends(get_db),
) -> BusinessCatalogService:
    return BusinessCatalogService(db)
