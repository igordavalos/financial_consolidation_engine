from __future__ import annotations

import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import List, Dict, Any, Tuple, Iterable, Mapping

from .base_connector import BaseConnector


class CsvConnector(BaseConnector):
    """Simple CSV connector that validates required columns and parses rows.

    Behavior:
    - Requires columns: `date`, `account_id`, `amount`.
    - Parses `date` as ISO date (YYYY-MM-DD or full ISO datetime).
    - Parses `amount` to float.
    - Returns a tuple: (successes, errors) where successes is a list of
      normalized dicts and errors is a list of per-row error dicts.
    """

    REQUIRED_COLUMNS = ("date", "account_id", "amount")

    def import_file(self, path: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Open and parse a CSV file at `path`.

        Returns (successes, errors).
        """
        with open(path, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            fieldnames = [c.strip() for c in (reader.fieldnames or [])]
            for col in self.REQUIRED_COLUMNS:
                if col not in fieldnames:
                    raise ValueError(f"Missing required column: {col}")

            successes: List[Dict[str, Any]] = []
            errors: List[Dict[str, Any]] = []

            for row_index, raw_row in enumerate(reader, start=2):
                # row_index starts at 2 to correspond to text editor line (header=1)
                try:
                    # Normalize and validate fields
                    raw_date = raw_row.get("date", "").strip()
                    if not raw_date:
                        raise ValueError("date is empty")
                    # Accept ISO date or datetime
                    parsed_dt = datetime.fromisoformat(raw_date)
                    date_val = parsed_dt.date()

                    account_id = raw_row.get("account_id", "").strip()
                    if not account_id:
                        raise ValueError("account_id is empty")

                    amount_raw = raw_row.get("amount", "").strip()
                    if not amount_raw:
                        raise ValueError("amount is empty")
                    try:
                        amount_val = Decimal(amount_raw)
                    except InvalidOperation:
                        raise ValueError(f"invalid amount: {amount_raw}")

                    successes.append({
                        "date": date_val,
                        "account_id": account_id,
                        "amount": amount_val,
                        "raw": raw_row,
                    })
                except Exception as exc:  # per-row error handling
                    errors.append({"row": row_index, "error": str(exc), "raw": raw_row})

            return successes, errors

    # For compatibility with BaseConnector
    def import_rows(self, rows: Iterable[Mapping[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        # Accept an iterable of mappings; validate each similarly to import_file
        successes: List[Dict[str, Any]] = []
        errors: List[Dict[str, Any]] = []
        for idx, raw_row in enumerate(rows, start=1):
            try:
                raw_date = raw_row.get("date", "").strip()
                if not raw_date:
                    raise ValueError("date is empty")
                parsed_dt = datetime.fromisoformat(raw_date)
                date_val = parsed_dt.date()

                account_id = raw_row.get("account_id", "").strip()
                if not account_id:
                    raise ValueError("account_id is empty")

                try:
                    amount_val = Decimal(str(raw_row.get("amount", "")).strip())
                except InvalidOperation:
                    raise ValueError(f"invalid amount: {raw_row.get('amount')}")

                successes.append({"date": date_val, "account_id": account_id, "amount": amount_val, "raw": raw_row})
            except Exception as exc:
                errors.append({"row": idx, "error": str(exc), "raw": raw_row})
        return successes, errors
