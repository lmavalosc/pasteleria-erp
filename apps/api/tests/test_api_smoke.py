from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
TENANT_ID = "00000000-0000-0000-0000-000000000001"
HEADERS = {"X-Tenant-ID": TENANT_ID}


def test_smoke_health():
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_smoke_tenant_context():
    res = client.get("/api/v1/debug/tenant-context", headers=HEADERS)
    assert res.status_code == 200
    assert res.json()["tenant_id"] == TENANT_ID


def test_smoke_openapi_json():
    res = client.get("/api/v1/openapi.json")
    assert res.status_code == 200
    assert "paths" in res.json()
