from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db_models.business import Business
from app.schemas.business import BusinessCreate, BusinessUpdate


def create_business(
    db: Session,
    business_data: BusinessCreate,
    organization_id: UUID,
) -> Business:
    business = Business(
        **business_data.model_dump(),
        organization_id=organization_id,
    )

    try:
        db.add(business)
        db.commit()
        db.refresh(business)
        return business
    except Exception:
        db.rollback()
        raise


def get_business(
    db: Session,
    business_id: UUID,
    organization_id: UUID,
) -> Business | None:
    statement = select(Business).where(
        Business.id == business_id,
        Business.organization_id == organization_id,
    )
    return db.scalar(statement)


def get_businesses(
    db: Session,
    organization_id: UUID,
) -> list[Business]:
    statement = (
        select(Business)
        .where(Business.organization_id == organization_id)
        .order_by(Business.name)
    )
    return list(db.scalars(statement).all())


def update_business(
    db: Session,
    business_id: UUID,
    organization_id: UUID,
    business_data: BusinessUpdate,
) -> Business | None:
    business = get_business(db, business_id, organization_id)

    if business is None:
        return None

    update_data = business_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(business, field, value)

    try:
        db.commit()
        db.refresh(business)
        return business
    except Exception:
        db.rollback()
        raise


def delete_business(
    db: Session,
    business_id: UUID,
    organization_id: UUID,
) -> bool:
    business = get_business(db, business_id, organization_id)

    if business is None:
        return False

    try:
        db.delete(business)
        db.commit()
        return True
    except Exception:
        db.rollback()
        raise
