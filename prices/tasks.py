import logging

from celery import shared_task

from .services import fetch_and_store_price

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def fetch_price_for_symbol(self, symbol):
    try:
        logger.info("fetching price for %s", symbol)
        fetch_and_store_price(symbol)

    except RuntimeError as e:
        logger.warning("retrying fetch for %s, attempt %s", symbol, self.request.retries)
        self.retry(exc=e)


@shared_task
def fetch_prices(symbols):
    logger.info("dispatching price fetch for %s securities: %s", len(symbols), symbols)
    for symbol in symbols:
        fetch_price_for_symbol.delay(symbol)
