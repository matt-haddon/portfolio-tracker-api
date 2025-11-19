import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db
User = get_user_model()


@pytest.fixture
def user():
    return User.objects.create_user(email="u1@example.com", password="pass1234")


@pytest.fixture
def other_user():
    return User.objects.create_user(email="u2@example.com", password="pass1234")


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(api_client, user):
    """
    API client authenticated as `user` via SimpleJWT.
    Adjust /api/v1/token/ if your token endpoint differs.
    """
    res = api_client.post(
        "/api/v1/token/",
        {"email": user.email, "password": "pass1234"},
        format="json",
    )
    assert res.status_code == 200, res.content
    token = res.json()["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return api_client


@pytest.fixture
def other_auth_client(api_client, other_user):
    """
    API client authenticated as `other_user` via SimpleJWT.
    """
    res = api_client.post(
        "/api/v1/token/",
        {"email": other_user.email, "password": "pass1234"},
        format="json",
    )
    assert res.status_code == 200, res.content
    token = res.json()["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return api_client
