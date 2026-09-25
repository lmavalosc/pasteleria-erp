import random
from fastapi import APIRouter, Header
from schemas.models import CustomCakeQuoteInput, CustomCakeQuoteResponse

router = APIRouter(prefix="/custom-cakes", tags=["CustomCakes"])

@router.post("/quote", response_model=CustomCakeQuoteResponse)
def request_custom_cake_quote(payload: CustomCakeQuoteInput, x_tenant_id: str = Header(default="default-atelier")):
    quote_number = random.randint(100000, 999999)
    base_price = payload.guestCount * 4.8
    min_price = round(base_price * 0.9, 0)
    max_price = round(base_price * 1.35, 0)

    return CustomCakeQuoteResponse(
        quoteId=f"QT-{quote_number}",
        estimatedPriceMin=min_price,
        estimatedPriceMax=max_price,
        message=f"¡Gracias {payload.customerName}! El chef pastelero ha recibido tu solicitud para el evento del {payload.eventDate}. Recibirás la propuesta visual en {payload.customerEmail}.",
    )
