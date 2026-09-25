from typing import Optional
from fastapi import Header, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from app.core.security import decode_access_token

security = HTTPBearer(auto_error=False)

class TenantContext(BaseModel):
    user_id: str
    tenant_id: str
    role: str
    email: Optional[str] = None
    is_development_fallback: bool = False

def get_current_context(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    x_tenant_id: Optional[str] = Header(default=None)
) -> TenantContext:
    """
    Regla arquitectonica:
    1. Si viene Bearer token valido, se resuelve user_id, tenant_id y role del JWT.
    2. Fallback unicamente si no viene token y viene x_tenant_id (para desarrollo local).
    3. Si no hay token ni header, deniega el acceso con 401 Unauthorized.
    """
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
                    detail="Token JWT invalido: faltan claims obligatorios (sub, tenant_id)"
                )
            
            return TenantContext(
                user_id=user_id,
                tenant_id=tenant_id,
                role=role,
                email=email,
                is_development_fallback=False
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token expirado o no autorizado: {str(e)}"
            )

    # Fallback exclusivo para llamadas internas de desarrollo
    if x_tenant_id:
        return TenantContext(
            user_id="dev-usr-01",
            tenant_id=x_tenant_id,
            role="admin",
            email="dev@pasteleria-delice.com",
            is_development_fallback=True
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Se requiere autenticacion mediante Bearer Token o cabecera X-Tenant-ID."
    )

def require_roles(*allowed_roles: str):
    def role_checker(ctx: TenantContext = Depends(get_current_context)) -> TenantContext:
        if ctx.role not in allowed_roles and ctx.role != "owner":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permiso denegado. Rol '{ctx.role}' no autorizado para esta operacion."
            )
        return ctx
    return role_checker
