from app.auth.dependencies import get_current_user
from app.db_models.organization import Organization
from app.db_models.service import Service
from app.db_models.user import User
from app.main import app


def test_create_service_as_authenticated_user(client, db_session):
    organization = Organization(name="Service Create Organization")
    db_session.add(organization)
    db_session.flush()

    user = User(
        email="service-create@example.com",
        name="Service Create User",
        organization_id=organization.id,
    )
    db_session.add(user)
    db_session.flush()

    app.dependency_overrides[get_current_user] = lambda: user

    try:
        response = client.post(
            "/services/",
            json={
                "name": "Rug Cleaning",
                "description": "Professional rug cleaning",
            },
        )
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Rug Cleaning"
    assert data["description"] == "Professional rug cleaning"
    assert data["organization_id"] == str(organization.id)


def test_list_services_only_returns_own_organization(client, db_session):
    organization_a = Organization(name="Service List Tenant A")
    organization_b = Organization(name="Service List Tenant B")
    db_session.add_all([organization_a, organization_b])
    db_session.flush()

    db_session.add_all(
        [
            Service(
                name="Tenant A Service",
                organization_id=organization_a.id,
            ),
            Service(
                name="Tenant B Service",
                organization_id=organization_b.id,
            ),
        ]
    )
    db_session.flush()

    user_a = User(
        email="service-list-a@example.com",
        name="Service List User A",
        organization_id=organization_a.id,
    )
    db_session.add(user_a)
    db_session.flush()

    app.dependency_overrides[get_current_user] = lambda: user_a

    try:
        response = client.get("/services/")
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 200
    services = response.json()
    assert len(services) == 1
    assert services[0]["name"] == "Tenant A Service"


def test_user_cannot_access_another_organizations_service(client, db_session):
    organization_a = Organization(name="Service Get Tenant A")
    organization_b = Organization(name="Service Get Tenant B")
    db_session.add_all([organization_a, organization_b])
    db_session.flush()

    service = Service(
        name="Private Tenant B Service",
        organization_id=organization_b.id,
    )
    db_session.add(service)
    db_session.flush()

    user_a = User(
        email="service-get-a@example.com",
        name="Service Get User A",
        organization_id=organization_a.id,
    )
    db_session.add(user_a)
    db_session.flush()

    app.dependency_overrides[get_current_user] = lambda: user_a

    try:
        response = client.get(f"/services/{service.id}")
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 404
    assert response.json() == {"detail": "Service not found"}


def test_user_cannot_update_another_organizations_service(client, db_session):
    organization_a = Organization(name="Service Update Tenant A")
    organization_b = Organization(name="Service Update Tenant B")
    db_session.add_all([organization_a, organization_b])
    db_session.flush()

    service = Service(
        name="Original Private Service",
        organization_id=organization_b.id,
    )
    db_session.add(service)
    db_session.flush()

    user_a = User(
        email="service-update-a@example.com",
        name="Service Update User A",
        organization_id=organization_a.id,
    )
    db_session.add(user_a)
    db_session.flush()

    app.dependency_overrides[get_current_user] = lambda: user_a

    try:
        response = client.patch(
            f"/services/{service.id}",
            json={"name": "Unauthorized Rename"},
        )
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 404

    db_session.refresh(service)
    assert service.name == "Original Private Service"


def test_user_cannot_delete_another_organizations_service(client, db_session):
    organization_a = Organization(name="Service Delete Tenant A")
    organization_b = Organization(name="Service Delete Tenant B")
    db_session.add_all([organization_a, organization_b])
    db_session.flush()

    service = Service(
        name="Protected Private Service",
        organization_id=organization_b.id,
    )
    db_session.add(service)
    db_session.flush()
    service_id = service.id

    user_a = User(
        email="service-delete-a@example.com",
        name="Service Delete User A",
        organization_id=organization_a.id,
    )
    db_session.add(user_a)
    db_session.flush()

    app.dependency_overrides[get_current_user] = lambda: user_a

    try:
        response = client.delete(f"/services/{service_id}")
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 404

    db_session.expire_all()
    remaining_service = db_session.get(Service, service_id)
    assert remaining_service is not None
    assert remaining_service.name == "Protected Private Service"


def test_update_service_as_authenticated_user(client, db_session):
    organization = Organization(name="Service Update Success Org")
    db_session.add(organization)
    db_session.flush()

    service = Service(
        name="Old Service Name",
        description="Old description",
        organization_id=organization.id,
    )
    db_session.add(service)
    db_session.flush()

    user = User(
        email="service-update-success@example.com",
        name="Service Update User",
        organization_id=organization.id,
    )
    db_session.add(user)
    db_session.flush()

    app.dependency_overrides[get_current_user] = lambda: user

    try:
        response = client.patch(
            f"/services/{service.id}",
            json={
                "name": "New Service Name",
                "description": "Updated description",
            },
        )
        assert response.status_code == 200
        assert response.json()["name"] == "New Service Name"
        assert response.json()["description"] == "Updated description"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


def test_delete_service_as_authenticated_user(client, db_session):
    organization = Organization(name="Service Delete Success Org")
    db_session.add(organization)
    db_session.flush()

    service = Service(
        name="Service To Delete",
        organization_id=organization.id,
    )
    db_session.add(service)
    db_session.flush()
    service_id = service.id

    user = User(
        email="service-delete-success@example.com",
        name="Service Delete User",
        organization_id=organization.id,
    )
    db_session.add(user)
    db_session.flush()

    app.dependency_overrides[get_current_user] = lambda: user

    try:
        response = client.delete(f"/services/{service_id}")
        assert response.status_code == 204

        # Authentication must remain enabled for this request.
        get_response = client.get(f"/services/{service_id}")
        assert get_response.status_code == 404
    finally:
        app.dependency_overrides.pop(get_current_user, None)


def test_duplicate_service_name_returns_conflict(client, db_session):
    organization = Organization(name="Duplicate Service Test Org")
    db_session.add(organization)
    db_session.flush()

    user = User(
        email="duplicate-service-test@example.com",
        name="Duplicate Service Test User",
        organization_id=organization.id,
    )
    db_session.add(user)
    db_session.flush()

    app.dependency_overrides[get_current_user] = lambda: user

    try:
        first_response = client.post(
            "/services/",
            json={"name": "Rug Cleaning"},
        )
        assert first_response.status_code == 201

        second_response = client.post(
            "/services/",
            json={"name": "Rug Cleaning"},
        )
        assert second_response.status_code == 409
        assert second_response.json() == {
            "detail": (
                "A service with this name already exists " "in your organization."
            )
        }
    finally:
        app.dependency_overrides.pop(get_current_user, None)
