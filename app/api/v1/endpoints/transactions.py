"""Transactions endpoints implemented against the database."""

import uuid
from datetime import date
from fastapi import APIRouter, HTTPException, status

from app.api.v1.schemas import (
    TransactionCreate,
    TransactionListResponse,
    TransactionResponse,
    TransactionUpdate,
)
from app.api.constants import INVALID_ID
from app.infrastructure.database import AsyncSessionLocal
from app.infrastructure.repositories.transaction_repository import TransactionRepository
from app.infrastructure.repositories.account_repository import AccountRepository

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.get("", response_model=TransactionListResponse, summary="List all transactions")
async def list_transactions() -> TransactionListResponse:
    """List transactions from the database."""
    async with AsyncSessionLocal() as session:
        repo = TransactionRepository(session)
        items = await repo.list()
        transactions = []
        for t in items:
            tid = getattr(t, "id")
            transactions.append(
                TransactionResponse(
                    id=uuid.UUID(int=int(tid)),
                    account_id=uuid.UUID(int=int(getattr(t, "account_id"))),
                    subsidiary_id=None,
                    amount=getattr(t, "amount"),
                    transaction_date=getattr(t, "date"),
                    description=getattr(t, "description"),
                    period=getattr(t, "date").strftime("%Y-%m"),
                )
            )
        return TransactionListResponse(transactions=transactions, total=len(transactions))

@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED, summary="Create a new transaction")
async def create_transaction(transaction: TransactionCreate) -> TransactionResponse:
    """Create a transaction in the database."""
    # Convert incoming UUID account_id to integer id used by DB
    int_account_id = transaction.account_id.int
    async with AsyncSessionLocal() as session:
        # validate account exists
        acc_repo = AccountRepository(session)
        acc = await acc_repo.get(int_account_id)
        if not acc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
        repo = TransactionRepository(session)
        data = transaction.model_dump()
        # map field names
        data_db = {
            "account_id": int_account_id,
            "date": data["transaction_date"],
            "amount": data["amount"],
            "description": data.get("description"),
        }
        db_obj = await repo.create(data_db)
        return TransactionResponse(
            id=uuid.UUID(int=int(getattr(db_obj, "id"))),
            account_id=uuid.UUID(int=int(getattr(db_obj, "account_id"))),
            subsidiary_id=None,
            amount=getattr(db_obj, "amount"),
            transaction_date=getattr(db_obj, "date"),
            description=getattr(db_obj, "description"),
            period=getattr(db_obj, "date").strftime("%Y-%m"),
        )

@router.get("/{transaction_id}", response_model=TransactionResponse, summary="Get transaction by ID")
async def get_transaction(transaction_id: str) -> TransactionResponse:
    """Retrieve a single transaction by ID."""
    try:
        uid = uuid.UUID(transaction_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=INVALID_ID)
    int_id = uid.int
    async with AsyncSessionLocal() as session:
        repo = TransactionRepository(session)
        db_obj = await repo.get(int_id)
        if not db_obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        did = getattr(db_obj, "id")
        return TransactionResponse(
            id=uuid.UUID(int=int(did)),
            account_id=uuid.UUID(int=int(getattr(db_obj, "account_id"))),
            subsidiary_id=None,
            amount=getattr(db_obj, "amount"),
            transaction_date=getattr(db_obj, "date"),
            description=getattr(db_obj, "description"),
            period=getattr(db_obj, "date").strftime("%Y-%m"),
        )

@router.put("/{transaction_id}", response_model=TransactionResponse, summary="Update a transaction")
async def update_transaction(transaction_id: str, transaction: TransactionUpdate) -> TransactionResponse:
    """Update a transaction."""
    try:
        uid = uuid.UUID(transaction_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=INVALID_ID)
    int_id = uid.int
    async with AsyncSessionLocal() as session:
        repo = TransactionRepository(session)
        db_obj = await repo.get(int_id)
        if not db_obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        update_data = transaction.model_dump(exclude_none=True)
        if "transaction_date" in update_data:
            update_data["date"] = update_data.pop("transaction_date")
        updated = await repo.update(db_obj, update_data)
        uid_up = getattr(updated, "id")
        return TransactionResponse(
            id=uuid.UUID(int=int(uid_up)),
            account_id=uuid.UUID(int=int(getattr(updated, "account_id"))),
            subsidiary_id=None,
            amount=getattr(updated, "amount"),
            transaction_date=getattr(updated, "date"),
            description=getattr(updated, "description"),
            period=getattr(updated, "date").strftime("%Y-%m"),
        )

@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a transaction")
async def delete_transaction(transaction_id: str) -> None:
    """Delete a transaction by ID."""
    try:
        uid = uuid.UUID(transaction_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=INVALID_ID)
    int_id = uid.int
    async with AsyncSessionLocal() as session:
        repo = TransactionRepository(session)
        obj = await repo.delete(int_id)
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return None
