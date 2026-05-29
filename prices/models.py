from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from core.models import TimeStampedModel


class Price(TimeStampedModel):
    symbol = models.CharField(max_length=32, db_index=True)
    price = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="last updated price for the security",
    )
    currency = models.CharField(
        max_length=3,
        default="GBP",
        validators=[RegexValidator(r"^[A-Z]{3}$", "Use a 3-letter ISO currency code.")],
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["symbol", "currency"], name="uq_price_symbol_currency")
        ]
