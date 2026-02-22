"""Pydantic schemas for Account models."""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.models.account import AccountCategory, AccountType


class AccountBase(BaseModel):
    """Base schema for Account."""

    code: str = Field(..., description="Account code (e.g., '4000', 'REV-001')")
    name: str = Field(..., description="Account name (e.g., 'Product Revenue')")
    category: AccountCategory = Field(..., description="Account category")
    account_type: AccountType = Field(..., description="Account type (debit/credit)")
    description: str | None = Field(None, description="Optional description")


class AccountCreate(AccountBase):
    """Schema for creating a new Account."""

    pass


class AccountUpdate(BaseModel):
    """Schema for updating an Account."""

    code: str | None = None
    name: str | None = None
    category: AccountCategory | None = None
    account_type: AccountType | None = None
    description: str | None = None


class AccountResponse(AccountBase):
    """Schema for Account response."""

    id: UUID = Field(..., description="Account unique identifier")

    model_config = ConfigDict(from_attributes=True)


class AccountListResponse(BaseModel):
    """Schema for list of accounts response."""

    accounts: list[AccountResponse]
    total: int
