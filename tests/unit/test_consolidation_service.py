# filepath: c:\Personal\financial_consolidation_engine\tests\unit\test_consolidation_service.py
"""Tests for the ConsolidationService.

Covers:
  - Single-entity P&L consolidation
  - Multi-entity (parent + subsidiary) consolidation
  - Period-level aggregation (monthly reports)
  - Revenue percentage calculation
  - Error handling (unknown accounts, empty data)
  - Edge cases (zero revenue, single transaction, balance-sheet-only txns)
"""

from __future__ import annotations

import uuid
from decimal import Decimal

import pytest

from app.domain.exceptions import ConsolidationError, InsufficientDataError
from app.domain.models.account import Account, AccountCategory, AccountType
from app.domain.models.transaction import Transaction
from app.domain.services.consolidation_service import ConsolidationService
from tests.conftest import (
    ACCT_COGS_ID,
    ACCT_EU_REVENUE_ID,
    ACCT_REVENUE_ID,
    PARENT_ENTITY_ID,
    SUB_EU_ENTITY_ID,
    make_transaction,
)


@pytest.fixture()
def service() -> ConsolidationService:
    return ConsolidationService()


# =============================================================================
# consolidate_pnl — Single Entity
# =============================================================================
class TestConsolidatePnl:
    """Tests for ConsolidationService.consolidate_pnl()."""

    def test_basic_pnl_report(
        self,
        service: ConsolidationService,
        january_transactions: list[Transaction],
        parent_accounts: list[Account],
    ) -> None:
        """Produces a valid P&L from a typical month of transactions."""
        report = service.consolidate_pnl(
            transactions=january_transactions,
            accounts=parent_accounts,
            entity_name="Acme Corp",
            period="2024-01",
            currency="USD",
        )

        assert report.entity_name == "Acme Corp"
        assert report.period == "2024-01"
        assert report.currency == "USD"

    def test_revenue_total(
        self,
        service: ConsolidationService,
        january_transactions: list[Transaction],
        parent_accounts: list[Account],
    ) -> None:
        """Total revenue = SaaS Revenue (100k) + Interest Income (500)."""
        report = service.consolidate_pnl(
            transactions=january_transactions,
            accounts=parent_accounts,
        )
        # Revenue items include OPERATING_REVENUE and OTHER_INCOME
        assert report.total_revenue == Decimal("100500.00")

    def test_gross_profit(
        self,
        service: ConsolidationService,
        january_transactions: list[Transaction],
        parent_accounts: list[Account],
    ) -> None:
        """Gross profit = total_revenue - COGS = 100500 - 20000 = 80500."""
        report = service.consolidate_pnl(
            transactions=january_transactions,
            accounts=parent_accounts,
        )
        assert report.gross_profit == Decimal("80500.00")

    def test_operating_income(
        self,
        service: ConsolidationService,
        january_transactions: list[Transaction],
        parent_accounts: list[Account],    ) -> None:
        """Operating income = gross_profit - opex = 80500 - 50000 = 30500."""
        report = service.consolidate_pnl(
            transactions=january_transactions,
            accounts=parent_accounts,
        )
        # opex: salaries 45000 + rent 5000 = 50000
        assert report.operating_income == Decimal("30500.00")

    def test_net_income(
        self,
        service: ConsolidationService,
        january_transactions: list[Transaction],
        parent_accounts: list[Account],
    ) -> None:
        """Net income = operating_income - other = 30500 - 8500 = 22000."""
        report = service.consolidate_pnl(
            transactions=january_transactions,
            accounts=parent_accounts,
        )
        # other: tax 7000 + interest_expense 1500 = 8500
        assert report.net_income == Decimal("22000.00")

    def test_revenue_items_sorted_by_code(
        self,
        service: ConsolidationService,
        january_transactions: list[Transaction],
        parent_accounts: list[Account],
    ) -> None:
        """Revenue line items are sorted by account code."""
        report = service.consolidate_pnl(
            transactions=january_transactions,
            accounts=parent_accounts,
        )
        codes = [item.account_code for item in report.revenue_items]
        assert codes == sorted(codes)

    def test_opex_items_sorted_by_code(
        self,
        service: ConsolidationService,
        january_transactions: list[Transaction],
        parent_accounts: list[Account],
    ) -> None:
        """Opex line items are sorted by account code."""
        report = service.consolidate_pnl(
            transactions=january_transactions,
            accounts=parent_accounts,
        )
        codes = [item.account_code for item in report.opex_items]
        assert codes == sorted(codes)

    def test_percentage_of_revenue_calculated(
        self,
        service: ConsolidationService,
        january_transactions: list[Transaction],
        parent_accounts: list[Account],
    ) -> None:
        """Each line item has a percentage_of_revenue relative to total revenue."""
        report = service.consolidate_pnl(
            transactions=january_transactions,
            accounts=parent_accounts,
        )
        total_rev = report.total_revenue  # 100500
        for item in report.revenue_items:
            expected_pct = (item.amount / total_rev * 100).quantize(Decimal("0.01"))
            assert item.percentage_of_revenue == expected_pct

    def test_cogs_percentage_of_revenue(
        self,
        service: ConsolidationService,
        january_transactions: list[Transaction],
        parent_accounts: list[Account],
    ) -> None:
        """COGS items also have a percentage relative to total revenue."""
        report = service.consolidate_pnl(
            transactions=january_transactions,
            accounts=parent_accounts,
        )
        cogs_item = report.cogs_items[0]
        # 20000 / 100500 * 100
        expected = (Decimal("20000") / Decimal("100500") * 100).quantize(Decimal("0.01"))
        assert cogs_item.percentage_of_revenue == expected

    def test_single_revenue_transaction(
        self,
        service: ConsolidationService,
        parent_accounts: list[Account],
    ) -> None:
        """A single revenue transaction produces a valid P&L."""
        txns = [make_transaction(ACCT_REVENUE_ID, "50000")]
        report = service.consolidate_pnl(
            transactions=txns, accounts=parent_accounts
        )
        assert report.total_revenue == Decimal("50000")
        assert report.gross_profit == Decimal("50000")
        assert report.net_income == Decimal("50000")

    def test_multiple_transactions_same_account_are_summed(
        self,
        service: ConsolidationService,
        parent_accounts: list[Account],
    ) -> None:
        """Two transactions for the same account are added together."""
        txns = [
            make_transaction(ACCT_REVENUE_ID, "30000"),
            make_transaction(ACCT_REVENUE_ID, "20000"),
        ]
        report = service.consolidate_pnl(
            transactions=txns, accounts=parent_accounts
        )
        assert report.total_revenue == Decimal("50000")
        assert len(report.revenue_items) == 1

    def test_balance_sheet_accounts_excluded_from_pnl(
        self,
        service: ConsolidationService,
    ) -> None:
        """Balance-sheet accounts (assets, liabilities) are skipped."""
        cash_id = uuid.uuid4()
        accounts = [
            Account(
                id=ACCT_REVENUE_ID,
                code="4000",
                name="Revenue",
                account_type=AccountType.REVENUE,
                category=AccountCategory.OPERATING_REVENUE,
                entity_id=PARENT_ENTITY_ID,
            ),
            Account(
                id=cash_id,
                code="1000",
                name="Cash",
                account_type=AccountType.ASSET,
                category=AccountCategory.CURRENT_ASSET,
                entity_id=PARENT_ENTITY_ID,
            ),
        ]
        txns = [
            make_transaction(ACCT_REVENUE_ID, "10000"),
            make_transaction(cash_id, "10000"),
        ]
        report = service.consolidate_pnl(transactions=txns, accounts=accounts)
        assert report.total_revenue == Decimal("10000")
        assert len(report.cogs_items) == 0
        assert len(report.opex_items) == 0
        assert len(report.other_items) == 0


