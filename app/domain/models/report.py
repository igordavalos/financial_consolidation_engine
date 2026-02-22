from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
import uuid


@dataclass
class PnLLineItem:
    """A single line in a Profit & Loss report."""

    account_id: uuid.UUID | None = None
    account_code: str = ""
    account_name: str = ""
    category: str = ""
    amount: Decimal = Decimal("0.00")
    percentage_of_revenue: Decimal = Decimal("0.00")


@dataclass
class PnLReport:
    """Profit & Loss (Income Statement) report."""

    entity_name: str = ""
    period: str = ""
    currency: str = "USD"
    revenue_items: list[PnLLineItem] = field(default_factory=list)
    cogs_items: list[PnLLineItem] = field(default_factory=list)
    opex_items: list[PnLLineItem] = field(default_factory=list)
    other_items: list[PnLLineItem] = field(default_factory=list)

    @property
    def total_revenue(self) -> Decimal:
        return sum((item.amount for item in self.revenue_items), Decimal("0.00"))

    @property
    def gross_profit(self) -> Decimal:
        total_cogs = sum((item.amount for item in self.cogs_items), Decimal("0.00"))
        return self.total_revenue - total_cogs

    @property
    def operating_income(self) -> Decimal:
        total_opex = sum((item.amount for item in self.opex_items), Decimal("0.00"))
        return self.gross_profit - total_opex

    @property
    def net_income(self) -> Decimal:
        total_other = sum((item.amount for item in self.other_items), Decimal("0.00"))
        return self.operating_income - total_other


@dataclass
class VarianceLineItem:
    """A single line in a Budget vs Actual variance report."""

    account_code: str = ""
    account_name: str = ""
    category: str = ""
    budget_amount: Decimal = Decimal("0.00")
    actual_amount: Decimal = Decimal("0.00")

    @property
    def variance_amount(self) -> Decimal:
        return self.actual_amount - self.budget_amount

    @property
    def variance_percentage(self) -> Decimal:
        if self.budget_amount == 0:
            return Decimal("0.00")
        return (self.variance_amount / self.budget_amount * 100).quantize(Decimal("0.01"))


@dataclass
class VarianceReport:
    """Budget vs Actual variance report."""

    entity_name: str = ""
    period: str = ""
    currency: str = "USD"
    line_items: list[VarianceLineItem] = field(default_factory=list)

    @property
    def total_budget(self) -> Decimal:
        return sum((item.budget_amount for item in self.line_items), Decimal("0.00"))

    @property
    def total_actual(self) -> Decimal:
        return sum((item.actual_amount for item in self.line_items), Decimal("0.00"))

    @property
    def total_variance(self) -> Decimal:
        return self.total_actual - self.total_budget
