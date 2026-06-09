from unittest.mock import MagicMock, patch

import pytest

from insights.services import generate_portfolio_insights

pytestmark = pytest.mark.django_db


@patch("insights.services.cache.get")
@patch("insights.services.anthropic.Anthropic")
def test_generate_portfolio_insights_returns_cached_insight(mock_anthropic, mock_cache_get):

    mock_cache_get.return_value = "This is an AI insight"

    result = generate_portfolio_insights(1)

    assert result == "This is an AI insight"
    mock_anthropic.assert_not_called()


@patch("insights.services.cache.set")
@patch("insights.services.cache.get")
@patch("insights.services.Price.objects.filter")
@patch("insights.services.Portfolio.objects.get")
@patch("insights.services.anthropic.Anthropic")
def test_generate_portfolio_insights_calls_claude_on_cache_miss(
    mock_anthropic, mock_portfolio_get, mock_price_filter, mock_cache_get, mock_cache_set
):
    # cache miss
    mock_cache_get.return_value = None

    # mock holding
    mock_holding = MagicMock()
    mock_holding.symbol = "AAPL"
    mock_holding.quantity = 10

    # mock portfolio with holdings
    mock_portfolio = MagicMock()
    mock_portfolio.holdings.all.return_value = [mock_holding]
    mock_portfolio_get.return_value = mock_portfolio

    # mock price
    mock_price = MagicMock()
    mock_price.symbol = "AAPL"
    mock_price.price = 182.50
    mock_price_filter.return_value = [mock_price]

    # mock Claude response
    mock_message = MagicMock()
    mock_message.content[0].text = "This is an AI insight"
    mock_anthropic.return_value.messages.create.return_value = mock_message

    result = generate_portfolio_insights(1)

    assert result == "This is an AI insight"
    mock_cache_set.assert_called_once()


@patch("insights.services.cache.set")
@patch("insights.services.cache.get")
@patch("insights.services.Price.objects.filter")
@patch("insights.services.Portfolio.objects.get")
@patch("insights.services.anthropic.Anthropic")
def test_generate_portfolio_insights_raises_on_failure(
    mock_anthropic, mock_portfolio_get, mock_price_filter, mock_cache_get, mock_cache_set
):

    # cache miss
    mock_cache_get.return_value = None

    # mock holding
    mock_holding = MagicMock()
    mock_holding.symbol = "AAPL"
    mock_holding.quantity = 10

    # mock portfolio with holdings
    mock_portfolio = MagicMock()
    mock_portfolio.holdings.all.return_value = [mock_holding]
    mock_portfolio_get.return_value = mock_portfolio

    # mock price
    mock_price = MagicMock()
    mock_price.symbol = "AAPL"
    mock_price.price = 182.50
    mock_price_filter.return_value = [mock_price]

    # mock Claude response
    mock_anthropic.return_value.messages.create.side_effect = Exception("API error")

    with pytest.raises(RuntimeError):
        generate_portfolio_insights(1)

    mock_cache_set.assert_not_called()
