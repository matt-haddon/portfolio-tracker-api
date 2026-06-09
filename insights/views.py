import logging

from django.core.cache import cache
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from .tasks import fetch_insight_for_portfolio

logger = logging.getLogger(__name__)


class PortfolioInsightsMixin:
    @action(detail=True, methods=["get"], url_path="insights")
    def insights(self, request, pk=None):
        portfolio = self.get_object()
        cache_key = f"insights:{portfolio.id}"

        cached = cache.get(cache_key)
        if cached:
            logger.info("returning cached insights for portfolio %s", portfolio.id)
            return Response({"insights": cached})

        logger.info("generating insights for portfolio %s", portfolio.id)
        fetch_insight_for_portfolio.delay(portfolio.id)
        return Response(
            {"message": "Insights are being generated. Please retry in a few seconds"},
            status=status.HTTP_202_ACCEPTED,
        )
