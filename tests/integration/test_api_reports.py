"""Integration tests for reports endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestPnLDemoEndpoint:
    """Tests for the demo P&L report endpoint."""

    def test_generate_demo_pnl_default(self):
        """Test generating demo P&L with default parameters."""
        response = client.post("/api/v1/reports/pnl/demo")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "company_id" in data
        assert "company_name" in data
        assert "period" in data
        assert "revenue" in data
        assert "cogs" in data
        assert "gross_profit" in data
        assert "gross_margin" in data
        assert "operating_expenses" in data
        assert "operating_income" in data
        assert "operating_margin" in data
        assert "other_items" in data
        assert "net_income" in data
        assert "net_margin" in data
        assert "line_items" in data
        
        # Check that we have line items
        assert len(data["line_items"]) > 0
        
        # Check line item structure
        line_item = data["line_items"][0]
        assert "account_id" in line_item
        assert "account_code" in line_item
        assert "account_name" in line_item
        assert "amount" in line_item

    def test_generate_demo_pnl_with_custom_period(self):
        """Test generating demo P&L with custom period."""
        response = client.post(
            "/api/v1/reports/pnl/demo",
            json={"period": "2024-01"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["period"] == "2024-01"

    def test_generate_demo_pnl_with_custom_company_name(self):
        """Test generating demo P&L with custom company name."""
        custom_name = "Test Corporation"
        response = client.post(
            "/api/v1/reports/pnl/demo",
            json={"company_name": custom_name}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["company_name"] == custom_name

    def test_generate_demo_pnl_financial_calculations(self):
        """Test that financial calculations are correct."""
        response = client.post("/api/v1/reports/pnl/demo")
        
        assert response.status_code == 200
        data = response.json()
        
        # Convert strings to floats for calculation
        revenue = float(data["revenue"])
        cogs = float(data["cogs"])
        gross_profit = float(data["gross_profit"])
        operating_expenses = float(data["operating_expenses"])
        operating_income = float(data["operating_income"])
        other_items = float(data["other_items"])
        net_income = float(data["net_income"])
        
        # Check calculations
        assert abs(gross_profit - (revenue - cogs)) < 0.01
        assert abs(operating_income - (gross_profit - operating_expenses)) < 0.01
        assert abs(net_income - (operating_income - other_items)) < 0.01
        
        # Check margins
        if revenue > 0:
            gross_margin = float(data["gross_margin"])
            expected_gross_margin = (gross_profit / revenue) * 100
            assert abs(gross_margin - expected_gross_margin) < 0.01

    def test_generate_demo_pnl_empty_request_body(self):
        """Test generating demo P&L with empty request body."""
        response = client.post("/api/v1/reports/pnl/demo", json={})
        
        assert response.status_code == 200
        data = response.json()
        assert "revenue" in data
