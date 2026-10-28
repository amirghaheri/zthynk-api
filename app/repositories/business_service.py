from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db_models.business import Business
from app.db_models.business_service import BusinessService
from app.db_models.service import Service
from app.schemas.business_service import (
    BusinessServiceCreate,
    BusinessServiceUpdate,
)


def get_business_service(
    db: Session,
    organization_id: UUID,
    business_id: UUID,
    association_id: UUID,
) -> BusinessService | None:
    statement = (
        select(BusinessService)
        .join(Business, BusinessService.business_id == Business.id)
        .where(
            BusinessService.id == association_id,
            Business.id == business_id,
            Business.organization_id == organization_id,
        )
    )
    return db.scalars(statement).first()


def get_business_services(
    db: Session,
    organization_id: UUID,
    business_id: UUID,
) -> list[BusinessService]:
    statement = (
        select(BusinessService)
        .join(Business, BusinessService.business_id == Business.id)
        .where(
            Business.id == business_id,
            Business.organization_id == organization_id,
        )
        .order_by(BusinessService.id)
    )
    return list(db.scalars(statement).all())


def business_belongs_to_organization(
    db: Session,
    organization_id: UUID,
    business_id: UUID,
) -> bool:
    statement = select(Business.id).where(
        Business.id == business_id,
        Business.organization_id == organization_id,
    )
    return db.scalar(statement) is not None


def create_business_service(
    db: Session,
    organization_id: UUID,
    business_id: UUID,
    association_data: BusinessServiceCreate,
) -> BusinessService | None:
    business_statement = select(Business).where(
        Business.id == business_id,
        Business.organization_id == organization_id,
    )
    business = db.scalars(business_statement).first()

    if business is None:
        return None

    service_statement = select(Service).where(
        Service.id == association_data.service_id,
        Service.organization_id == organization_id,
    )
    service = db.scalars(service_statement).first()

    if service is None:
        return None

    association = BusinessService(
        business_id=business.id,
        service_id=service.id,
        price=association_data.price,
        duration_minutes=association_data.duration_minutes,
        active=association_data.active,
    )

    db.add(association)

    try:
        db.commit()
        db.refresh(association)
        return association
    except Exception:
        db.rollback()
        raise


def update_business_service(
    db: Session,
    organization_id: UUID,
    business_id: UUID,
    association_id: UUID,
    update_data: BusinessServiceUpdate,
) -> BusinessService | None:
    association = get_business_service(
        db,
        organization_id,
        business_id,
        association_id,
    )

    if association is None:
        return None

    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(association, field, value)

    try:
        db.commit()
        db.refresh(association)
        return association
    except Exception:
        db.rollback()
        raise


def delete_business_service(
    db: Session,
    organization_id: UUID,
    business_id: UUID,
    association_id: UUID,
) -> bool:
    association = get_business_service(
        db,
        organization_id,
        business_id,
        association_id,
    )

    if association is None:
        return False

    try:
        db.delete(association)
        db.commit()
        return True
    except Exception:
        db.rollback()
        raise
