"""scope services to organizations

Revision ID: 52cafab08e0d
Revises: 992cb95a9290
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "52cafab08e0d"
down_revision: Union[str, Sequence[str], None] = "992cb95a9290"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add the column as nullable so existing records can be backfilled.
    op.add_column(
        "services",
        sa.Column("organization_id", sa.Uuid(), nullable=True),
    )

    # Preserve existing services by assigning them to an organization
    # that owns a business currently associated with that service.
    op.execute("""
        UPDATE services AS s
        SET organization_id = (
            SELECT b.organization_id
            FROM business_services AS bs
            JOIN businesses AS b ON b.id = bs.business_id
            WHERE bs.service_id = s.id
            ORDER BY b.id
            LIMIT 1
        )
        WHERE s.organization_id IS NULL
        """)

    # If a service has no associated business, its owner cannot be
    # inferred safely. Stop rather than assign it to the wrong tenant.
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM services
                WHERE organization_id IS NULL
            ) THEN
                RAISE EXCEPTION
                    'Cannot migrate services without an inferable organization';
            END IF;
        END $$;
        """)

    op.alter_column(
        "services",
        "organization_id",
        existing_type=sa.Uuid(),
        nullable=False,
    )

    op.drop_constraint(
        "services_name_key",
        "services",
        type_="unique",
    )

    op.create_index(
        "ix_services_organization_id",
        "services",
        ["organization_id"],
        unique=False,
    )

    op.create_unique_constraint(
        "uq_services_organization_name",
        "services",
        ["organization_id", "name"],
    )

    op.create_foreign_key(
        "fk_services_organization_id_organizations",
        "services",
        "organizations",
        ["organization_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_services_organization_id_organizations",
        "services",
        type_="foreignkey",
    )

    op.drop_constraint(
        "uq_services_organization_name",
        "services",
        type_="unique",
    )

    op.drop_index(
        "ix_services_organization_id",
        table_name="services",
    )

    op.create_unique_constraint(
        "services_name_key",
        "services",
        ["name"],
    )

    op.drop_column("services", "organization_id")
