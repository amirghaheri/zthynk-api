from app.auth.dependencies import get_current_user
from app.db_models.business import Business
from app.db_models.business_service import BusinessService
from app.db_models.organization import Organization
from app.db_models.service import Service
from app.db_models.user import User
from app.main import app


def test_user_cannot_associate_another_organizations_service(
    client, db_session
):
    organization_a = Organization(name="Association Create Tenant A")
    organization_b = Organization(name="Association Create Tenant B")
    db_session.add_all([organization_a, organization_b])
    db_session.flush()

    business_a = Business(
        name="Tenant A Business",
        organization_id=organization_a.id,
    )
    service_b = Service(
        name="Tenant B Service",
        organization_id=organization_b.id,
    )
    user_a = User(
        email="association-create-a@example.com",
        name="Association Create User A",
        organization_id=organization_a.id,
    )
    db_session.add_all([business_a, service_b, user_a])
    db_session.flush()

    app.dependency_overrides[get_current_user] = lambda: user_a

    try:
        response = client.post(
            f"/businesses/{business_a.id}/services/",
            json={"service_id": str(service_b.id)},
        )
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 404
    assert db_session.query(BusinessService).count() == 0


def test_list_business_services_only_returns_own_business(
    client, db_session
):
    organization_a = Organization(name="Association List Tenant A")
    organization_b = Organization(name="Association List Tenant B")
    db_session.add_all([organization_a, organization_b])
    db_session.flush()

    business_a = Business(
        name="Association List Business A",
        organization_id=organization_a.id,
    )
    business_b = Business(
        name="Association List Business B",
        organization_id=organization_b.id,
    )
    service_a = Service(
        name="Association List Service A",
        organization_id=organization_a.id,
    )
    service_b = Service(
        name="Association List Service B",
        organization_id=organization_b.id,
    )
    user_a = User(
        email="association-list-a@example.com",
        name="Association List User A",
        organization_id=organization_a.id,
    )
    db_session.add_all(
        [business_a, business_b, service_a, service_b, user_a]
    )
    db_session.flush()

    db_session.add_all(
        [
            BusinessService(
                business_id=business_a.id,
                service_id=service_a.id,
            ),
            BusinessService(
                business_id=business_b.id,
                service_id=service_b.id,
            ),
        ]
    )
    db_session.flush()

    app.dependency_overrides[get_current_user] = lambda: user_a

    try:
        response = client.get(
            f"/businesses/{business_a.id}/services/"
        )
        foreign_business_response = client.get(
            f"/businesses/{business_b.id}/services/"
        )
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["service_id"] == str(service_a.id)

    assert foreign_business_response.status_code == 404


def test_user_cannot_update_another_organizations_association(
    client, db_session
):
    organization_a = Organization(name="Association Update Tenant A")
    organization_b = Organization(name="Association Update Tenant B")
    db_session.add_all([organization_a, organization_b])
    db_session.flush()

    business_a = Business(
        name="Association Update Business A",
        organization_id=organization_a.id,
    )
    business_b = Business(
        name="Association Update Business B",
        organization_id=organization_b.id,
    )
    service_b = Service(
        name="Association Update Service B",
        organization_id=organization_b.id,
    )
    user_a = User(
        email="association-update-a@example.com",
        name="Association Update User A",
        organization_id=organization_a.id,
    )
    db_session.add_all(
        [business_a, business_b, service_b, user_a]
    )
    db_session.flush()

    association_b = BusinessService(
        business_id=business_b.id,
        service_id=service_b.id,
        price=50,
    )
    db_session.add(association_b)
    db_session.flush()

    app.dependency_overrides[get_current_user] = lambda: user_a

    try:
        response = client.patch(
            f"/businesses/{business_a.id}/services/{association_b.id}",
            json={"price": 1},
        )
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 404

    db_session.refresh(association_b)
    assert float(association_b.price) == 50.0


def test_user_cannot_delete_another_organizations_association(
    client, db_session
):
    organization_a = Organization(name="Association Delete Tenant A")
    organization_b = Organization(name="Association Delete Tenant B")
    db_session.add_all([organization_a, organization_b])
    db_session.flush()

    business_a = Business(
        name="Association Delete Business A",
        organization_id=organization_a.id,
    )
    business_b = Business(
        name="Association Delete Business B",
        organization_id=organization_b.id,
    )
    service_b = Service(
        name="Association Delete Service B",
        organization_id=organization_b.id,
    )
    user_a = User(
        email="association-delete-a@example.com",
        name="Association Delete User A",
        organization_id=organization_a.id,
    )
    db_session.add_all(
        [business_a, business_b, service_b, user_a]
    )
    db_session.flush()

    association_b = BusinessService(
        business_id=business_b.id,
        service_id=service_b.id,
    )
    db_session.add(association_b)
    db_session.flush()
    association_id = association_b.id

    app.dependency_overrides[get_current_user] = lambda: user_a

    try:
        response = client.delete(
            f"/businesses/{business_a.id}/services/{association_id}"
        )
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 404

    db_session.expire_all()
    remaining_association = db_session.get(
        BusinessService, association_id
    )
    assert remaining_association is not None