# =============================================================================
# Error handling
# =============================================================================
class TestConsolidatePnlErrors:
    """Tests for error conditions in consolidate_pnl."""

    def test_empty_transactions_raises(
        self,
        service: ConsolidationService,
        parent_accounts: list[Account],
    ) -> None:
        with pytest.raises(InsufficientDataError, match="No transactions"):
            service.consolidate_pnl(transactions=[], accounts=parent_accounts)

    def test_unknown_account_raises(
        self,
        service: ConsolidationService,
        parent_accounts: list[Account],
    ) -> None:
        unknown_acct_id = uuid.uuid4()
        txns = [make_transaction(unknown_acct_id, "5000")]
        with pytest.raises(ConsolidationError, match="unknown account"):
            service.consolidate_pnl(transactions=txns, accounts=parent_accounts)


# =============================================================================
# Zero / edge-case revenue
# =============================================================================
class TestZeroRevenueEdgeCases:
    """Edge cases where total revenue is zero."""

    def test_zero_revenue_percentage_is_zero(
        self,
        service: ConsolidationService,
    ) -> None:
        """When there is no revenue, percentage_of_revenue should be 0."""
        accounts = [
            Account(
                id=ACCT_COGS_ID,
                code="5000",
                name="COGS",
                account_type=AccountType.EXPENSE,
                category=AccountCategory.COST_OF_GOODS_SOLD,
                entity_id=PARENT_ENTITY_ID,
            ),
        ]
        txns = [make_transaction(ACCT_COGS_ID, "5000")]
        report = service.consolidate_pnl(transactions=txns, accounts=accounts)

        assert report.total_revenue == Decimal("0.00")
        assert report.cogs_items[0].percentage_of_revenue == Decimal("0.00")


