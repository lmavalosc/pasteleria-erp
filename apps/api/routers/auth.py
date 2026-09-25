from fastapi import APIRouter, Header
from schemas.models import LoginInput, AuthResponse

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=AuthResponse)
def login(payload: LoginInput, x_tenant_id: str = Header(default="default-atelier")):
    username = payload.email.split("@")[0].capitalize()
    return AuthResponse(
        token=f"jwt_token_sample_{x_tenant_id}_{username.lower()}",
        user={
            "id": "usr-01",
            "name": username,
            "email": payload.email,
            "role": "customer",
            "tenantId": x_tenant_id,
        },
    )
