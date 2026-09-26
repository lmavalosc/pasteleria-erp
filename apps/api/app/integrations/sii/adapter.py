from app.core.config import settings
from app.integrations.sii.port import SIIClientPort
from app.integrations.sii.stub import StubSIIClient


class RealSIIAdapter(SIIClientPort):
    """Adaptador de producción conectado al servicio SOAP/REST del SII."""

    def __init__(self, env: str):
        self.env = env

    def emit_dte(self, payload):
        raise NotImplementedError("El conector real SOAP del SII se activará en despliegues certificados.")

    def get_track_status(self, track_id: str) -> str:
        raise NotImplementedError("El conector real SOAP del SII se activará en despliegues certificados.")


def get_sii_client() -> SIIClientPort:
    if settings.SII_PROVIDER == "sii":
        return RealSIIAdapter(env=settings.SII_ENV)
    return StubSIIClient()
