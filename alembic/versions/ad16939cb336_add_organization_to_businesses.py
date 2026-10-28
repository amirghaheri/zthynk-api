"""add organization to businesses

Revision ID: ad16939cb336
Revises: 6eb541c48a81
Create Date: 2026-10-04 01:15:00.826254

"""

from typing import Sequence, Union
from uuid import UUID, uuid4

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "ad16939cb336"
down_revision: Union[str, Sequence[str], None] = "6eb541c48a81"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    organization_id = uuid4()

    # 1. Add organization_id temporarily as nullable.
    op.add_column(
        "businesses",
        sa.Column(
            "organization_id",
            sa.Uuid(),
            nullable=True,
        ),
    )

    # 2. Create the foreign key with an explicit name.
    op.create_foreign_key(
        "fk_businesses_organization_id",
        "businesses",
        "organizations",
        ["organization_id"],
        ["id"],
    )

    # 3. Create an organization for the existing business.
    op.execute(
        sa.text("""
        INSERT INTO organizations (id, name)
        VALUES (:organization_id, :name)
        """).bindparams(
            organization_id=organization_id,
            name="Green Rug Care",
        )
    )

    # 4. Assign the existing business to that organization.
    op.execute(
        sa.text("""
        UPDATE businesses
        SET organization_id = :organization_id
        WHERE id = :business_id
        """).bindparams(
            organization_id=organization_id,
            business_id=UUID("7534ab81-47d8-4217-9f5c-f11604f9958c"),
        )
    )

    # 5. Now that every existing business has an organization,
    #    make the column required.
    op.alter_column(
        "businesses",
        "organization_id",
        nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    # Remove the foreign key first.
    op.drop_constraint(
        "fk_businesses_organization_id",
        "businesses",
        type_="foreignkey",
    )

    # Remove the organization_id column.
    op.drop_column(
        "businesses",
        "organization_id",
    )

    # The organization created by this migration is intentionally
    # not deleted here because we don't want to accidentally delete
    # an organization that may have been modified after migration.
