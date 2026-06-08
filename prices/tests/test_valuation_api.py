from unittest.mock import patch

import pytest

from prices.models import Price

pytestmark = pytest.mark.django_db


@patch("portfolio.views.fetch_and_store_price")
def test_valuation_returns_correct_data(mock_fetch, auth_client, holding):
    mock_fetch.return_value = 182.50

    Price.objects.create(
        symbol="AAPL",
        price="182.50",
        currency="USD",
    )

    resp = auth_client.get(f"/api/v1/holdings/{holding.id}/valuation/")

    assert resp.status_code == 200
    data = resp.json()
    assert data["symbol"] == "AAPL"
    assert data["price"] == 182.50
    assert data["currency"] == "USD"
    assert data["value"] is not None


@patch("portfolio.views.fetch_and_store_price")
def test_valuation_returns_503_when_price_unavailable(mock_fetch, auth_client, holding):

    mock_fetch.side_effect = RuntimeError("API failed")

    resp = auth_client.get(f"/api/v1/holdings/{holding.id}/valuation/")

    assert resp.status_code == 503
    assert resp.json()["message"] == "Unable to fetch price for this symbol"


@patch("portfolio.views.fetch_and_store_price")
def test_valuation_returns_404_for_other_users_holding(mock_fetch, other_auth_client, holding):
    mock_fetch.return_value = 182.50

    Price.objects.create(
        symbol="AAPL",
        price="182.50",
        currency="USD",
    )

    resp = other_auth_client.get(f"/api/v1/holdings/{holding.id}/valuation/")

    assert resp.status_code == 404
