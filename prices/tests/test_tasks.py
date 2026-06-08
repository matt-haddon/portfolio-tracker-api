from unittest.mock import patch

import pytest

from prices.tasks import fetch_price_for_symbol, fetch_prices

pytestmark = pytest.mark.django_db


@patch("prices.tasks.fetch_price_for_symbol.delay")
def test_fetch_prices_dispatches_tasks(mock_delay):

    symbols = ["AAPL", "MSFT"]
    fetch_prices(symbols)
    assert mock_delay.call_count == 2
    mock_delay.assert_any_call("AAPL")
    mock_delay.assert_any_call("MSFT")


@patch("prices.tasks.fetch_and_store_price")
def test_fetch_price_for_symbol_retries_on_failure(mock_fetch):
    mock_fetch.side_effect = RuntimeError("API failed")

    with pytest.raises(RuntimeError):
        fetch_price_for_symbol.apply(args=["AAPL"])
