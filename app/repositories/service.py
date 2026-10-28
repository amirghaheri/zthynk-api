from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db_models.service import Service
from app.schemas.service import ServiceCreate, ServiceUpdate


def get_services(
    db: Session,
    organization_id: UUID,
) -> list[Service]:
    statement = (
        select(Service)
        .where(Service.organization_id == organization_id)
        .order_by(Service.name)
    )
    return list(db.scalars(statement).all())


def get_service(
    db: Session,
    organization_id: UUID,
    service_id: UUID,
) -> Service | None:
    statement = select(Service).where(
        Service.id == service_id,
        Service.organization_id == organization_id,
    )
    return db.scalars(statement).first()


def create_service(
    db: Session,
    organization_id: UUID,
    service_data: ServiceCreate,
) -> Service:
    service = Service(
        organization_id=organization_id,
        name=service_data.name.strip(),
        description=service_data.description,
    )

    db.add(service)

    try:
        db.commit()
        db.refresh(service)
        return service
    except Exception:
        db.rollback()
        raise


def update_service(
    db: Session,
    organization_id: UUID,
    service_id: UUID,
    service_data: ServiceUpdate,
) -> Service | None:
    service = get_service(db, organization_id, service_id)

    if service is None:
        return None

    changes = service_data.model_dump(exclude_unset=True)

    if "name" in changes and changes["name"] is not None:
        changes["name"] = changes["name"].strip()

    for field, value in changes.items():
        setattr(service, field, value)

    try:
        db.commit()
        db.refresh(service)
        return service
    except Exception:
        db.rollback()
        raise


def delete_service(
    db: Session,
    organization_id: UUID,
    service_id: UUID,
) -> bool:
    service = get_service(db, organization_id, service_id)

    if service is None:
        return False

    try:
        db.delete(service)
        db.commit()
        return True
    except Exception:
        db.rollback()
        raise
