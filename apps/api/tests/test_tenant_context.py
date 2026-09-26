import os
import sys

# Asegurar que apps/api esté en el path de Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

TENANT_1 = "00000000-0000-0000-0000-000000000001"
TENANT_2 = "00000000-0000-0000-0000-000000000002"


def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_debug_tenant_context():
    response = client.get(
        "/api/v1/debug/tenant-context",
        headers={"X-Tenant-ID": TENANT_1},
    )
    assert response.status_code == 200
    assert response.json()["tenant_id"] == TENANT_1


def test_debug_tenant_context_missing_header():
    response = client.get("/api/v1/debug/tenant-context")
    assert response.status_code == 400
    assert "Falta header X-Tenant-ID" in response.json()["detail"]


def test_accounts_tenant_1():
    response = client.get(
        "/api/v1/debug/accounts",
        headers={"X-Tenant-ID": TENANT_1},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["tenant_id"] == TENANT_1
    assert data["total_accounts"] == 6
    codes = [acc["code"] for acc in data["accounts"]]
    assert "1110101" in codes
    assert "5110101" in codes


def test_accounts_tenant_2():
    response = client.get(
        "/api/v1/debug/accounts",
        headers={"X-Tenant-ID": TENANT_2},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["tenant_id"] == TENANT_2
    assert data["total_accounts"] == 1
    assert data["accounts"][0]["code"] == "1110101"


def test_missing_header():
    response = client.get("/api/v1/debug/accounts")
    assert response.status_code == 400
    assert "X-Tenant-ID" in response.json()["detail"]


def test_invalid_uuid_header():
    response = client.get(
        "/api/v1/debug/accounts",
        headers={"X-Tenant-ID": "invalid-uuid"},
    )
    assert response.status_code == 400
    assert "UUID válido" in response.json()["detail"]


if __name__ == "__main__":
    test_health_check()
    test_debug_tenant_context()
    test_debug_tenant_context_missing_header()
    test_accounts_tenant_1()
    test_accounts_tenant_2()
    test_missing_header()
    test_invalid_uuid_header()
    print("[SUCCESS] Todas las pruebas de inyección de tenant en FastAPI pasaron exitosamente.")
