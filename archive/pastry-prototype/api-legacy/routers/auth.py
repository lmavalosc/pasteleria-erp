from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import TenantContext, get_current_context
from app.core.security import create_access_token, verify_password
from app.schemas.core_models import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    SwitchTenantRequest,
    SwitchTenantResponse,
)
from app.services.tenant_service import tenant_store

router = APIRouter(prefix="/v1/auth", tags=["auth"])

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest):
    existing = tenant_store.get_user_by_email(payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado."
        )

    tenant, user, membership = tenant_store.create_user_and_tenant(
        email=payload.email,
        password=payload.password,
        nombre_completo=payload.nombre_completo,
        razon_social=payload.razon_social,
        rut_o_identificador=payload.rut_o_identificador,
        nombre_fantasia=payload.nombre_fantasia
    )

    token = create_access_token({
        "sub": user["id"],
        "tenant_id": tenant["id"],
        "role": membership["rol"]
    })

    return RegisterResponse(
        access_token=token,
        token_type="bearer",
        tenant_id=tenant["id"],
        user_id=user["id"],
        role=membership["rol"]
    )

@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest):
    user = tenant_store.get_user_by_email(payload.email)
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas."
        )

    if not user.get("activo", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo."
        )

    memberships = tenant_store.get_user_memberships(user["id"])
    if not memberships:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario no tiene membresías en ninguna empresa."
        )

    active_tenant_id = payload.tenant_id or memberships[0]["tenant_id"]
    current_membership = next((m for m in memberships if m["tenant_id"] == active_tenant_id), None)
    if not current_membership:
        current_membership = memberships[0]
        active_tenant_id = current_membership["tenant_id"]

    token = create_access_token({
        "sub": user["id"],
        "tenant_id": active_tenant_id,
        "role": current_membership["rol"]
    })

    return LoginResponse(
        access_token=token,
        token_type="bearer",
        tenant_id=active_tenant_id,
        user_id=user["id"],
        role=current_membership["rol"]
    )

@router.post("/switch-tenant", response_model=SwitchTenantResponse)
def switch_tenant(
    payload: SwitchTenantRequest,
    context: TenantContext = Depends(get_current_context)
):
    target_membership = tenant_store.get_membership(payload.tenant_id, context.user_id)
    if not target_membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes membresía activa en la empresa destino solicitada."
        )

    token = create_access_token({
        "sub": context.user_id,
        "tenant_id": payload.tenant_id,
        "role": target_membership["rol"]
    })

    return SwitchTenantResponse(
        access_token=token,
        token_type="bearer",
        tenant_id=payload.tenant_id,
        role=target_membership["rol"]
    )
