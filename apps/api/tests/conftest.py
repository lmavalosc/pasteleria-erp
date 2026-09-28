import io
import os
import sys
import uuid
import pytest
from fastapi.testclient import TestClient

# Asegurar que apps/api esté en sys.path
api_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if api_root not in sys.path:
    sys.path.insert(0, api_root)

from app.main import app

DEMO_TENANT_ID = "00000000-0000-0000-0000-000000000001"


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def tenant_headers():
    return {
        "X-Tenant-ID": DEMO_TENANT_ID,
    }


@pytest.fixture
def sample_pdf_file():
    return (
        "factura_test.pdf",
        io.BytesIO(b"%PDF-1.4 Test file binary content for document upload"),
        "application/pdf",
    )