# =============================================================================
# consolidate_multi_entity
# =============================================================================
class TestConsolidateMultiEntity:
    """Tests for multi-entity (subsidiary) consolidation."""

    def test_combined_revenue(
        self,
        service: ConsolidationService,
        january_transactions: list[Transaction],
        eu_january_transactions: list[Transaction],
        all_accounts: list[Account],
    ) -> None:
        """Consolidated revenue = parent 100500 + EU 50000 = 150500."""
        all_txns = january_transactions + eu_january_transactions
        report = service.consolidate_multi_entity(
            transactions=all_txns,
            accounts=all_accounts,
            entity_ids=[PARENT_ENTITY_ID, SUB_EU_ENTITY_ID],
            entity_name="Acme Consolidated",
            period="2024-01",
        )
        assert report.entity_name == "Acme Consolidated"
        assert report.total_revenue == Decimal("150500.00")

    def test_combined_net_income(
        self,
        service: ConsolidationService,
        january_transactions: list[Transaction],
        eu_january_transactions: list[Transaction],
        all_accounts: list[Account],
    ) -> None:
        """Net income aggregates across both entities."""
        all_txns = january_transactions + eu_january_transactions
        report = service.consolidate_multi_entity(
            transactions=all_txns,
            accounts=all_accounts,
            entity_ids=[PARENT_ENTITY_ID, SUB_EU_ENTITY_ID],
        )
        # Parent net = 22000, EU net = 50000 - 10000 - 20000 = 20000
        assert report.net_income == Decimal("42000.00")

    def test_filters_to_specified_entities(
        self,
        service: ConsolidationService,
        january_transactions: list[Transaction],
        eu_january_transactions: list[Transaction],
        all_accounts: list[Account],
    ) -> None:
        """Only transactions for specified entity ids are included."""
        all_txns = january_transactions + eu_january_transactions
        # Only consolidate EU
        report = service.consolidate_multi_entity(
            transactions=all_txns,
            accounts=all_accounts,
            entity_ids=[SUB_EU_ENTITY_ID],
            entity_name="EU Only",
        )
        assert report.total_revenue == Decimal("50000.00")

    def test_no_matching_entities_raises(
        self,
        service: ConsolidationService,
        january_transactions: list[Transaction],
        all_accounts: list[Account],
    ) -> None:
        """Raises InsufficientDataError when no transactions match the entity ids."""
        unknown_entity = uuid.uuid4()
        with pytest.raises(InsufficientDataError, match="No transactions found"):
            service.consolidate_multi_entity(
                transactions=january_transactions,
                accounts=all_accounts,
                entity_ids=[unknown_entity],
            )


