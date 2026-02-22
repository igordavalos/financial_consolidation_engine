from __future__ import annotations

import sys
import uuid
from dataclasses import dataclass, field
from enum import Enum

# Python 3.10 compatibility
if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    class StrEnum(str, Enum):
        """String Enum for Python 3.10 compatibility."""
        pass


class AccountType(StrEnum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"


class AccountCategory(StrEnum):
    """Subcategories for P&L and Balance Sheet grouping."""

    OPERATING_REVENUE = "operating_revenue"
    COST_OF_GOODS_SOLD = "cost_of_goods_sold"
    OPERATING_EXPENSE = "operating_expense"
    OTHER_INCOME = "other_income"
    OTHER_EXPENSE = "other_expense"
    TAX = "tax"
    CURRENT_ASSET = "current_asset"
    FIXED_ASSET = "fixed_asset"
    CURRENT_LIABILITY = "current_liability"
    LONG_TERM_LIABILITY = "long_term_liability"
    SHAREHOLDERS_EQUITY = "shareholders_equity"


# Mapping: which categories belong to which account types
CATEGORY_TYPE_MAP: dict[AccountCategory, AccountType] = {
    AccountCategory.OPERATING_REVENUE: AccountType.REVENUE,
    AccountCategory.COST_OF_GOODS_SOLD: AccountType.EXPENSE,
    AccountCategory.OPERATING_EXPENSE: AccountType.EXPENSE,
    AccountCategory.OTHER_INCOME: AccountType.REVENUE,
    AccountCategory.OTHER_EXPENSE: AccountType.EXPENSE,
    AccountCategory.TAX: AccountType.EXPENSE,
    AccountCategory.CURRENT_ASSET: AccountType.ASSET,
    AccountCategory.FIXED_ASSET: AccountType.ASSET,
    AccountCategory.CURRENT_LIABILITY: AccountType.LIABILITY,
    AccountCategory.LONG_TERM_LIABILITY: AccountType.LIABILITY,
    AccountCategory.SHAREHOLDERS_EQUITY: AccountType.EQUITY,
}


@dataclass
class Account:
    """A financial account in the chart of accounts."""

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    code: str = ""
    name: str = ""
    account_type: AccountType = AccountType.EXPENSE
    category: AccountCategory = AccountCategory.OPERATING_EXPENSE
    entity_id: uuid.UUID = field(default_factory=uuid.uuid4)
    parent_account_id: uuid.UUID | None = None
    is_active: bool = True

    def __post_init__(self) -> None:
        expected_type = CATEGORY_TYPE_MAP.get(self.category)
        if expected_type and expected_type != self.account_type:
            raise ValueError(
                f"Category '{self.category}' is incompatible with "
                f"account type '{self.account_type}' (expected '{expected_type}')"
            )

    @property
    def is_debit_normal(self) -> bool:
        """Assets and Expenses have debit normal balances."""
        return self.account_type in (AccountType.ASSET, AccountType.EXPENSE)
