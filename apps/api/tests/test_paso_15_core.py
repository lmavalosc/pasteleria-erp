import io
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_15_1_auth_and_tenant_flow():
    # 1. Register new user and tenant
    reg_payload = {
        "email": "pastelero@delice.cl",
        "password": "SecretPassword123!",
        "nombre_completo": "Jean-Luc Boulanger",
        "razon_social": "Delice Pasteleria Artesanal SpA",
        "rut_o_identificador": "76.999.888-1",
        "nombre_fantasia": "Maison Delice"
    }
    res_reg = client.post("/v1/auth/register", json=reg_payload)
    assert res_reg.status_code == 201, res_reg.text
    reg_data = res_reg.json()
    assert "access_token" in reg_data
    assert reg_data["role"] == "owner"
    token = reg_data["access_token"]
    tenant_id = reg_data["tenant_id"]

    # 2. Login
    login_payload = {
        "email": "pastelero@delice.cl",
        "password": "SecretPassword123!"
    }
    res_login = client.post("/v1/auth/login", json=login_payload)
    assert res_login.status_code == 200
    assert res_login.json()["tenant_id"] == tenant_id

    # 3. Test multi-tenant isolation with Bearer Token
    headers = {"Authorization": f"Bearer {token}"}
    return headers, tenant_id

def test_15_2_document_upload_and_download():
    # Register user to get token
    reg_res = client.post("/v1/auth/register", json={
        "email": "docs_tester@delice.cl",
        "password": "Password123!",
        "nombre_completo": "Auditor Documental",
        "razon_social": "Auditoria SpA"
    })
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    file_bytes = b"%PDF-1.4 Mock Receipt for Organic Flour Purchase"
    files = {"file": ("factura_compra_harina.pdf", file_bytes, "application/pdf")}
    upload_res = client.post("/v1/documents/upload", headers=headers, files=files)
    assert upload_res.status_code == 201, upload_res.text
    doc_data = upload_res.json()
    assert doc_data["filename_original"] == "factura_compra_harina.pdf"
    assert doc_data["mime_type"] == "application/pdf"
    doc_id = doc_data["id"]

    # Metadata
    meta_res = client.get(f"/v1/documents/{doc_id}", headers=headers)
    assert meta_res.status_code == 200
    assert meta_res.json()["checksum_sha256"] == doc_data["checksum_sha256"]

    # Download
    dl_res = client.get(f"/v1/documents/{doc_id}/download", headers=headers)
    assert dl_res.status_code == 200
    assert dl_res.content == file_bytes

def test_15_3_expense_flow_with_document():
    reg_res = client.post("/v1/auth/register", json={
        "email": "chef_gastos@delice.cl",
        "password": "Password123!",
        "nombre_completo": "Chef Compras",
        "razon_social": "Chef Gastos SpA"
    })
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Upload voucher
    voucher_bytes = b"Boleta 1234 - Frutas y Bayas"
    files = {"file": ("boleta_frutas.png", voucher_bytes, "image/png")}
    doc_res = client.post("/v1/documents/upload", headers=headers, files=files)
    doc_id = doc_res.json()["id"]

    # Create expense
    exp_payload = {
        "folio_comprobante": "BOL-9871",
        "proveedor_nombre": "Distribuidora Fruticola",
        "proveedor_rut": "77.111.222-3",
        "fecha_gasto": "2026-09-25",
        "monto_neto": 50000.0,
        "monto_iva": 9500.0,
        "monto_total": 59500.0,
        "moneda": "CLP",
        "categoria_gasto": "materias_primas",
        "metodo_pago": "transferencia",
        "document_id": doc_id
    }
    exp_res = client.post("/v1/expenses", headers=headers, json=exp_payload)
    assert exp_res.status_code == 201, exp_res.text
    exp = exp_res.json()
    assert exp["estado"] == "pending_approval"
    exp_id = exp["id"]

    # List expenses
    list_res = client.get("/v1/expenses", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    # Approve expense
    approve_res = client.post(f"/v1/expenses/{exp_id}/approve", headers=headers)
    assert approve_res.status_code == 200
    assert approve_res.json()["estado"] == "approved"

def test_15_4_accounting_double_entry_balance():
    reg_res = client.post("/v1/auth/register", json={
        "email": "contador@delice.cl",
        "password": "Password123!",
        "nombre_completo": "Contador General",
        "razon_social": "Pasteleria Contable SpA"
    })
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Accounts
    accs_res = client.get("/v1/accounting/accounts", headers=headers)
    assert accs_res.status_code == 200
    accounts = accs_res.json()
    assert len(accounts) >= 10
    caja_id = next(a["id"] for a in accounts if a["codigo"] == "1.1.01")
    ventas_id = next(a["id"] for a in accounts if a["codigo"] == "4.1.01")

    # 1. Unbalanced entry should fail on post
    unbalanced_entry = {
        "fecha_asiento": "2026-09-25",
        "glosa_descripcion": "Venta desbalanceada",
        "items": [
            {"account_id": caja_id, "debe": 10000.0, "haber": 0.0},
            {"account_id": ventas_id, "debe": 0.0, "haber": 8000.0} # diff 2000
        ]
    }
    created_unbalanced = client.post("/v1/accounting/entries", headers=headers, json=unbalanced_entry).json()
    post_unbalanced = client.post(f"/v1/accounting/entries/{created_unbalanced['id']}/post", headers=headers)
    assert post_unbalanced.status_code == 400
    assert "no está cuadrado" in post_unbalanced.json()["detail"]

    # 2. Balanced entry must succeed
    balanced_entry = {
        "fecha_asiento": "2026-09-25",
        "glosa_descripcion": "Venta de tarta de frambuesa en efectivo",
        "items": [
            {"account_id": caja_id, "debe": 15000.0, "haber": 0.0},
            {"account_id": ventas_id, "debe": 0.0, "haber": 15000.0}
        ]
    }
    created_balanced = client.post("/v1/accounting/entries", headers=headers, json=balanced_entry).json()
    post_balanced = client.post(f"/v1/accounting/entries/{created_balanced['id']}/post", headers=headers)
    assert post_balanced.status_code == 200
    assert post_balanced.json()["estado"] == "posted"

def test_15_5_dte_emission_with_mock_provider():
    reg_res = client.post("/v1/auth/register", json={
        "email": "dte_admin@delice.cl",
        "password": "Password123!",
        "nombre_completo": "Encargado DTE",
        "razon_social": "Pasteleria Facturadora SpA",
        "rut_o_identificador": "76.555.444-2"
    })
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create DTE (Boleta Electrónica 39)
    dte_payload = {
        "tipo_dte": 39,
        "fecha_emision": "2026-09-25",
        "emisor_rut": "76.555.444-2",
        "receptor_rut": "66.666.666-6",
        "receptor_razon_social": "Cliente Final",
        "monto_neto": 10000.0,
        "monto_exento": 0.0,
        "monto_iva": 1900.0,
        "monto_total": 11900.0
    }
    res_create = client.post("/v1/dte/create", headers=headers, json=dte_payload)
    assert res_create.status_code == 201, res_create.text
    dte = res_create.json()
    assert dte["estado_sii"] == "draft"
    assert dte["folio"] >= 1
    dte_id = dte["id"]

    # Emit DTE (Provider mock)
    res_emit = client.post(f"/v1/dte/{dte_id}/emit", headers=headers)
    assert res_emit.status_code == 200, res_emit.text
    emitted = res_emit.json()
    assert emitted["estado_sii"] == "accepted_by_sii"
    assert emitted["track_id_sii"].startswith("SII-SIM-")
