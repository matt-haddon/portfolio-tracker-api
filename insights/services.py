import logging

import anthropic
from django.conf import settings
from django.core.cache import cache

from portfolio.models import Portfolio
from prices.models import Price

logger = logging.getLogger(__name__)

INSIGHTS_CACHE_KEY = "insights:{portfolio_id}"


def generate_portfolio_insights(portfolio_id: int) -> str:
    cache_key = INSIGHTS_CACHE_KEY.format(portfolio_id=portfolio_id)

    cached = cache.get(cache_key)
    if cached:
        logger.info("returning cached insights for portfolio %s", portfolio_id)
        return cached

    try:
        portfolio = Portfolio.objects.get(id=portfolio_id)
        holdings = portfolio.holdings.all()
        symbols = [h.symbol for h in holdings]
        prices = {p.symbol: p for p in Price.objects.filter(symbol__in=symbols)}

        holdings_data = []
        total_value = sum(
            float(h.quantity) * float(prices[h.symbol].price)
            for h in holdings
            if h.symbol in prices
        )

        for holding in holdings:
            price_obj = prices.get(holding.symbol)
            current_price = price_obj.price if price_obj else None
            value = float(holding.quantity) * float(current_price) if current_price else None
            percentage = (value / total_value * 100) if total_value and value else None
            if percentage:
                holdings_data.append(
                    f"{holding.symbol}: quantity={holding.quantity}, "
                    f"price={current_price}, value={value:.2f}, "
                    f"portfolio_weight={percentage:.1f}%"
                )
            else:
                holdings_data.append(
                    f"{holding.symbol}: quantity={holding.quantity}, price=unavailable"
                )

        holdings_text = "\n".join(holdings_data)

        prompt = f"You are a portfolio analysis tool. Your role is strictly to analyse portfolio composition \
    and structure based on the data provided. You must not provide personalised financial advice, recommendations \
    to buy or sell specific securities, or predictions about future performance.\
    Based on the following portfolio data, provide an objective analysis covering: \
    1. Portfolio composition -- what asset types and sectors are represented \
    2. Concentration risk -- identify any positions representing more than 20% of \
    the total portfolio value \
    3. Diversification -- assess whether the portfolio is broadly or narrowly spread \
    4. General observations about portfolio balance and structure \
    Portfolio data: \
    {holdings_text} \
    Important: This analysis is for informational purposes only. It does not \
    constitute financial advice. Users should consult a qualified financial adviser \
    before making investment decisions."

        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=settings.ANTHROPIC_MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        )

        claude_response = response.content[0].text

        cache.set(cache_key, claude_response, timeout=settings.INSIGHTS_CACHE_TTL)
        logger.info("storing insight for %s in the cache", portfolio_id)
        return claude_response

    except Exception as e:
        logger.exception("failed to generate insight for portfolio %s", portfolio_id)
        raise RuntimeError(f"Failed to generate insight for {portfolio_id}: {e}") from e
