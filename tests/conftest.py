# filepath: c:\Personal\financial_consolidation_engine\tests\conftest.py
"""Shared pytest fixtures for all test modules.

Provides a realistic SaaS-style chart of accounts, sample companies,
and helper factories for generating transactions.
"""

from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal

import pytest

from app.domain.models.account import Account, AccountCategory, AccountType
from app.domain.models.company import Company, Currency, Subsidiary
from app.domain.models.transaction import Transaction


# ── Fixed UUIDs for deterministic tests ──────────────────────────────────────

PARENT_ENTITY_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
SUB_EU_ENTITY_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")
SUB_ASIA_ENTITY_ID = uuid.UUID("00000000-0000-0000-0000-000000000003")

ACCT_REVENUE_ID = uuid.UUID("10000000-0000-0000-0000-000000000001")
ACCT_OTHER_INCOME_ID = uuid.UUID("10000000-0000-0000-0000-000000000002")
ACCT_COGS_ID = uuid.UUID("10000000-0000-0000-0000-000000000003")
ACCT_SALARIES_ID = uuid.UUID("10000000-0000-0000-0000-000000000004")
ACCT_RENT_ID = uuid.UUID("10000000-0000-0000-0000-000000000005")
ACCT_TAX_ID = uuid.UUID("10000000-0000-0000-0000-000000000006")
ACCT_INTEREST_ID = uuid.UUID("10000000-0000-0000-0000-000000000007")

# EU subsidiary account ids
ACCT_EU_REVENUE_ID = uuid.UUID("20000000-0000-0000-0000-000000000001")
ACCT_EU_COGS_ID = uuid.UUID("20000000-0000-0000-0000-000000000002")
ACCT_EU_SALARIES_ID = uuid.UUID("20000000-0000-0000-0000-000000000003")


# ── Company fixtures ────────────────────────────────────────────────────────


@pytest.fixture()
def parent_company() -> Company:
    """A parent holding company."""
    return Company(
        id=PARENT_ENTITY_ID,
        name="Acme Corp",
        base_currency=Currency.USD,
    )


@pytest.fixture()
def eu_subsidiary() -> Subsidiary:
    """European subsidiary."""
    return Subsidiary(
        id=SUB_EU_ENTITY_ID,
        name="Acme EU",
        currency=Currency.EUR,
    )


@pytest.fixture()
def asia_subsidiary() -> Subsidiary:
    """Asia-Pacific subsidiary."""
    return Subsidiary(
        id=SUB_ASIA_ENTITY_ID,
        name="Acme APAC",
        currency=Currency.JPY,
    )


@pytest.fixture()
def company_with_subsidiaries(
    parent_company: Company,
    eu_subsidiary: Subsidiary,
    asia_subsidiary: Subsidiary,
) -> Company:
    """Parent company with two subsidiaries attached."""
    parent_company.add_subsidiary(eu_subsidiary)
    parent_company.add_subsidiary(asia_subsidiary)
    return parent_company


# ── Chart of Accounts fixtures ──────────────────────────────────────────────


@pytest.fixture()
def parent_accounts() -> list[Account]:
    """Typical SaaS chart of accounts for the parent entity."""
    return [
        Account(
            id=ACCT_REVENUE_ID,
            code="4000",
            name="SaaS Revenue",
            account_type=AccountType.REVENUE,
            category=AccountCategory.OPERATING_REVENUE,
            entity_id=PARENT_ENTITY_ID,
        ),
        Account(
            id=ACCT_OTHER_INCOME_ID,
            code="4500",
            name="Interest Income",
            account_type=AccountType.REVENUE,
            category=AccountCategory.OTHER_INCOME,
            entity_id=PARENT_ENTITY_ID,
        ),
        Account(
            id=ACCT_COGS_ID,
            code="5000",
            name="Hosting Costs",
            account_type=AccountType.EXPENSE,
            category=AccountCategory.COST_OF_GOODS_SOLD,
            entity_id=PARENT_ENTITY_ID,
        ),
        Account(
            id=ACCT_SALARIES_ID,
            code="6000",
            name="Salaries & Wages",
            account_type=AccountType.EXPENSE,
            category=AccountCategory.OPERATING_EXPENSE,
            entity_id=PARENT_ENTITY_ID,
        ),
        Account(
            id=ACCT_RENT_ID,
            code="6100",
            name="Office Rent",
            account_type=AccountType.EXPENSE,
            category=AccountCategory.OPERATING_EXPENSE,
            entity_id=PARENT_ENTITY_ID,
        ),
        Account(
            id=ACCT_TAX_ID,
            code="8000",
            name="Income Tax",
            account_type=AccountType.EXPENSE,
            category=AccountCategory.TAX,
            entity_id=PARENT_ENTITY_ID,
        ),
        Account(
            id=ACCT_INTEREST_ID,
            code="7500",
            name="Interest Expense",
            account_type=AccountType.EXPENSE,
            category=AccountCategory.OTHER_EXPENSE,
            entity_id=PARENT_ENTITY_ID,
        ),
    ]


