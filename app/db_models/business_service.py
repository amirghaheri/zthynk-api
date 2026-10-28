from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Integer,
    Numeric,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

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
    )

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid4,
    )

    business_id: Mapped[UUID] = mapped_column(
        ForeignKey("businesses.id"),
        nullable=False,
    )

    service_id: Mapped[UUID] = mapped_column(
        ForeignKey("services.id"),
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
    )

    service: Mapped["Service"] = relationship(
        back_populates="businesses",
    )
