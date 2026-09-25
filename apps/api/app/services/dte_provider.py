from abc import ABC, abstractmethod
from typing import Dict, Any
import uuid
from datetime import datetime

class DTEProvider(ABC):
    @abstractmethod
    def emit_dte(self, dte_record: dict) -> Dict[str, Any]:
        """
        Emits DTE to SII or provider.
        Returns dict with track_id, estado_sii, and optional xml/pdf url.
        """
        pass

class MockDTEProvider(DTEProvider):
    """
    Mock implementation simulating SII acceptance for staging & development.
    No certificate or CAF required.
    """
    def emit_dte(self, dte_record: dict) -> Dict[str, Any]:
        track_id = f"SII-SIM-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
        xml_uri = f"sii-storage://mock-env/dte-{dte_record['tipo_dte']}-folio-{dte_record['folio']}.xml"
        return {
            "track_id_sii": track_id,
            "estado_sii": "accepted_by_sii",
            "xml_payload_uri": xml_uri
        }

dte_provider = MockDTEProvider()
