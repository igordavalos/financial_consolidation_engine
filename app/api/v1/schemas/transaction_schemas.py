"""Pydantic schemas for Transaction models."""

from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TransactionBase(BaseModel):
    """Base schema for Transaction."""

    account_id: UUID = Field(..., description="Account reference")
    subsidiary_id: UUID | None = Field(None, description="Subsidiary reference (optional)")
    amount: Decimal = Field(..., description="Transaction amount")
    transaction_date: date = Field(..., description="Transaction date")
    description: str | None = Field(None, description="Transaction description")


class TransactionCreate(TransactionBase):
    """Schema for creating a new Transaction."""

    pass


class TransactionUpdate(BaseModel):
    """Schema for updating a Transaction."""

    account_id: UUID | None = None
    subsidiary_id: UUID | None = None
    amount: Decimal | None = None
    transaction_date: date | None = None
    description: str | None = None


class TransactionResponse(TransactionBase):
    """Schema for Transaction response."""

    id: UUID = Field(..., description="Transaction unique identifier")
    period: str = Field(..., description="Auto-detected period (YYYY-MM)")

    model_config = ConfigDict(from_attributes=True)


class TransactionListResponse(BaseModel):
    """Schema for list of transactions response."""

    transactions: list[TransactionResponse]
    total: int
