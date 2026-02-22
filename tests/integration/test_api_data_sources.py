from fastapi.testclient import TestClient
import io

from app.main import app

client = TestClient(app)


def test_csv_import_endpoint_valid():
    csv_content = "date,account_id,amount\n2026-01-31,4000,100.00\n2026-01-31,5000,50.00\n"
    files = {"file": ("test.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    resp = client.post("/api/v1/data-sources/csv/import", files=files)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success_count"] == 2
    assert data["error_count"] == 0


def test_csv_import_endpoint_per_row_errors():
    csv_content = "date,account_id,amount\nbad-date,4000,100.00\n2026-01-31,,50.00\n"
    files = {"file": ("test.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    resp = client.post("/api/v1/data-sources/csv/import", files=files)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success_count"] == 0
    assert data["error_count"] == 2
