import pytest
from rest_framework import status

from portfolio.models import Holding, Portfolio

pytestmark = pytest.mark.django_db


@pytest.fixture
def portfolio_u1(user):
    return Portfolio.objects.create(owner=user, name="Main", currency="GBP")


@pytest.fixture
def portfolio_u2(other_user):
    return Portfolio.objects.create(owner=other_user, name="Other", currency="USD")


def test_create_holding_in_own_portfolio(auth_client, portfolio_u1):
    resp = auth_client.post(
        "/api/v1/holdings/",
        {
            "portfolio": portfolio_u1.id,
            "symbol": "aapl",
            "display_name": "Apple",
            "quantity": "10",
            "avg_price": "150",
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_201_CREATED
    h = Holding.objects.get()
    # symbol normalized
    assert h.symbol == "AAPL"


def test_prevent_cross_user_portfolio_reference(auth_client, portfolio_u2):
    # user1 tries to create a holding in user2's portfolio
    resp = auth_client.post(
        "/api/v1/holdings/",
        {
            "portfolio": portfolio_u2.id,
            "symbol": "MSFT",
            "quantity": "1",
            "avg_price": "1",
        },
        format="json",
    )
    # serializer validate() should block this
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


def test_list_only_own_holdings(auth_client, other_auth_client, portfolio_u1, portfolio_u2):
    # user1 holding
    auth_client.post(
        "/api/v1/holdings/",
        {
            "portfolio": portfolio_u1.id,
            "symbol": "VUSA.L",
            "quantity": "2",
            "avg_price": "60",
        },
        format="json",
    )

    # user2 holding
    other_auth_client.post(
        "/api/v1/holdings/",
        {
            "portfolio": portfolio_u2.id,
            "symbol": "TSLA",
            "quantity": "1",
            "avg_price": "100",
        },
        format="json",
    )

    # user1 should only see their own holding
    r = auth_client.get("/api/v1/holdings/")
    assert r.status_code == 200
    data = r.json()
    assert data["count"] == 1
    symbols = [h["symbol"] for h in data["results"]]
    assert symbols == ["VUSA.L"] or symbols == ["VUSA.L".upper()]


def test_case_insensitive_symbol_uniqueness(auth_client, portfolio_u1):
    # first insert
    r1 = auth_client.post(
        "/api/v1/holdings/",
        {
            "portfolio": portfolio_u1.id,
            "symbol": "aapl",
            "quantity": "1",
            "avg_price": "10",
        },
        format="json",
    )
    assert r1.status_code == status.HTTP_201_CREATED

    # attempt duplicate with different case
    r2 = auth_client.post(
        "/api/v1/holdings/",
        {
            "portfolio": portfolio_u1.id,
            "symbol": "AAPL",
            "quantity": "2",
            "avg_price": "20",
        },
        format="json",
    )
    assert r2.status_code == status.HTTP_409_CONFLICT


def test_validation_non_negative(auth_client, portfolio_u1):
    r = auth_client.post(
        "/api/v1/holdings/",
        {
            "portfolio": portfolio_u1.id,
            "symbol": "IBM",
            "quantity": "-1",
            "avg_price": "10",
        },
        format="json",
    )
    assert r.status_code == status.HTTP_400_BAD_REQUEST

    r = auth_client.post(
        "/api/v1/holdings/",
        {
            "portfolio": portfolio_u1.id,
            "symbol": "IBM",
            "quantity": "1",
            "avg_price": "-10",
        },
        format="json",
    )
    assert r.status_code == status.HTTP_400_BAD_REQUEST


def test_search_filter_ordering(auth_client, portfolio_u1):
    auth_client.post(
        "/api/v1/holdings/",
        {"portfolio": portfolio_u1.id, "symbol": "AAPL", "quantity": "1", "avg_price": "10"},
        format="json",
    )
    auth_client.post(
        "/api/v1/holdings/",
        {"portfolio": portfolio_u1.id, "symbol": "MSFT", "quantity": "1", "avg_price": "10"},
        format="json",
    )

    # search by partial symbol
    r = auth_client.get("/api/v1/holdings/?search=MSF")
    assert r.status_code == 200
    data = r.json()
    assert data["count"] == 1
    assert data["results"][0]["symbol"].startswith("MSF")

    # ordering by symbol desc
    r = auth_client.get("/api/v1/holdings/?ordering=-symbol")
    assert r.status_code == 200
    symbols = [h["symbol"] for h in r.json()["results"]]
    assert symbols == sorted(symbols, reverse=True)


def test_retrieve_other_users_holding_returns_404(auth_client, other_auth_client, portfolio_u2):
    # user2 creates a holding
    r = other_auth_client.post(
        "/api/v1/holdings/",
        {
            "portfolio": portfolio_u2.id,
            "symbol": "TSLA",
            "quantity": "1",
            "avg_price": "100",
        },
        format="json",
    )
    h2_id = r.json()["id"]

    # user1 tries to fetch user2's holding
    resp = auth_client.get(f"/api/v1/holdings/{h2_id}/")
    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_patch_other_users_holding_returns_404(auth_client, other_auth_client, portfolio_u2):
    # user2 creates a holding
    r = other_auth_client.post(
        "/api/v1/holdings/",
        {
            "portfolio": portfolio_u2.id,
            "symbol": "TSLA",
            "quantity": "1",
            "avg_price": "100",
        },
        format="json",
    )
    h2_id = r.json()["id"]

    # user1 tries to update user2's holding
    resp = auth_client.patch(
        f"/api/v1/holdings/{h2_id}/",
        {"quantity": "999"},
        format="json",
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_delete_other_users_holding_returns_404(auth_client, other_auth_client, portfolio_u2):
    # user2 creates a holding
    r = other_auth_client.post(
        "/api/v1/holdings/",
        {
            "portfolio": portfolio_u2.id,
            "symbol": "TSLA",
            "quantity": "1",
            "avg_price": "100",
        },
        format="json",
    )
    h2_id = r.json()["id"]

    # user1 tries to delete user2's holding
    resp = auth_client.delete(f"/api/v1/holdings/{h2_id}/")
    assert resp.status_code == status.HTTP_404_NOT_FOUND
