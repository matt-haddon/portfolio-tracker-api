from unittest.mock import MagicMock, patch

import pytest

from prices.services import fetch_and_store_price

pytestmark = pytest.mark.django_db


def test_fetch_and_store_price_raises_on_no_symbol():
    with pytest.raises(ValueError):
        fetch_and_store_price(None)


@patch("prices.services.cache.get")
@patch("prices.services.yf.Ticker")
def test_fetch_and_store_price_returns_cached_price(mock_ticker, mock_cache_get):
    mock_cache_get.return_value = 190.50

    mock_info = MagicMock()
    mock_info.last_price = 100.00
    mock_info.currency = "USD"
    mock_ticker.return_value.fast_info = mock_info

    result = fetch_and_store_price("AAPL")

    assert result == 190.50
    mock_ticker.assert_not_called()


@patch("prices.services.cache.get")
@patch("prices.services.yf.Ticker")
def test_fetch_and_store_price_raises_on_none_price(mock_ticker, mock_cache_get):

    mock_cache_get.return_value = None

    mock_info = MagicMock()
    mock_info.last_price = None
    mock_info.currency = "USD"
    mock_ticker.return_value.fast_info = mock_info

    with pytest.raises(RuntimeError):
        fetch_and_store_price("AAPL")


@patch("prices.services.cache.get")
@patch("prices.services.yf.Ticker")
def test_fetch_and_store_price_fetches_from_yahoo_when_no_cache(mock_ticker, mock_cache_get):
    mock_cache_get.return_value = None

    mock_info = MagicMock()
    mock_info.last_price = 150.50
    mock_info.currency = "USD"
    mock_ticker.return_value.fast_info = mock_info

    result = fetch_and_store_price("AAPL")

    assert result == 150.50
    mock_ticker.assert_called_once_with("AAPL")
