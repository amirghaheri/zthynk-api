
from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import (
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    and_,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, foreign

from app.database.base import Base


class Service(Base):
    __tablename__ = "services"

    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "name",
            name="uq_services_organization_name",
        ),
        UniqueConstraint(
            "id",
            "organization_id",
            name="uq_services_id_organization_id",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid4,
    )

    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    businesses: Mapped[list["BusinessService"]] = relationship(
        back_populates="service",
        cascade="all, delete-orphan",
        primaryjoin=lambda: _service_businesses_join(),
    )


def _service_businesses_join():
    from app.db_models.business_service import BusinessService

    return and_(
        Service.id == foreign(BusinessService.service_id),
        Service.organization_id == BusinessService.organization_id,
    )
