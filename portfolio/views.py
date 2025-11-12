from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import filters, permissions, viewsets

from .models import Holding, Portfolio
from .serializers import HoldingSerializer, PortfolioSerializer


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
        serializer.save(owner=self.request.user)


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
        # Enforce ownership and avoid N+1 with select_related
        return Holding.objects.select_related("portfolio", "portfolio__owner").filter(
            portfolio__owner=self.request.user
        )
