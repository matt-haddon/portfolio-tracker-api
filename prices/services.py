import logging

import yfinance as yf
from django.conf import settings
from django.core.cache import cache

from .models import Price

logger = logging.getLogger(__name__)


def fetch_and_store_price(symbol):
    if symbol is None:
        raise ValueError("No symbol provided")

    cached_price = cache.get(f"price:{symbol}")

    if not cached_price:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.fast_info
            price = info.last_price
            currency = info.currency

            if price is None:
                logger.warning("No price returned for symbol: %s", symbol)
                raise ValueError(f"No price returned for symbol: {symbol}")

            Price.objects.update_or_create(
                symbol=symbol, currency=currency, defaults={"price": price}
            )
            logger.info("fetched price for %s: %s %s", symbol, price, currency)

            cache.set(f"price:{symbol}", price, timeout=settings.PRICE_CACHE_TTL)
            logger.info("storing price for %s in the cache", symbol)

            return price

        except Exception as e:
            logger.exception("failed to fetch price for %s: %s", symbol, e)
            raise RuntimeError(f"Failed to fetch price for {symbol}: {e}") from e

    logger.info("returning cached price for %s", symbol)
    return cached_price
