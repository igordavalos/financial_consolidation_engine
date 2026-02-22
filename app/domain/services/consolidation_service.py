# filepath: c:\Personal\financial_consolidation_engine\app\domain\services\consolidation_service.py
"""Consolidation service — transforms raw transactions into P&L reports.

This is the core engine of the project: it aggregates financial transactions
by account, computes subtotals (revenue, COGS, opex, other), and produces
a structured Profit & Loss report.  It also supports multi-entity
consolidation (parent + subsidiaries) and period-level aggregation.
"""

from __future__ import annotations

import uuid
from collections import defaultdict
from decimal import Decimal

from app.domain.exceptions import ConsolidationError, InsufficientDataError
from app.domain.models.account import Account, AccountCategory
from app.domain.models.report import PnLLineItem, PnLReport
from app.domain.models.transaction import Transaction

# Categories that map to each P&L section
_REVENUE_CATEGORIES = frozenset(
    {AccountCategory.OPERATING_REVENUE, AccountCategory.OTHER_INCOME}
)
_COGS_CATEGORIES = frozenset({AccountCategory.COST_OF_GOODS_SOLD})
_OPEX_CATEGORIES = frozenset({AccountCategory.OPERATING_EXPENSE})
_OTHER_CATEGORIES = frozenset(
    {AccountCategory.OTHER_EXPENSE, AccountCategory.TAX}
)


class ConsolidationService:
    """Transforms transactions + chart-of-accounts into P&L reports."""

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def consolidate_pnl(
        self,
        transactions: list[Transaction],
        accounts: list[Account],
        entity_name: str = "",
        period: str = "",
        currency: str = "USD",
    ) -> PnLReport:
        """Build a single-entity P&L report from transactions and accounts.

        Args:
            transactions: financial transactions to aggregate.
            accounts: the chart-of-accounts used to classify each transaction.
            entity_name: name shown on the report header.
            period: human-readable period label (e.g. "2024-Q1").
            currency: ISO currency code for the report.

        Returns:
            A fully populated ``PnLReport``.

        Raises:
            ConsolidationError: if a transaction references an unknown account.
            InsufficientDataError: if no transactions are provided.
        """
        if not transactions:
            raise InsufficientDataError("No transactions provided for consolidation")

        account_map = {a.id: a for a in accounts}
        self._validate_transactions(transactions, account_map)

        # Aggregate amounts by account id
        totals_by_account: dict[uuid.UUID, Decimal] = defaultdict(lambda: Decimal("0.00"))
        for txn in transactions:
            totals_by_account[txn.account_id] += txn.amount

        # Classify line items into P&L sections
        revenue_items: list[PnLLineItem] = []
        cogs_items: list[PnLLineItem] = []
        opex_items: list[PnLLineItem] = []
        other_items: list[PnLLineItem] = []

        # Pre-compute total revenue for percentage calculation
        total_revenue = Decimal("0.00")
        for acct_id, amount in totals_by_account.items():
            acct = account_map[acct_id]
            if acct.category in _REVENUE_CATEGORIES:
                total_revenue += amount

        for acct_id, amount in totals_by_account.items():
            acct = account_map[acct_id]
            pct = (
                (amount / total_revenue * 100).quantize(Decimal("0.01"))
                if total_revenue != 0
                else Decimal("0.00")
            )
            item = PnLLineItem(
                account_id=acct.id,
                account_code=acct.code,
                account_name=acct.name,
                category=str(acct.category),
                amount=amount,
                percentage_of_revenue=pct,
            )
            if acct.category in _REVENUE_CATEGORIES:
                revenue_items.append(item)
            elif acct.category in _COGS_CATEGORIES:
                cogs_items.append(item)
            elif acct.category in _OPEX_CATEGORIES:
                opex_items.append(item)
            elif acct.category in _OTHER_CATEGORIES:
                other_items.append(item)
            # Balance-sheet categories are silently skipped in a P&L report

        return PnLReport(
            entity_name=entity_name,
            period=period,
            currency=currency,
            revenue_items=sorted(revenue_items, key=lambda i: i.account_code),
            cogs_items=sorted(cogs_items, key=lambda i: i.account_code),
            opex_items=sorted(opex_items, key=lambda i: i.account_code),
            other_items=sorted(other_items, key=lambda i: i.account_code),
        )

    def consolidate_multi_entity(
        self,
        transactions: list[Transaction],
        accounts: list[Account],
        entity_ids: list[uuid.UUID],
        entity_name: str = "Consolidated",
        period: str = "",
        currency: str = "USD",
    ) -> PnLReport:
        """Consolidate P&L across multiple entities (parent + subsidiaries).

        Filters transactions to only those belonging to the given entity ids,
        then produces a single consolidated report.

        Args:
            transactions: all available transactions.
            accounts: the chart-of-accounts for the relevant entities.
            entity_ids: entity UUIDs to include in consolidation.
            entity_name: label for the consolidated report.
            period: human-readable period label.
            currency: ISO currency code.

        Returns:
            A consolidated ``PnLReport``.

        Raises:
            InsufficientDataError: if no matching transactions are found.
        """
        entity_id_set = set(entity_ids)
        filtered_txns = [t for t in transactions if t.entity_id in entity_id_set]

        if not filtered_txns:
            raise InsufficientDataError(
                "No transactions found for the specified entities"
            )

        # Collect only accounts that belong to those entities
        filtered_accounts = [a for a in accounts if a.entity_id in entity_id_set]

        return self.consolidate_pnl(
            transactions=filtered_txns,
            accounts=filtered_accounts,
            entity_name=entity_name,
            period=period,
            currency=currency,
        )

    def aggregate_by_period(
        self,
        transactions: list[Transaction],
        accounts: list[Account],
        entity_name: str = "",
        currency: str = "USD",
    ) -> list[PnLReport]:
        """Produce one P&L report per calendar month found in the data.

        Args:
            transactions: financial transactions to aggregate.
            accounts: the chart-of-accounts.
            entity_name: name shown on each report header.
            currency: ISO currency code.

        Returns:
            A list of ``PnLReport`` objects, one per month, sorted
            chronologically.

        Raises:
            InsufficientDataError: if no transactions are provided.
        """
        if not transactions:
            raise InsufficientDataError("No transactions provided for aggregation")

        # Group transactions by period_key
        by_period: dict[str, list[Transaction]] = defaultdict(list)
        for txn in transactions:
            by_period[txn.period_key].append(txn)

        reports: list[PnLReport] = []
        for period_key in sorted(by_period):
            report = self.consolidate_pnl(
                transactions=by_period[period_key],
                accounts=accounts,
                entity_name=entity_name,
                period=period_key,
                currency=currency,
            )
            reports.append(report)

        return reports

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_transactions(
        transactions: list[Transaction],
        account_map: dict[uuid.UUID, Account],
    ) -> None:
        """Ensure every transaction references a known account."""
        for txn in transactions:
            if txn.account_id not in account_map:
                raise ConsolidationError(
                    f"Transaction {txn.id} references unknown account {txn.account_id}"
                )
