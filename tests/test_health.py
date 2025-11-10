import pytest

pytestmark = pytest.mark.django_db


def test_health(client):
    resp = client.get("/health/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
