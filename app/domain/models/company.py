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


class Currency(StrEnum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"


@dataclass
class Company:
    """Root entity representing a company in the FP&A system."""

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    name: str = ""
    base_currency: Currency = Currency.USD
    subsidiaries: list[Subsidiary] = field(default_factory=list)

    def add_subsidiary(self, subsidiary: Subsidiary) -> None:
        if any(s.id == subsidiary.id for s in self.subsidiaries):
            raise ValueError(f"Subsidiary {subsidiary.id} already exists")
        subsidiary.parent_company_id = self.id
        self.subsidiaries.append(subsidiary)

    def get_all_entity_ids(self) -> list[uuid.UUID]:
        """Returns IDs of the company and all its subsidiaries."""
        return [self.id] + [s.id for s in self.subsidiaries]


@dataclass
class Subsidiary:
    """A subsidiary belonging to a parent company."""

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    name: str = ""
    currency: Currency = Currency.USD
    parent_company_id: uuid.UUID | None = None
