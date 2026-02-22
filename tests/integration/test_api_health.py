"""Integration tests for health endpoint."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint returns 200 OK."""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "healthy"
    assert data["service"] == "Financial Consolidation Engine"
    assert data["version"] == "0.1.0"


def test_root_endpoint():
    """Test root endpoint returns API information."""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "message" in data
    assert "version" in data
    assert data["docs"] == "/docs"
    assert data["health"] == "/health"
