from app.db_models.business import Business
from app.db_models.organization import Organization
from app.repositories.business import (
    create_business,
    get_business,
    get_businesses,
)
from app.schemas.business import BusinessCreate


def test_create_and_retrieve_business(db_session):
    organization = Organization(name="Test Organization")
    db_session.add(organization)
    db_session.commit()
    db_session.refresh(organization)

    business_data = BusinessCreate(
        name="Test Business",
        city="Magnolia",
        state="TX",
    )

    business = create_business(
        db_session,
        business_data,
        organization.id,
    )

    assert business.name == "Test Business"
    assert business.city == "Magnolia"
    assert business.organization_id == organization.id

    retrieved = get_business(
        db_session,
        business.id,
        organization.id,
    )

    assert retrieved is not None
    assert retrieved.id == business.id

    businesses = get_businesses(
        db_session,
        organization.id,
    )

    assert len(businesses) == 1
    assert businesses[0].name == "Test Business"


def test_business_not_visible_to_another_organization(db_session):
    organization = Organization(name="Tenant A")
    db_session.add(organization)
    db_session.commit()
    db_session.refresh(organization)

    business = create_business(
        db_session,
        BusinessCreate(name="Tenant A Business"),
        organization.id,
    )

    other_organization = Organization(name="Tenant B")
    db_session.add(other_organization)
    db_session.commit()
    db_session.refresh(other_organization)

    result = get_business(
        db_session,
        business.id,
        other_organization.id,
    )

    assert result is None
