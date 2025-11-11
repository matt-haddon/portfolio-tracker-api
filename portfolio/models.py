from __future__ import annotations

from django.conf import settings
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.db.models.functions import Upper

from core.models import TimeStampedModel

User = settings.AUTH_USER_MODEL


class Portfolio(TimeStampedModel):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="portfolios")
    name = models.CharField(max_length=120)
    currency = models.CharField(
        max_length=3,
        default="GBP",
        validators=[RegexValidator(r"^[A-Z]{3}$", "Use a 3-letter ISO currency code.")],
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "name"],
                name="uq_portfolio_owner_name",
            )
        ]
        ordering = ["id"]

    def __str__(self):
        return f"{self.name} ({self.currency})"


class Holding(TimeStampedModel):
    portfolio = models.ForeignKey(
        "portfolio.Portfolio", on_delete=models.CASCADE, related_name="holdings"
    )
    portfolio_id: int | None

    # Canonical uppercase trading symbol (e.g., AAPL, VUSA.L)
    symbol = models.CharField(max_length=32)
    display_name = models.CharField(max_length=160, blank=True, default="")
    quantity = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        validators=[MinValueValidator(0)],
        help_text="Number of units or shares held.",
    )
    avg_price = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        validators=[MinValueValidator(0)],
        help_text="Average cost per unit in the portfolio’s base currency.",
    )
    notes = models.TextField(blank=True, default="")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Upper("symbol"),
                "portfolio",
                name="uq_holding_portfolio_symbol_upper",
            )
        ]
        ordering = ["id"]

    def __str__(self):
        return f"{self.symbol}@{self.portfolio_id or 'unsaved'}"

    def save(self, *args, **kwargs):
        """Ensure symbol is always stored uppercase before saving."""
        if self.symbol:
            self.symbol = self.symbol.upper()
        super().save(*args, **kwargs)

    @property
    def cost_basis(self):
        """
        Convenience property — total amount invested (quantity * avg_price).
        Not stored in the DB, just computed on demand.
        """
        if self.quantity is None or self.avg_price is None:
            return None
        return self.quantity * self.avg_price
