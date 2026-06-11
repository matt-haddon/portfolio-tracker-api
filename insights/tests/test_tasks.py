import pytest
from unittest.mock import patch
from insights.tasks import fetch_insight_for_portfolio

pytestmark = pytest.mark.django_db

@patch("insights.tasks.generate_portfolio_insights")
def test_fetch_insight_for_portfolio_calls_service(mock_generate):
  fetch_insight_for_portfolio.apply(args=[1])
  mock_generate.assert_called_once_with(1)

@patch("insights.tasks.generate_portfolio_insights")
def test_fetch_insight_for_portfolio_retries_on_failure(mock_generate):
  mock_generate.side_effect = RuntimeError("Insight failed")
  fetch_insight_for_portfolio.apply(args=[1])
  assert mock_generate.call_count == 4




