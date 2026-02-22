"""Pydantic schemas for Report models."""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PnLLineItemResponse(BaseModel):
    """Schema for P&L line item response."""

    account_id: UUID
    account_code: str
    account_name: str
    amount: Decimal
    percent_of_revenue: Decimal | None = None

    model_config = ConfigDict(from_attributes=True)


class PnLReportResponse(BaseModel):
    """Schema for P&L report response."""

    company_id: UUID
    company_name: str
    period: str
    revenue: Decimal
    cogs: Decimal
    gross_profit: Decimal
    gross_margin: Decimal
    operating_expenses: Decimal
    operating_income: Decimal
    operating_margin: Decimal
    other_items: Decimal
    net_income: Decimal
    net_margin: Decimal
    line_items: list[PnLLineItemResponse]

    model_config = ConfigDict(from_attributes=True)


class PnLDemoRequest(BaseModel):
    """Schema for demo P&L request (optional parameters)."""

    period: str | None = Field(None, description="Period to generate report for (YYYY-MM)")
    company_name: str | None = Field(None, description="Company name for demo data")


class VarianceLineItemResponse(BaseModel):
    """Schema for variance line item response."""

    account_id: UUID
    account_code: str
    account_name: str
    budget: Decimal
    actual: Decimal
    variance: Decimal
    variance_percent: Decimal
    is_favorable: bool

    model_config = ConfigDict(from_attributes=True)


class VarianceReportResponse(BaseModel):
    """Schema for variance report response."""

    company_id: UUID
    company_name: str
    period: str
    total_budget: Decimal
    total_actual: Decimal
    total_variance: Decimal
    total_variance_percent: Decimal
    line_items: list[VarianceLineItemResponse]

    model_config = ConfigDict(from_attributes=True)
