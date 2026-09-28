import random
import uuid
import pytest
from fastapi.testclient import TestClient


def test_system_health(client: TestClient):
    """Verifica que el API responda al healthcheck sin requerir tenant."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_missing_tenant_header_raises_400(client: TestClient):
    """Verifica que endpoints protegidos rechacen solicitudes sin X-Tenant-ID."""
    response = client.get("/api/v1/debug/tenant-context")
    assert response.status_code in (400, 401, 422)
    data = response.json()
    assert "x-tenant-id" in str(data).lower()


def test_invalid_tenant_uuid_raises_400(client: TestClient):
    """Verifica validación de formato UUID para el tenant."""
    response = client.get(
        "/api/v1/debug/tenant-context",
        headers={"X-Tenant-ID": "tenant-invalido-123"},
    )
    assert response.status_code in (400, 401, 422)
    data = response.json()
    assert "uuid" in str(data).lower()


def test_tenant_context_injection(client: TestClient, tenant_headers: dict):
    """Verifica que PostgreSQL configure app.tenant_id en la transacción."""
    response = client.get("/api/v1/debug/tenant-context", headers=tenant_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["expected_tenant_id"] == tenant_headers["X-Tenant-ID"]
    assert data["database_tenant_context"] == tenant_headers["X-Tenant-ID"]


def test_validation_error_format_rfc7807(client: TestClient, tenant_headers: dict):
    """Verifica que errores de Pydantic respondan como ProblemDetail con status 422."""
    response = client.post(
        "/api/v1/expenses",
        json={"amount": "monto_invalido"},  # Fallo de tipo/regex
        headers=tenant_headers,
    )
    assert response.status_code == 422
    data = response.json()
    assert data["status"] == 422
    assert "validation-error" in data["type"]
    assert len(data["errors"]) > 0


def test_accounting_flow(client: TestClient, tenant_headers: dict):
    """Prueba listado y creación de cuentas contables y validación de asientos."""
    # 1. Listar cuentas sembradas en Etapa 3
    res_list = client.get("/api/v1/accounting/accounts", headers=tenant_headers)
    assert res_list.status_code == 200
    accounts = res_list.json()["items"]
    assert len(accounts) >= 2

    caja = next(a for a in accounts if a["code"] == "1110101")
    gastos = next(a for a in accounts if a["code"] == "5110101")

    # 2. Asiento contable desbalanceado debe fallar con 422 (DomainError)
    invalid_entry = {
        "entry_date": "2026-03-31",
        "description": "Asiento desbalanceado test",
        "lines": [
            {"account_id": caja["id"], "debit": "100.00", "credit": "0.00"},
            {"account_id": gastos["id"], "debit": "0.00", "credit": "50.00"},
        ],
    }
    res_invalid = client.post(
        "/api/v1/accounting/journal-entries",
        json=invalid_entry,
        headers=tenant_headers,
    )
    assert res_invalid.status_code == 422
    assert "JOURNAL_ENTRY_NOT_BALANCED" in res_invalid.json().get("type", "") or "validation-error" in res_invalid.json().get("type", "")

    # 3. Asiento contable balanceado válido
    valid_entry = {
        "entry_date": "2026-03-31",
        "description": "Asiento de prueba smoke",
        "lines": [
            {"account_id": caja["id"], "debit": "5000.00", "credit": "0.00", "memo": "Ingreso"},
            {"account_id": gastos["id"], "debit": "0.00", "credit": "5000.00", "memo": "Contrapartida"},
        ],
    }
    res_valid = client.post(
        "/api/v1/accounting/journal-entries",
        json=valid_entry,
        headers=tenant_headers,
    )
    assert res_valid.status_code == 201
    entry_data = res_valid.json()
    assert entry_data["status"] == "draft"
    assert entry_data["total_debit"] == "5000.00"
    assert entry_data["total_credit"] == "5000.00"

    # 4. Postear asiento
    res_post = client.post(
        f"/api/v1/accounting/journal-entries/{entry_data['id']}/post",
        headers=tenant_headers,
    )
    assert res_post.status_code == 200
    assert res_post.json()["status"] == "posted"


def test_documents_and_expenses_flow(client: TestClient, tenant_headers: dict, sample_pdf_file):
    """Prueba subida de archivo y creación de gasto vinculado al documento."""
    # 1. Subir documento
    filename, file_bytes, mime = sample_pdf_file
    res_doc = client.post(
        "/api/v1/documents",
        files={"file": (filename, file_bytes, mime)},
        headers=tenant_headers,
    )
    assert res_doc.status_code == 201
    doc_data = res_doc.json()
    assert doc_data["filename"] == filename
    assert doc_data["checksum_sha256"] is not None

    # 2. Descargar contenido del documento
    res_content = client.get(
        f"/api/v1/documents/{doc_data['id']}/content",
        headers=tenant_headers,
    )
    assert res_content.status_code == 200
    assert len(res_content.content) > 0

    # 3. Crear gasto referenciando el documento subido
    expense_payload = {
        "expense_date": "2026-03-31",
        "amount": "14990.00",
        "currency": "CLP",
        "document_id": doc_data["id"],
        "description": "Insumos de oficina",
        "merchant": "Librería Central",
    }
    res_exp = client.post(
        "/api/v1/expenses",
        json=expense_payload,
        headers=tenant_headers,
    )
    assert res_exp.status_code == 201
    expense_data = res_exp.json()
    assert expense_data["status"] == "draft"
    assert expense_data["amount"] == "14990.00"
    assert expense_data["document_id"] == doc_data["id"]


def test_invoicing_dte_flow(client: TestClient, tenant_headers: dict):
    """Prueba creación de DTE en borrador y emisión simulada con Stub SII."""
    random_folio = random.randint(100000, 999999)
    dte_payload = {
        "dte_type": "33",
        "folio": random_folio,
        "issue_date": "2026-03-31",
        "currency": "CLP",
        "recipient_rut": "76111222-3",
        "recipient_name": "Cliente Prueba SpA",
        "subtotal": "100000.00",
        "tax_amount": "19000.00",
        "total": "119000.00",
    }

    # 1. Crear DTE en draft
    res_create = client.post(
        "/api/v1/invoicing/dte",
        json=dte_payload,
        headers=tenant_headers,
    )
    assert res_create.status_code == 201
    dte_data = res_create.json()
    assert dte_data["status"] == "draft"
    assert dte_data["total"] == "119000.00"

    # 2. Emitir DTE (usa el StubSiiAdapter por defecto)
    res_issue = client.post(
        f"/api/v1/invoicing/dte/{dte_data['id']}/issue",
        headers=tenant_headers,
    )
    assert res_issue.status_code == 200
    issued_data = res_issue.json()
    assert issued_data["status"] in ("issued", "accepted")
    assert issued_data["sii_track_id"].startswith(("STUB-", "TRACK-"))
