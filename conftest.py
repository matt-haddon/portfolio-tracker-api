import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()

TOKEN_URL = "/api/v1/auth/token/"


@pytest.fixture
def user():
    return User.objects.create_user(email="u1@example.com", password="pass1234")  # type: ignore[attr-defined]


@pytest.fixture
def other_user():
    return User.objects.create_user(email="u2@example.com", password="pass1234")  # type: ignore[attr-defined]


@pytest.fixture
def auth_client(user):
    """
    API client authenticated as `user` via SimpleJWT.
    Adjust TOKEN_URL if your token endpoint differs.
    """

    client = APIClient()
    res = client.post(
        TOKEN_URL,
        {"email": user.email, "password": "pass1234"},
        format="json",
    )
    assert res.status_code == 200, res.content
    token = res.json()["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.fixture
def other_auth_client(other_user):
    """
    API client authenticated as `other_user` via SimpleJWT.
    """

    client = APIClient()
    res = client.post(
        TOKEN_URL,
        {"email": other_user.email, "password": "pass1234"},
        format="json",
    )
    assert res.status_code == 200, res.content
    token = res.json()["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.fixture
def portfolio(user):
    from portfolio.models import Portfolio

    return Portfolio.objects.create(owner=user, name="Main", currency="GBP")


@pytest.fixture
def holding(portfolio):
    from portfolio.models import Holding

    return Holding.objects.create(
        portfolio=portfolio, symbol="AAPL", quantity="10", avg_price="150"
    )
