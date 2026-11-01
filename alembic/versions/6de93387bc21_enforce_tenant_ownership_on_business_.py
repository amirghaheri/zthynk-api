"""enforce tenant ownership on business services

Revision ID: 6de93387bc21
Revises: 9b0a83238629
Create Date: 2026-11-01 01:59:03.136359

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6de93387bc21'
down_revision: Union[str, Sequence[str], None] = '9b0a83238629'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Allow foreign keys to reference (id, organization_id).
    op.create_unique_constraint(
        "uq_businesses_id_organization_id",
        "businesses",
        ["id", "organization_id"],
    )

    op.create_unique_constraint(
        "uq_services_id_organization_id",
        "services",
        ["id", "organization_id"],
    )

    # Add organization_id temporarily as nullable.
    op.add_column(
        "business_services",
        sa.Column("organization_id", sa.Uuid(), nullable=True),
    )

    # Copy the organization's ID from each associated business.
    op.execute("""
        UPDATE business_services AS bs
        SET organization_id = b.organization_id
        FROM businesses AS b
        WHERE bs.business_id = b.id
    """)

    # Stop if any association has a missing or mismatched organization.
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM business_services AS bs
                JOIN businesses AS b ON b.id = bs.business_id
                JOIN services AS s ON s.id = bs.service_id
                WHERE bs.organization_id IS NULL
                   OR bs.organization_id <> b.organization_id
                   OR bs.organization_id <> s.organization_id
            ) THEN
                RAISE EXCEPTION
                    'Cannot enforce tenant ownership: business and service organizations do not match';
            END IF;

            IF EXISTS (
                SELECT 1
                FROM business_services AS bs
                WHERE bs.organization_id IS NULL
            ) THEN
                RAISE EXCEPTION
                    'Cannot enforce tenant ownership: association organization_id could not be inferred';
            END IF;
        END $$;
    """)

    op.alter_column(
        "business_services",
        "organization_id",
        existing_type=sa.Uuid(),
        nullable=False,
    )

    # Remove the old single-column foreign keys.
    op.drop_constraint(
        "business_services_business_id_fkey",
        "business_services",
        type_="foreignkey",
    )

    op.drop_constraint(
        "business_services_service_id_fkey",
        "business_services",
        type_="foreignkey",
    )

    # A business association must reference a business
    # belonging to the same organization.
    op.create_foreign_key(
        "fk_business_services_business_organization",
        "business_services",
        "businesses",
        ["business_id", "organization_id"],
        ["id", "organization_id"],
    )

    # A service association must reference a service
    # belonging to the same organization.
    op.create_foreign_key(
        "fk_business_services_service_organization",
        "business_services",
        "services",
        ["service_id", "organization_id"],
        ["id", "organization_id"],
    )

def downgrade() -> None:
    """Downgrade schema."""

    # Remove the composite foreign keys.
    op.drop_constraint(
        "fk_business_services_business_organization",
        "business_services",
        type_="foreignkey",
    )

    op.drop_constraint(
        "fk_business_services_service_organization",
        "business_services",
        type_="foreignkey",
    )

    # Restore the original foreign keys.
    op.create_foreign_key(
        "business_services_business_id_fkey",
        "business_services",
        "businesses",
        ["business_id"],
        ["id"],
    )

    op.create_foreign_key(
        "business_services_service_id_fkey",
        "business_services",
        "services",
        ["service_id"],
        ["id"],
    )

    # Remove the organization column.
    op.drop_column("business_services", "organization_id")

    # Remove the composite unique constraints.
    op.drop_constraint(
        "uq_businesses_id_organization_id",
        "businesses",
        type_="unique",
    )

    op.drop_constraint(
        "uq_services_id_organization_id",
        "services",
        type_="unique",
    )
