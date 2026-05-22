import pytest

from portfolio.models import Holding, Portfolio

pytestmark = pytest.mark.django_db


def test_portfolio_str(user):
    p = Portfolio.objects.create(owner=user, name="ISA", currency="GBP")
    assert str(p) == "ISA (GBP)"


def test_holding_symbol_normalized(user):
    p = Portfolio.objects.create(owner=user, name="Core", currency="GBP")
    h = Holding.objects.create(
        portfolio=p,
        symbol="vusa.l",
        quantity="1",
        avg_price="10",
    )
    assert h.symbol == "VUSA.L"
    assert str(h).startswith("VUSA.L@")


def test_cost_basis_property(user):
    p = Portfolio.objects.create(owner=user, name="Core", currency="GBP")
    h = Holding.objects.create(
        portfolio=p,
        symbol="AAPL",
        quantity="2",
        avg_price="150",
    )
    assert h.cost_basis == 300


def test_cost_value_equals_none_when_amount_missing(user):
    p = Portfolio.objects.create(owner=user, name="Core", currency="GBP")
    h = Holding.objects.create(
        portfolio=p,
        symbol="AAPL",
        quantity="2",
        avg_price="150",
    )

    h.quantity = None
    assert h.cost_basis is None
