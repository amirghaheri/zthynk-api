from uuid import UUID, uuid4

from sqlalchemy import (
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Service(Base):
    __tablename__ = "services"

    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "name",
            name="uq_services_organization_name",
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
    )
