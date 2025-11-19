import pytest
from rest_framework import status

from portfolio.models import Portfolio

pytestmark = pytest.mark.django_db


def test_create_portfolio(auth_client):
    resp = auth_client.post(
        "/api/v1/portfolios/",
        {"name": "Core", "currency": "GBP"},
        format="json",
    )
    assert resp.status_code == status.HTTP_201_CREATED
    body = resp.json()
    assert body["name"] == "Core"
    assert body["currency"] == "GBP"
    assert Portfolio.objects.filter(name="Core").exists()


def test_list_only_own_portfolios(auth_client, other_auth_client):
    # create one for user1
    auth_client.post(
        "/api/v1/portfolios/",
        {"name": "U1", "currency": "GBP"},
        format="json",
    )
    # create one for user2
    other_auth_client.post(
        "/api/v1/portfolios/",
        {"name": "U2", "currency": "USD"},
        format="json",
    )

    resp = auth_client.get("/api/v1/portfolios/")
    assert resp.status_code == 200
    data = resp.json()
    names = [p["name"] for p in data["results"]]
    assert names == ["U1"]


def test_unique_name_per_user(auth_client):
    auth_client.post(
        "/api/v1/portfolios/",
        {"name": "Core", "currency": "GBP"},
        format="json",
    )
    resp = auth_client.post(
        "/api/v1/portfolios/",
        {"name": "Core", "currency": "GBP"},
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize("bad", ["gbp", "GB", "GBPP", "12$", "eur "])
def test_currency_validator_rejects_non_iso(auth_client, bad):
    resp = auth_client.post(
        "/api/v1/portfolios/",
        {"name": "P", "currency": bad},
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


def test_search_and_ordering(auth_client):
    auth_client.post(
        "/api/v1/portfolios/",
        {"name": "Beta", "currency": "GBP"},
        format="json",
    )

    auth_client.post(
        "/api/v1/portfolios/",
        {"name": "Alpha", "currency": "GBP"},
        format="json",
    )

    # search
    r = auth_client.get("/api/v1/portfolios/?search=Alpha")
    assert r.status_code == 200
    data = r.json()
    assert data["count"] == 1
    assert data["results"][0]["name"] == "Alpha"

    # ordering by name asc
    r = auth_client.get("/api/v1/portfolios/?ordering=name")
    assert r.status_code == 200
    names = [p["name"] for p in r.json()["results"]]
    assert names == ["Alpha", "Beta"]


def test_retrieve_other_users_portfolio_returns_404(auth_client, other_auth_client):
    # user2 creates a portfolio
    r = other_auth_client.post(
        "/api/v1/portfolios/",
        {"name": "U2", "currency": "USD"},
        format="json",
    )
    p2_id = r.json()["id"]

    # user1 tries to fetch user2's portfolio
    resp = auth_client.get(f"/api/v1/portfolios/{p2_id}/")
    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_patch_other_users_portfolio_returns_404(auth_client, other_auth_client):
    # user2 creates a portfolio
    r = other_auth_client.post(
        "/api/v1/portfolios/",
        {"name": "U2", "currency": "USD"},
        format="json",
    )
    p2_id = r.json()["id"]

    # user1 tries to update user2's portfolio
    resp = auth_client.patch(
        f"/api/v1/portfolios/{p2_id}/",
        {"name": "Hacked"},
        format="json",
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_delete_other_users_portfolio_returns_404(auth_client, other_auth_client):
    # user2 creates a portfolio
    r = other_auth_client.post(
        "/api/v1/portfolios/",
        {"name": "U2", "currency": "USD"},
        format="json",
    )
    p2_id = r.json()["id"]

    # user1 tries to delete user2's portfolio
    resp = auth_client.delete(f"/api/v1/portfolios/{p2_id}/")
    assert resp.status_code == status.HTTP_404_NOT_FOUND
