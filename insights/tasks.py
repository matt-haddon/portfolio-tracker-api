import logging

from celery import shared_task

from .services import generate_portfolio_insights

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def fetch_insight_for_portfolio(self, portfolio_id):
    try:
        logger.info("fetching insights for portfolio %s", portfolio_id)
        generate_portfolio_insights(portfolio_id)
        logger.info("successfully generated insights for portfolio %s", portfolio_id)

    except RuntimeError as e:
        logger.warning(
            "retrying fetch for portfolio %s, attempt %s", portfolio_id, self.request.retries
        )
        self.retry(exc=e)
