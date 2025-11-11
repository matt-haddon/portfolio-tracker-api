import pytest
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


def test_validation_shape(client: APIClient):
    # Hit an endpoint you know validates input (later: portfolio create)
    # For now, sanity-check a 404 using /users/me without auth:
    resp = client.get("/api/v1/users/me/")
    assert resp.status_code == 401
    body = resp.json()
    assert set(body.keys()) >= {"code", "message"}
    assert body["code"] in {"not_authenticated", "authentication_failed"}


def test_health_ok(client: APIClient):
    resp = client.get("/health/")
    assert resp.status_code == 200
