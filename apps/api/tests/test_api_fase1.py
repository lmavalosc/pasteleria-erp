import io
import os
import sys

# Asegurar que apps/api esté en el path de Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
TENANT_ID = "00000000-0000-0000-0000-000000000001"
HEADERS = {"X-Tenant-ID": TENANT_ID}


def test_health():
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_missing_tenant_header():
    res = client.get("/api/v1/debug/tenant-context")
    assert res.status_code == 401
    assert "Se requiere autenticación" in res.json()["detail"]


def test_validation_error_rfc7807():
    # Enviar payload inválido para probar el formato ProblemDetail
    res = client.post("/api/v1/expenses", json={"amount": -100}, headers=HEADERS)
    assert res.status_code == 422
    body = res.json()
    assert body["title"] in ("Solicitud inválida", "Error de validación en la solicitud")
    assert "invalid_params" in body or "errors" in body


def test_upload_document_flow():
    fake_file = io.BytesIO(b"%PDF-1.4 Fake receipt file content")
    res = client.post(
        "/api/v1/documents/upload",
        files={"file": ("boleta.pdf", fake_file, "application/pdf")},
        headers=HEADERS,
    )
    assert res.status_code == 201
    data = res.json()
    assert data["filename"] == "boleta.pdf"
    assert data["checksum_sha256"] is not None
    assert data["storage_provider"] == "local"


def test_list_and_create_accounting_accounts():
    res = client.get("/api/v1/accounting/accounts", headers=HEADERS)
    assert res.status_code == 200
    data = res.json()
    accounts = data["items"] if isinstance(data, dict) and "items" in data else data
    assert len(accounts) >= 6
    codes = [a["code"] for a in accounts]
    assert "1110101" in codes


def test_double_entry_validation():
    # Obtener cuentas
    res = client.get("/api/v1/accounting/accounts", headers=HEADERS)
    data = res.json()
    accounts = data["items"] if isinstance(data, dict) and "items" in data else data
    caja_id = next(a["id"] for a in accounts if a["code"] == "1110101")
    gastos_id = next(a["id"] for a in accounts if a["code"] == "5110101")

    # 1. Asiento desbalanceado -> Error 422 por validación de partida doble
    unbalanced_payload = {
        "entry_date": "2026-09-26",
        "description": "Asiento desbalanceado prueba",
        "lines": [
            {"account_id": caja_id, "debit": 1000.0, "credit": 0.0},
            {"account_id": gastos_id, "debit": 0.0, "credit": 500.0},
        ],
    }
    res_err = client.post(
        "/api/v1/accounting/journal-entries",
        json=unbalanced_payload,
        headers=HEADERS,
    )
    assert res_err.status_code == 422

    # 2. Asiento balanceado válido -> 201
    balanced_payload = {
        "entry_date": "2026-09-26",
        "description": "Asiento balanceado test api",
        "lines": [
            {"account_id": caja_id, "debit": 15000.0, "credit": 0.0},
            {"account_id": gastos_id, "debit": 0.0, "credit": 15000.0},
        ],
    }
    res_ok = client.post(
        "/api/v1/accounting/journal-entries",
        json=balanced_payload,
        headers=HEADERS,
    )
    assert res_ok.status_code == 201
    data = res_ok.json()
    assert data["total_debit"] == "15000.00"
    assert data["total_credit"] == "15000.00"


def test_dte_emission_flow():
    import random
    random_folio = random.randint(100000, 999999)
    dte_payload = {
        "dte_type": 33,
        "folio": random_folio,
        "issue_date": "2026-09-26",
        "receiver_rut": "76123456-7",
        "receiver_name": "Cliente de Prueba SpA",
        "subtotal": 100000.0,
        "tax_amount": 19000.0,
        "total": 119000.0,
        "currency": "CLP",
    }
    res = client.post("/api/v1/invoicing/dte", json=dte_payload, headers=HEADERS)
    assert res.status_code == 201
    data = res.json()
    assert data["dte_type"] == "33"
    assert data["folio"] == random_folio
    
    # Si el DTE fue creado en estado draft (contrato modular 4.18/4.19), emitir mediante el endpoint issue
    if data["status"] == "draft":
        issue_res = client.post(f"/api/v1/invoicing/dte/{data['id']}/issue", headers=HEADERS)
        assert issue_res.status_code == 200
        data = issue_res.json()

    assert data["status"] in ("accepted", "issued")
    assert data["sii_track_id"] is not None
    assert f"TRACK-33-{random_folio}" in data["sii_track_id"]


