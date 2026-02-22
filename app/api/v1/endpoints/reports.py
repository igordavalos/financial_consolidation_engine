"""Reports endpoints."""

from fastapi import APIRouter, status

from decimal import Decimal

from app.api.v1.schemas.report_schemas import PnLDemoRequest, PnLReportResponse
from app.demo.sample_data import (
    create_sample_accounts,
    create_sample_company,
    create_sample_transactions,
)
from app.domain.services.consolidation_service import ConsolidationService

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post(
    "/pnl/demo",
    response_model=PnLReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate demo P&L report",
    description="Generate a P&L report using sample data (no database required)",
)
async def generate_demo_pnl(request: PnLDemoRequest | None = None) -> PnLReportResponse:
    """
    Generate a demo P&L report using fixtures.
    
    This endpoint demonstrates the consolidation engine without requiring a database.
    It uses the same fixtures from the test suite.
    
    Args:
        request: Optional request parameters (period, company_name)
    
    Returns:
        PnLReportResponse: The generated P&L report
    """
    # Create sample data using test fixtures
    company = create_sample_company()
    accounts = create_sample_accounts()
    transactions = create_sample_transactions()
    
    # Override company name if provided
    if request and request.company_name:
        company.name = request.company_name
    
    # Use the consolidation service
    service = ConsolidationService()
    
    # Determine period: use request if provided, otherwise default to
    # the period of the first sample transaction (keeps demo data in sync)
    period = None
    if request and request.period:
        period = request.period
    else:
        period = transactions[0].period_key if transactions else ""

    # Filter transactions for the requested period (use period_key on Transaction)
    period_transactions = [t for t in transactions if t.period_key == period]

    # If no transactions found for the requested period, return an empty report
    # with zeroed numeric fields (useful for demo/testing scenarios).
    if not period_transactions:
        return PnLReportResponse(
            company_id=company.id,
            company_name=company.name,
            period=period,
            revenue=Decimal("0.00"),
            cogs=Decimal("0.00"),
            gross_profit=Decimal("0.00"),
            gross_margin=Decimal("0.00"),
            operating_expenses=Decimal("0.00"),
            operating_income=Decimal("0.00"),
            operating_margin=Decimal("0.00"),
            other_items=Decimal("0.00"),
            net_income=Decimal("0.00"),
            net_margin=Decimal("0.00"),
            line_items=[],
        )
    
    # Generate the report
    report = service.consolidate_pnl(
        transactions=period_transactions,
        accounts=accounts,
        entity_name=company.name,
        period=period,
        currency=company.base_currency,
    )
    
    # Convert to Pydantic model for response
    zero = Decimal("0.00")
    total_revenue = report.total_revenue
    cogs_sum = sum((i.amount for i in report.cogs_items), zero)
    opex_sum = sum((i.amount for i in report.opex_items), zero)
    other_sum = sum((i.amount for i in report.other_items), zero)

    if total_revenue != 0:
        gross_margin = (report.gross_profit / total_revenue * Decimal("100")).quantize(Decimal("0.01"))
        operating_margin = (report.operating_income / total_revenue * Decimal("100")).quantize(Decimal("0.01"))
        net_margin = (report.net_income / total_revenue * Decimal("100")).quantize(Decimal("0.01"))
    else:
        gross_margin = zero
        operating_margin = zero
        net_margin = zero

    return PnLReportResponse(
        company_id=company.id,
        company_name=report.entity_name,
        period=report.period,
        revenue=total_revenue,
        cogs=cogs_sum,
        gross_profit=report.gross_profit,
        gross_margin=gross_margin,
        operating_expenses=opex_sum,
        operating_income=report.operating_income,
        operating_margin=operating_margin,
        other_items=other_sum,
        net_income=report.net_income,
        net_margin=net_margin,
        line_items=[
            {
                "account_id": item.account_id,
                "account_code": item.account_code,
                "account_name": item.account_name,
                "amount": item.amount,
                "percent_of_revenue": item.percentage_of_revenue,
            }
            for item in (report.revenue_items + report.cogs_items + report.opex_items + report.other_items)
        ],
    )
