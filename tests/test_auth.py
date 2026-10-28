from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_services_requires_authentication():
    response = client.get("/services/")

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required"}
