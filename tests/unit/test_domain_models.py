import uuid
from datetime import date
from decimal import Decimal

import pytest

from app.domain.models.account import Account, AccountCategory, AccountType
from app.domain.models.company import Company, Currency, Subsidiary
from app.domain.models.report import PnLReport, PnLLineItem, VarianceLineItem, VarianceReport
from app.domain.models.transaction import Transaction


# =============================================================================
# Company Tests
# =============================================================================
class TestCompany:
    def test_create_company(self) -> None:
        company = Company(name="Acme Corp", base_currency=Currency.USD)
        assert company.name == "Acme Corp"
        assert company.base_currency == Currency.USD
        assert company.id is not None

    def test_add_subsidiary(self) -> None:
        company = Company(name="Parent Corp")
        subsidiary = Subsidiary(name="EU Operations", currency=Currency.EUR)

        company.add_subsidiary(subsidiary)

        assert len(company.subsidiaries) == 1
        assert subsidiary.parent_company_id == company.id

    def test_add_duplicate_subsidiary_raises(self) -> None:
        company = Company(name="Parent Corp")
        subsidiary = Subsidiary(name="EU Operations")
        company.add_subsidiary(subsidiary)

        with pytest.raises(ValueError, match="already exists"):
            company.add_subsidiary(subsidiary)

    def test_get_all_entity_ids(self) -> None:
        company = Company(name="Parent Corp")
        sub1 = Subsidiary(name="Sub 1")
        sub2 = Subsidiary(name="Sub 2")
        company.add_subsidiary(sub1)
        company.add_subsidiary(sub2)

        ids = company.get_all_entity_ids()
        assert len(ids) == 3
        assert company.id in ids
        assert sub1.id in ids
        assert sub2.id in ids

    def test_company_default_currency_is_usd(self) -> None:
        company = Company(name="Test")
        assert company.base_currency == Currency.USD

    def test_subsidiary_tracks_parent(self) -> None:
        company = Company(name="Parent")
        sub = Subsidiary(name="Child")

        assert sub.parent_company_id is None
        company.add_subsidiary(sub)
        assert sub.parent_company_id == company.id


# =============================================================================
# Account Tests
# =============================================================================
class TestAccount:
    def test_valid_revenue_account(self) -> None:
        account = Account(
            code="4000",
            name="Revenue",
            account_type=AccountType.REVENUE,
            category=AccountCategory.OPERATING_REVENUE,
        )
        assert account.code == "4000"
        assert account.is_debit_normal is False

    def test_valid_expense_account(self) -> None:
        account = Account(
            code="6000",
            name="Salaries",
            account_type=AccountType.EXPENSE,
            category=AccountCategory.OPERATING_EXPENSE,
        )
        assert account.is_debit_normal is True

    def test_invalid_category_type_combination_raises(self) -> None:
        with pytest.raises(ValueError, match="incompatible"):
            Account(
                code="4000",
                name="Bad Account",
                account_type=AccountType.ASSET,
                category=AccountCategory.OPERATING_REVENUE,
            )

    def test_debit_normal_for_asset(self) -> None:
        account = Account(
            code="1000",
            name="Cash",
            account_type=AccountType.ASSET,
            category=AccountCategory.CURRENT_ASSET,
        )
        assert account.is_debit_normal is True

    def test_credit_normal_for_liability(self) -> None:
        account = Account(
            code="2000",
            name="Accounts Payable",
            account_type=AccountType.LIABILITY,
            category=AccountCategory.CURRENT_LIABILITY,
        )
        assert account.is_debit_normal is False

    def test_credit_normal_for_equity(self) -> None:
        account = Account(
            code="3000",
            name="Retained Earnings",
            account_type=AccountType.EQUITY,
            category=AccountCategory.SHAREHOLDERS_EQUITY,
        )
        assert account.is_debit_normal is False

    def test_account_is_active_by_default(self) -> None:
        account = Account(
            code="1000",
            name="Cash",
            account_type=AccountType.ASSET,
            category=AccountCategory.CURRENT_ASSET,
        )
        assert account.is_active is True


# =============================================================================
# Transaction Tests
# =============================================================================
class TestTransaction:
    def test_auto_period_from_date(self) -> None:
        txn = Transaction(
            transaction_date=date(2024, 3, 15),
            amount=Decimal("1000.00"),
        )
        assert txn.period_year == 2024
        assert txn.period_month == 3
        assert txn.period_key == "2024-03"

    def test_explicit_period_override(self) -> None:
        txn = Transaction(
            transaction_date=date(2024, 3, 15),
            amount=Decimal("1000.00"),
            period_year=2024,
            period_month=2,
        )
        assert txn.period_key == "2024-02"

    def test_default_amount_is_zero(self) -> None:
        txn = Transaction()
        assert txn.amount == Decimal("0.00")

    def test_default_currency_is_usd(self) -> None:
        txn = Transaction()
        assert txn.currency == "USD"

    def test_period_key_format(self) -> None:
        txn = Transaction(
            transaction_date=date(2024, 1, 5),
            amount=Decimal("500"),
        )
        assert txn.period_key == "2024-01"

    def test_unique_id_generated(self) -> None:
        txn1 = Transaction()
        txn2 = Transaction()
        assert txn1.id != txn2.id

# =============================================================================
# Report Tests
# =============================================================================
class TestPnLReport:
    def test_total_revenue(self) -> None:
        report = PnLReport(
            revenue_items=[
                PnLLineItem(amount=Decimal("100000")),
                PnLLineItem(amount=Decimal("50000")),
            ]
        )
        assert report.total_revenue == Decimal("150000")

    def test_gross_profit(self) -> None:
        report = PnLReport(
            revenue_items=[PnLLineItem(amount=Decimal("200000"))],
            cogs_items=[PnLLineItem(amount=Decimal("50000"))],
        )
        assert report.gross_profit == Decimal("150000")

    def test_operating_income(self) -> None:
        report = PnLReport(
            revenue_items=[PnLLineItem(amount=Decimal("200000"))],
            cogs_items=[PnLLineItem(amount=Decimal("50000"))],
            opex_items=[PnLLineItem(amount=Decimal("80000"))],
        )
        assert report.operating_income == Decimal("70000")

    def test_net_income(self) -> None:
        report = PnLReport(
            revenue_items=[PnLLineItem(amount=Decimal("200000"))],
            cogs_items=[PnLLineItem(amount=Decimal("50000"))],
            opex_items=[PnLLineItem(amount=Decimal("80000"))],
            other_items=[PnLLineItem(amount=Decimal("5000"))],
        )
        # net = 200000 - 50000 - 80000 - 5000 = 65000
        assert report.net_income == Decimal("65000")

    def test_empty_report(self) -> None:
        report = PnLReport()
        assert report.total_revenue == Decimal("0.00")
        assert report.gross_profit == Decimal("0.00")
        assert report.operating_income == Decimal("0.00")
        assert report.net_income == Decimal("0.00")