# =============================================================================
# aggregate_by_period
# =============================================================================
class TestAggregateByPeriod:
    """Tests for period-level (monthly) aggregation."""

    def test_two_months_produce_two_reports(
        self,
        service: ConsolidationService,
        january_transactions: list[Transaction],
        february_transactions: list[Transaction],
        parent_accounts: list[Account],
    ) -> None:
        all_txns = january_transactions + february_transactions
        reports = service.aggregate_by_period(
            transactions=all_txns,
            accounts=parent_accounts,
            entity_name="Acme Corp",
        )
        assert len(reports) == 2

    def test_reports_sorted_chronologically(
        self,
        service: ConsolidationService,
        january_transactions: list[Transaction],
        february_transactions: list[Transaction],
        parent_accounts: list[Account],
    ) -> None:
        # Provide February first to ensure sorting
        all_txns = february_transactions + january_transactions
        reports = service.aggregate_by_period(
            transactions=all_txns,
            accounts=parent_accounts,
        )
        assert reports[0].period == "2024-01"
        assert reports[1].period == "2024-02"

    def test_january_report_values(
        self,
        service: ConsolidationService,
        january_transactions: list[Transaction],
        february_transactions: list[Transaction],
        parent_accounts: list[Account],
    ) -> None:
        all_txns = january_transactions + february_transactions
        reports = service.aggregate_by_period(
            transactions=all_txns,
            accounts=parent_accounts,
        )
        jan = reports[0]
        assert jan.period == "2024-01"
        assert jan.total_revenue == Decimal("100500.00")
        assert jan.net_income == Decimal("22000.00")

    def test_february_report_values(
        self,
        service: ConsolidationService,
        january_transactions: list[Transaction],
        february_transactions: list[Transaction],
        parent_accounts: list[Account],
    ) -> None:
        all_txns = january_transactions + february_transactions
        reports = service.aggregate_by_period(
            transactions=all_txns,
            accounts=parent_accounts,
        )
        feb = reports[1]
        assert feb.period == "2024-02"
        # Feb revenue = 110000 only (no other income)
        assert feb.total_revenue == Decimal("110000.00")
        # Feb net = 110000 - 22000 - 51000 = 37000 (no other items)
        assert feb.net_income == Decimal("37000.00")

    def test_single_month_produces_one_report(
        self,
        service: ConsolidationService,
        january_transactions: list[Transaction],
        parent_accounts: list[Account],
    ) -> None:
        reports = service.aggregate_by_period(
            transactions=january_transactions,
            accounts=parent_accounts,
        )
        assert len(reports) == 1
        assert reports[0].period == "2024-01"

    def test_empty_transactions_raises(
        self,
        service: ConsolidationService,
        parent_accounts: list[Account],
    ) -> None:
        with pytest.raises(InsufficientDataError, match="No transactions"):
            service.aggregate_by_period(
                transactions=[],
                accounts=parent_accounts,
            )

    def test_entity_name_propagated(
        self,
        service: ConsolidationService,
        january_transactions: list[Transaction],
        parent_accounts: list[Account],
    ) -> None:
        reports = service.aggregate_by_period(
            transactions=january_transactions,
            accounts=parent_accounts,
            entity_name="Acme Corp",
        )
        assert all(r.entity_name == "Acme Corp" for r in reports)

    def test_currency_propagated(
        self,
        service: ConsolidationService,
        january_transactions: list[Transaction],
        parent_accounts: list[Account],
    ) -> None:
        reports = service.aggregate_by_period(
            transactions=january_transactions,
            accounts=parent_accounts,
            currency="EUR",
        )
        assert all(r.currency == "EUR" for r in reports)
