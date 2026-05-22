import pytest
from rest_framework import status
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


def test_unauthenticated_user_cant_see_portfolios():
    client = APIClient()
    resp = client.get("/api/v1/portfolios/")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_unauthenticated_user_cant_see_holdings():
    client = APIClient()
    resp = client.get("/api/v1/holdings/")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
