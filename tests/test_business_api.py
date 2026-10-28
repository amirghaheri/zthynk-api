from app.auth.dependencies import get_current_user
from app.db_models.organization import Organization
from app.db_models.user import User
from app.main import app
from app.db_models.business import Business


def test_create_business_as_authenticated_user(client, db_session):
    # Create an organization for our test user.
    organization = Organization(name="API Test Organization")
    db_session.add(organization)
    db_session.flush()

    # Create a user who belongs to that organization.
    user = User(
        email="api-test@example.com",
        name="API Test User",
        organization_id=organization.id,
    )
    db_session.add(user)
    db_session.flush()

    # Simulate an authenticated user for this test.
    app.dependency_overrides[get_current_user] = lambda: user

    try:
        response = client.post(
            "/businesses/",
            json={
                "name": "API Test Business",
                "city": "Magnolia",
                "state": "TX",
            },
        )
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    # Verify the API response.
    assert response.status_code == 201

    data = response.json()
    assert data["name"] == "API Test Business"
    assert data["city"] == "Magnolia"
    assert data["state"] == "TX"
    assert data["organization_id"] == str(organization.id)


def test_user_cannot_access_another_organizations_business(client, db_session):
    # Create two separate organizations.
    organization_a = Organization(name="Tenant A API Test")
    organization_b = Organization(name="Tenant B API Test")
    db_session.add_all([organization_a, organization_b])
    db_session.flush()

    # Create a business owned by organization B.
    from app.db_models.business import Business

    business = Business(
        name="Tenant B Private Business",
        organization_id=organization_b.id,
    )
    db_session.add(business)
    db_session.flush()

    # Authenticate as a user from organization A.
    user_a = User(
        email="tenant-a-api@example.com",
        name="Tenant A User",
        organization_id=organization_a.id,
    )
    db_session.add(user_a)
    db_session.flush()

    app.dependency_overrides[get_current_user] = lambda: user_a

    try:
        response = client.get(f"/businesses/{business.id}")
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    # The other organization's business must not be accessible.
    assert response.status_code == 404
    assert response.json() == {"detail": "Business not found"}


def test_list_businesses_only_returns_own_organization(client, db_session):
    organization_a = Organization(name="List Test Tenant A")
    organization_b = Organization(name="List Test Tenant B")
    db_session.add_all([organization_a, organization_b])
    db_session.flush()

    from app.db_models.business import Business

    db_session.add_all(
        [
            Business(
                name="Business A",
                organization_id=organization_a.id,
            ),
            Business(
                name="Business B",
                organization_id=organization_b.id,
            ),
        ]
    )
    db_session.flush()

    user_a = User(
        email="list-tenant-a@example.com",
        name="List Tenant A User",
        organization_id=organization_a.id,
    )
    db_session.add(user_a)
    db_session.flush()

    app.dependency_overrides[get_current_user] = lambda: user_a

    try:
        response = client.get("/businesses/")
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 200

    businesses = response.json()
    assert len(businesses) == 1
    assert businesses[0]["name"] == "Business A"
    assert businesses[0]["organization_id"] == str(organization_a.id)


def test_update_business_as_authenticated_user(client, db_session):
    organization = Organization(name="Update Test Organization")
    db_session.add(organization)
    db_session.flush()

    business = Business(
        name="Original Business Name",
        organization_id=organization.id,
    )
    db_session.add(business)
    db_session.flush()

    user = User(
        email="update-test@example.com",
        name="Update Test User",
        organization_id=organization.id,
    )
    db_session.add(user)
    db_session.flush()

    app.dependency_overrides[get_current_user] = lambda: user

    try:
        response = client.patch(
            f"/businesses/{business.id}",
            json={"name": "Updated Business Name"},
        )
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Business Name"


def test_delete_business_as_authenticated_user(client, db_session):
    organization = Organization(name="Delete Test Organization")
    db_session.add(organization)
    db_session.flush()

    business = Business(
        name="Business To Delete",
        organization_id=organization.id,
    )
    db_session.add(business)
    db_session.flush()

    user = User(
        email="delete-test@example.com",
        name="Delete Test User",
        organization_id=organization.id,
    )
    db_session.add(user)
    db_session.flush()

    app.dependency_overrides[get_current_user] = lambda: user

    try:
        response = client.delete(f"/businesses/{business.id}")
        assert response.status_code == 204

        # Keep authentication enabled for the follow-up request.
        get_response = client.get(f"/businesses/{business.id}")
        assert get_response.status_code == 404
    finally:
        app.dependency_overrides.pop(get_current_user, None)


def test_user_cannot_update_another_organizations_business(client, db_session):
    organization_a = Organization(name="Update Security Tenant A")
    organization_b = Organization(name="Update Security Tenant B")
    db_session.add_all([organization_a, organization_b])
    db_session.flush()

    business = Business(
        name="Tenant B Business",
        organization_id=organization_b.id,
    )
    db_session.add(business)
    db_session.flush()

    user_a = User(
        email="update-security-a@example.com",
        name="Tenant A User",
        organization_id=organization_a.id,
    )
    db_session.add(user_a)
    db_session.flush()

    app.dependency_overrides[get_current_user] = lambda: user_a

    try:
        response = client.patch(
            f"/businesses/{business.id}",
            json={"name": "Unauthorized Change"},
        )
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 404

    # Confirm the original business name is unchanged.
    db_session.refresh(business)
    assert business.name == "Tenant B Business"


def test_user_cannot_delete_another_organizations_business(client, db_session):
    organization_a = Organization(name="Delete Security Tenant A")
    organization_b = Organization(name="Delete Security Tenant B")
    db_session.add_all([organization_a, organization_b])
    db_session.flush()

    business = Business(
        name="Protected Tenant B Business",
        organization_id=organization_b.id,
    )
    db_session.add(business)
    db_session.flush()
    business_id = business.id

    user_a = User(
        email="delete-security-a@example.com",
        name="Tenant A User",
        organization_id=organization_a.id,
    )
    db_session.add(user_a)
    db_session.flush()

    app.dependency_overrides[get_current_user] = lambda: user_a

    try:
        response = client.delete(f"/businesses/{business_id}")
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 404

    # Confirm the business still exists.
    db_session.expire_all()
    remaining_business = db_session.get(Business, business_id)
    assert remaining_business is not None
    assert remaining_business.name == "Protected Tenant B Business"
