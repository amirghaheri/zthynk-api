from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db_models.organization import Organization

from app.database.base import Base


class Business(Base):
    __tablename__ = "businesses"

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id"),
        nullable=False,
    )
    organization: Mapped["Organization"] = relationship(back_populates="businesses")

    website: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    city: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    state: Mapped[str | None] = mapped_column(
        String(2),
        nullable=True,
    )

    zip_code: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
    )
    # your existing columns...

    services: Mapped[list["BusinessService"]] = relationship(
        back_populates="business",
        cascade="all, delete-orphan",
    )
