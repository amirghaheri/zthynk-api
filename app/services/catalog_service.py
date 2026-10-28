from uuid import UUID

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.repositories import service as service_repository
from app.schemas.service import ServiceCreate, ServiceUpdate


class CatalogService:
    def __init__(self, db: Session):
        self.db = db

    def list_services(self, organization_id: UUID):
        return service_repository.get_services(
            self.db,
            organization_id,
        )

    def get_service(self, organization_id: UUID, service_id: UUID):
        return service_repository.get_service(
            self.db,
            organization_id,
            service_id,
        )

    def create_service(
        self,
        organization_id: UUID,
        service_data: ServiceCreate,
    ):
        return service_repository.create_service(
            self.db,
            organization_id,
            service_data,
        )

    def update_service(
        self,
        organization_id: UUID,
        service_id: UUID,
        service_data: ServiceUpdate,
    ):
        return service_repository.update_service(
            self.db,
            organization_id,
            service_id,
            service_data,
        )

    def delete_service(self, organization_id: UUID, service_id: UUID):
        return service_repository.delete_service(
            self.db,
            organization_id,
            service_id,
        )


def get_catalog_service(
    db: Session = Depends(get_db),
) -> CatalogService:
    return CatalogService(db)
