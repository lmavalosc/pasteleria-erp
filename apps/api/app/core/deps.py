from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from app.core.config import settings
from app.core.security import decode_access_token

security = HTTPBearer(auto_error=False)


class TenantContext(BaseModel):
    user_id: str
    tenant_id: str
    role: str
    email: str | None = None
    is_development_fallback: bool = False


def get_current_context(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    x_tenant_id: str | None = Header(default=None),
) -> TenantContext:
    """
    Regla arquitectónica:
    1. Si viene Bearer token válido → user_id, tenant_id y role del JWT.
    2. Fallback de desarrollo SOLO si settings.debug == True y viene X-Tenant-ID.
    3. En cualquier otro caso → 401 Unauthorized.
    """
    # --- Ruta principal: JWT ---
    if credentials and credentials.credentials:
        token = credentials.credentials
        try:
            payload = decode_access_token(token)
            user_id = payload.get("sub")
            tenant_id = payload.get("tenant_id")
            role = payload.get("role", "member")
            email = payload.get("email")

            if not user_id or not tenant_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token JWT inválido: faltan claims obligatorios (sub, tenant_id)",
                )

            return TenantContext(
                user_id=user_id,
                tenant_id=tenant_id,
                role=role,
                email=email,
                is_development_fallback=False,
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token expirado o no autorizado: {e!s}",
            )

    # --- Fallback de desarrollo: SOLO en modo DEBUG ---
    if settings.debug and x_tenant_id:
        import logging
        logging.getLogger(__name__).warning(
            "⚠️  Acceso mediante fallback de desarrollo (X-Tenant-ID: %s). "
            "Deshabilitar en producción con DEBUG=false.",
            x_tenant_id,
        )
        return TenantContext(
            user_id="dev-usr-01",
            tenant_id=x_tenant_id,
            role="admin",
            email="dev@pasteleria-delice.com",
            is_development_fallback=True,
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Se requiere autenticación mediante Bearer Token.",
    )


def require_roles(*allowed_roles: str):
    def role_checker(
        ctx: TenantContext = Depends(get_current_context),
    ) -> TenantContext:
        if ctx.role not in allowed_roles and ctx.role != "owner":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permiso denegado. Rol '{ctx.role}' no autorizado para esta operación.",
            )
        return ctx
    return role_checker
