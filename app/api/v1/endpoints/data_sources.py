"""Data sources endpoints (basic implementations)."""

from fastapi import APIRouter, UploadFile, File
import io
import csv
from typing import Any

from app.infrastructure.connectors import CsvConnector
from app.infrastructure.database import AsyncSessionLocal
from app.infrastructure.models import Account
from app.infrastructure.repositories.transaction_repository import TransactionRepository
from sqlalchemy import select

# Avoid calling File(...) in a function default (ruff B008) by creating
# a module-level parameter that can be reused in endpoint signatures.
FILE_PARAM = File(...)

router = APIRouter(prefix="/data-sources", tags=["data-sources"])


@router.post("/csv/import", summary="Import transactions from CSV")
async def import_csv(file: UploadFile = FILE_PARAM) -> dict[str, Any]:
    """Accept a CSV file upload and parse it using the CsvConnector.

    Returns a summary with counts of successes and errors and the first
    few error messages for debugging.
    """
    # Read uploaded file into text
    contents = await file.read()
    text = contents.decode("utf-8")

    # Use csv.DictReader to create row mappings
    fh = io.StringIO(text)
    reader = csv.DictReader(fh)
    rows = list(reader)

    connector = CsvConnector()
    successes, errors = connector.import_rows(rows)

    # Persist parsed rows to the database: match account by `code` (CSV uses account code)
    persisted = 0
    persist_errors: list[dict] = []

    async with AsyncSessionLocal() as session:
        for idx, row in enumerate(successes, start=1):
            try:
                code = str(row["account_id"]).strip()
                q = select(Account).filter_by(code=code)
                res = await session.execute(q)
                account = res.scalars().first()
                if not account:
                    persist_errors.append({"row": idx, "error": f"account code not found: {code}", "raw": row.get("raw")})
                    continue

                repo = TransactionRepository(session)
                tx_payload = {
                    "account_id": account.id,
                    "date": row["date"],
                    "amount": row["amount"],
                    "description": None,
                }
                await repo.create(tx_payload)
                persisted += 1
            except Exception as exc:
                persist_errors.append({"row": idx, "error": str(exc), "raw": row.get("raw")})

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        # Backwards-compatible keys expected by tests
        "success_count": len(successes),
        "error_count": len(errors),
        # New, more explicit keys
        "parsed_count": len(successes),
        "parsed_error_count": len(errors),
        "parsed_errors": errors[:10],
        "persisted_count": persisted,
        "persist_errors": persist_errors[:10],
    }
