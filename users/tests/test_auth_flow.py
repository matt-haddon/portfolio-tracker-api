# users/tests/test_auth_flow.py
from typing import cast

import pytest
from django.contrib.auth import get_user_model

from users.models import CustomUser, UserManager

pytestmark = (
    pytest.mark.django_db
)  # must appear before tests, but DB work still must be inside tests


def test_jwt_login_and_me_flow(client):
    User = cast(type[CustomUser], get_user_model())
    manager = cast(UserManager, User.objects)

    # ✅ DB access happens inside the test function
    manager.create_user(
        email="test@example.com",
        password="pass123",
        first_name="T",
        last_name="E",
    )

    # Obtain tokens
    resp = client.post(
        "/api/v1/auth/token/",
        {"email": "test@example.com", "password": "pass123"},
        content_type="application/json",
    )
    assert resp.status_code == 200
    access = resp.json()["access"]

    # GET /users/me/
    resp = client.get("/api/v1/users/me/", HTTP_AUTHORIZATION=f"Bearer {access}")
    assert resp.status_code == 200
    assert resp.json()["email"] == "test@example.com"

    # PATCH name
    resp = client.patch(
        "/api/v1/users/me/",
        {"first_name": "New"},
        content_type="application/json",
        HTTP_AUTHORIZATION=f"Bearer {access}",
    )
    assert resp.status_code == 200
    assert resp.json()["first_name"] == "New"
