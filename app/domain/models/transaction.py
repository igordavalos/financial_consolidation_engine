from __future__ import annotations

import sys
import uuid
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from enum import Enum

# Python 3.10 compatibility
if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    class StrEnum(str, Enum):
        """String Enum for Python 3.10 compatibility."""
        pass


class TransactionSource(StrEnum):
    MANUAL = "manual"
    QUICKBOOKS = "quickbooks"
    XERO = "xero"
    CSV_IMPORT = "csv_import"


@dataclass
class Transaction:
    """A financial transaction (journal entry line)."""

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    account_id: uuid.UUID = field(default_factory=uuid.uuid4)
    entity_id: uuid.UUID = field(default_factory=uuid.uuid4)
    transaction_date: date = field(default_factory=date.today)
    amount: Decimal = Decimal("0.00")
    currency: str = "USD"
    description: str = ""
    source: TransactionSource = TransactionSource.MANUAL
    reference: str = ""
    period_year: int = 0
    period_month: int = 0

    def __post_init__(self) -> None:
        if self.period_year == 0:
            self.period_year = self.transaction_date.year
        if self.period_month == 0:
            self.period_month = self.transaction_date.month

    @property
    def period_key(self) -> str:
        """Returns a string key like '2024-01' for grouping."""
        return f"{self.period_year:04d}-{self.period_month:02d}"
