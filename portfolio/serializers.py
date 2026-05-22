import logging
from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Holding, Portfolio

User = get_user_model()
logger = logging.getLogger(__name__)


class PortfolioSerializer(serializers.ModelSerializer):
    # Owner is always the authenticated user
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Portfolio
        fields = ["id", "name", "currency", "created_at", "updated_at", "owner"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_name(self, value: str) -> str:
        # Optional: nicer API error, DB constraint already enforces uniqueness
        user = self.context["request"].user
        if Portfolio.objects.filter(owner=user, name=value).exists():
            raise serializers.ValidationError("Portfolio name must be unique per user.")
        return value


class HoldingSerializer(serializers.ModelSerializer):
    # Keep `symbol` normalized even if model.save() handles it; serializer ensures consistency on input
    symbol = serializers.CharField()
    cost_basis = serializers.SerializerMethodField()

    class Meta:
        model = Holding
        fields = [
            "id",
            "portfolio",
            "symbol",
            "display_name",
            "quantity",
            "avg_price",
            "notes",
            "created_at",
            "updated_at",
            "cost_basis",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    # Filter the `portfolio` FK to only those owned by the current user
    def get_fields(self) -> dict[str, serializers.Field]:
        fields = super().get_fields()
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            fields["portfolio"].queryset = Portfolio.objects.filter(owner=request.user)  # type: ignore[attr-defined]
        else:
            fields["portfolio"].queryset = Portfolio.objects.none()  # type: ignore[attr-defined]
        return fields

    def get_cost_basis(self, obj):
        return obj.cost_basis

    def validate_symbol(self, value: str) -> str:
        return value.upper()

    # Extra ownership check (defensive)
    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        user = self.context["request"].user
        portfolio = attrs.get("portfolio") or getattr(self.instance, "portfolio", None)
        if portfolio and portfolio.owner_id != user.id:
            logger.warning(
                "user %s is attempting to access portfolio %s that they do not own",
                user.id,
                portfolio.id,
            )
            raise serializers.ValidationError("You do not own this portfolio.")
        return attrs
