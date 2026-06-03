import logging
from decimal import Decimal

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from prices.models import Price
from prices.services import fetch_and_store_price

from .models import Holding, Portfolio
from .serializers import HoldingSerializer, PortfolioSerializer

logger = logging.getLogger(__name__)


class IsAuthenticated(permissions.IsAuthenticated):
    """Alias for clarity; all endpoints require login."""

    pass


@extend_schema(tags=["portfolios"])
class PortfolioViewSet(viewsets.ModelViewSet):
    """
    Auto-wires CRUD for /api/portfolios/ and /api/portfolios/{id}/
    - list / retrieve: only your portfolios
    - create: owner set to the logged-in user
    """

    serializer_class = PortfolioSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ["currency"]
    search_fields = ["name"]
    ordering_fields = ["created_at", "name"]
    ordering = ["id"]

    def get_queryset(self):
        # Enforce ownership for reads
        return Portfolio.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        # Enforce ownership for writes
        portfolio = serializer.save(owner=self.request.user)
        logger.info("portfolio %s created by user %s", portfolio.id, self.request.user.id)  # type: ignore[union-attr]

    def perform_destroy(self, instance):
        logger.info("portfolio %s destroyed by user %s", instance.id, self.request.user.id)  # type: ignore[union-attr]
        instance.delete()


@extend_schema(tags=["holdings"])
class HoldingViewSet(viewsets.ModelViewSet):
    """
    Auto-wires CRUD for /api/holdings/ and /api/holdings/{id}/
    - list / retrieve: only holdings in your portfolios
    - create/update: portfolio must belong to you (serializer double-checks)
    """

    serializer_class = HoldingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ["portfolio", "symbol"]
    search_fields = ["symbol", "display_name", "notes"]
    ordering_fields = ["created_at", "symbol"]
    ordering = ["id"]

    def get_queryset(self):
        logger.debug("user %s querying holdings", self.request.user.id)  # type: ignore[union-attr]
        # Enforce ownership and avoid N+1 with select_related
        return Holding.objects.select_related("portfolio", "portfolio__owner").filter(
            portfolio__owner=self.request.user
        )

    def perform_create(self, serializer):
        holding = serializer.save()
        logger.info(
            "holding %s (%s) created by user %s", holding.id, holding.symbol, self.request.user.id  # type: ignore[union-attr]
        )

    def perform_destroy(self, instance):
        logger.info("holding %s destroyed by user %s", instance.id, self.request.user.id)  # type: ignore[union-attr]
        instance.delete()

    @action(detail=True, methods=["get"], url_path="valuation")
    def valuation(self, request, pk=None):

        holding = self.get_object()
        logger.info(
            "valuation requested for holding %s (%s) by user %s",
            holding.id,
            holding.symbol,
            request.user.id,
        )
        try:
            current_price = fetch_and_store_price(holding.symbol)
        except RuntimeError:
            return Response(
                {"message": "Unable to fetch price for this symbol"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        price_obj = Price.objects.filter(symbol=holding.symbol).first()
        price_updated_at = price_obj.updated_at if price_obj else None

        try:
            value = Decimal(str(current_price)) * Decimal(holding.quantity)
        except Exception:
            logger.warning(
                "could not calculate value for holding %s, price: %s", holding.id, current_price
            )
            value = None

        return Response(
            {
                "symbol": holding.symbol,
                "price": current_price,
                "quantity": holding.quantity,
                "value": value,
                "currency": price_obj.currency if price_obj else None,
                "price_updated_at": price_updated_at,
            }
        )
