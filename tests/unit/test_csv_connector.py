import csv
from pathlib import Path
from datetime import date

import pytest

from app.infrastructure.connectors.csv_connector import CsvConnector


def write_csv(path, headers, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=headers)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def test_csv_connector_valid(tmp_path: Path):
    path = tmp_path / "data.csv"
    rows = [
        {"date": "2026-02-01", "account_id": "4000", "amount": "100.50"},
        {"date": "2026-02-02T00:00:00", "account_id": "6000", "amount": "200"},
    ]
    write_csv(path, ["date", "account_id", "amount"], rows)

    c = CsvConnector()
    successes, errors = c.import_file(str(path))
    assert len(successes) == 2
    assert all(isinstance(s["date"], date) for s in successes)
    assert errors == []


def test_csv_connector_missing_column(tmp_path: Path):
    path = tmp_path / "data.csv"
    rows = [{"date": "2026-02-01", "amount": "100.5"}]
    write_csv(path, ["date", "amount"], rows)
    c = CsvConnector()
    with pytest.raises(ValueError):
        c.import_file(str(path))


def test_csv_connector_per_row_errors(tmp_path: Path):
    path = tmp_path / "data.csv"
    rows = [
        {"date": "bad-date", "account_id": "4000", "amount": "100.50"},
        {"date": "2026-02-02", "account_id": "", "amount": "200"},
        {"date": "2026-02-03", "account_id": "7000", "amount": "x"},
        {"date": "2026-02-04", "account_id": "8000", "amount": "50"},
    ]
    write_csv(path, ["date", "account_id", "amount"], rows)
    c = CsvConnector()
    successes, errors = c.import_file(str(path))
    # only last row is valid
    assert len(successes) == 1
    assert len(errors) == 3
