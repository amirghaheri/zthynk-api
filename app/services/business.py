from uuid import UUID

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.db_models.business import Business
from app.repositories.business import (
    create_business as create_business_repository,
    get_business as get_business_repository,
    get_businesses as get_businesses_repository,
    update_business as update_business_repository,
    delete_business as delete_business_repository,
)
from app.schemas.business import BusinessCreate, BusinessUpdate


class BusinessService:
    def __init__(self, db: Session):
        self.db = db

    def create_business(
        self,
        business_data: BusinessCreate,
        organization_id: UUID,
    ) -> Business:
        return create_business_repository(
            self.db,
            business_data,
            organization_id,
        )

    def get_business(
        self,
        business_id: UUID,
        organization_id: UUID,
    ) -> Business | None:
        return get_business_repository(
            self.db,
            business_id,
            organization_id,
        )

    def get_businesses(
        self,
        organization_id: UUID,
    ) -> list[Business]:
        return get_businesses_repository(
            self.db,
            organization_id,
        )

    def update_business(
        self,
        business_id: UUID,
        organization_id: UUID,
        business_data: BusinessUpdate,
    ) -> Business | None:
        return update_business_repository(
            self.db,
            business_id,
            organization_id,
            business_data,
        )

    def delete_business(
        self,
        business_id: UUID,
        organization_id: UUID,
    ) -> bool:
        return delete_business_repository(
            self.db,
            business_id,
            organization_id,
        )


def get_business_service(
    db: Session = Depends(get_db),
) -> BusinessService:
    return BusinessService(db)