@pytest.fixture()
def eu_accounts() -> list[Account]:
    """Chart of accounts for the EU subsidiary."""
    return [
        Account(
            id=ACCT_EU_REVENUE_ID,
            code="4000",
            name="SaaS Revenue (EU)",
            account_type=AccountType.REVENUE,
            category=AccountCategory.OPERATING_REVENUE,
            entity_id=SUB_EU_ENTITY_ID,
        ),
        Account(
            id=ACCT_EU_COGS_ID,
            code="5000",
            name="Hosting Costs (EU)",
            account_type=AccountType.EXPENSE,
            category=AccountCategory.COST_OF_GOODS_SOLD,
            entity_id=SUB_EU_ENTITY_ID,
        ),
        Account(
            id=ACCT_EU_SALARIES_ID,
            code="6000",
            name="Salaries (EU)",
            account_type=AccountType.EXPENSE,
            category=AccountCategory.OPERATING_EXPENSE,
            entity_id=SUB_EU_ENTITY_ID,
        ),
    ]


@pytest.fixture()
def all_accounts(
    parent_accounts: list[Account], eu_accounts: list[Account]
) -> list[Account]:
    """Combined chart of accounts for parent + EU subsidiary."""
    return parent_accounts + eu_accounts


# ── Transaction factory helpers ─────────────────────────────────────────────


def make_transaction(
    account_id: uuid.UUID,
    amount: Decimal | str,
    entity_id: uuid.UUID = PARENT_ENTITY_ID,
    transaction_date: date = date(2024, 1, 15),
    description: str = "",
    currency: str = "USD",
) -> Transaction:
    """Convenience factory to create a transaction with sensible defaults."""
    if isinstance(amount, str):
        amount = Decimal(amount)
    return Transaction(
        account_id=account_id,
        entity_id=entity_id,
        transaction_date=transaction_date,
        amount=amount,
        currency=currency,
        description=description,
    )


# ── Pre-built transaction sets ──────────────────────────────────────────────


@pytest.fixture()
def january_transactions() -> list[Transaction]:
    """A realistic set of January 2024 transactions for the parent entity."""
    return [
        make_transaction(ACCT_REVENUE_ID, "100000.00", description="Monthly SaaS subscriptions"),
        make_transaction(ACCT_OTHER_INCOME_ID, "500.00", description="Bank interest"),
        make_transaction(ACCT_COGS_ID, "20000.00", description="AWS hosting"),
        make_transaction(ACCT_SALARIES_ID, "45000.00", description="Jan payroll"),
        make_transaction(ACCT_RENT_ID, "5000.00", description="Office lease"),
        make_transaction(ACCT_TAX_ID, "7000.00", description="Estimated tax"),
        make_transaction(ACCT_INTEREST_ID, "1500.00", description="Loan interest"),
    ]


@pytest.fixture()
def february_transactions() -> list[Transaction]:
    """February 2024 transactions for the parent entity."""
    return [
        make_transaction(
            ACCT_REVENUE_ID, "110000.00",
            transaction_date=date(2024, 2, 15),
            description="Monthly SaaS subscriptions",
        ),
        make_transaction(
            ACCT_COGS_ID, "22000.00",
            transaction_date=date(2024, 2, 15),
            description="AWS hosting",
        ),
        make_transaction(
            ACCT_SALARIES_ID, "46000.00",
            transaction_date=date(2024, 2, 15),
            description="Feb payroll",
        ),
        make_transaction(
            ACCT_RENT_ID, "5000.00",
            transaction_date=date(2024, 2, 15),
            description="Office lease",
        ),
    ]


@pytest.fixture()
def eu_january_transactions() -> list[Transaction]:
    """January 2024 transactions for the EU subsidiary."""
    return [
        make_transaction(
            ACCT_EU_REVENUE_ID, "50000.00",
            entity_id=SUB_EU_ENTITY_ID,
            description="EU SaaS subscriptions",
        ),
        make_transaction(
            ACCT_EU_COGS_ID, "10000.00",
            entity_id=SUB_EU_ENTITY_ID,
            description="EU hosting",
        ),
        make_transaction(
            ACCT_EU_SALARIES_ID, "20000.00",
            entity_id=SUB_EU_ENTITY_ID,
            description="EU payroll",
        ),
    ]
