
from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    ForeignKeyConstraint,
    Integer,
    Numeric,
    UniqueConstraint,
    Uuid,
    and_,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, foreign

from app.database.base import Base
from app.db_models.business import Business
from app.db_models.service import Service


class BusinessService(Base):
    __tablename__ = "business_services"

    __table_args__ = (
        UniqueConstraint(
            "business_id",
            "service_id",
            name="uq_business_services_business_service",
        ),
        ForeignKeyConstraint(
            ["business_id", "organization_id"],
            ["businesses.id", "businesses.organization_id"],
            name="fk_business_services_business_organization",
        ),
        ForeignKeyConstraint(
            ["service_id", "organization_id"],
            ["services.id", "services.organization_id"],
            name="fk_business_services_service_organization",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid4,
    )

    business_id: Mapped[UUID] = mapped_column(
        Uuid,
        nullable=False,
    )

    service_id: Mapped[UUID] = mapped_column(
        Uuid,
        nullable=False,
    )

    organization_id: Mapped[UUID] = mapped_column(
        Uuid,
        nullable=False,
    )

    price: Mapped[float | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    duration_minutes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    business: Mapped["Business"] = relationship(
        back_populates="services",
        primaryjoin=lambda: and_(
            Business.id == foreign(BusinessService.business_id),
            Business.organization_id == BusinessService.organization_id,
        ),
    )

    service: Mapped["Service"] = relationship(
        back_populates="businesses",
        primaryjoin=lambda: and_(
            Service.id == foreign(BusinessService.service_id),
            Service.organization_id == BusinessService.organization_id,
        ),
    )
