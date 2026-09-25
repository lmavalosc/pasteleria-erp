from typing import List
from datetime import datetime
from fastapi import APIRouter, HTTPException, Header
from schemas.models import OrderSchema, CreateOrderInput, OrderItemSchema

router = APIRouter(prefix="/orders", tags=["Orders"])

ORDERS_DB: List[OrderSchema] = [
    OrderSchema(
        id="ord-1001",
        orderNumber="PAST-2026-0042",
        customerName="Lucía Fernández",
        customerEmail="lucia@ejemplo.com",
        customerPhone="+34 612 345 678",
        status="in_preparation",
        deliveryType="delivery",
        scheduledDate="2026-09-26",
        scheduledTime="15:00 - 17:00",
        items=[
            OrderItemSchema(
                id="item-1",
                productId="prod-opera-noir",
                productName="Gâteau Opéra Grand Cru",
                productImage="https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=800&q=80",
                variantName="6 a 8 Porciones",
                quantity=1,
                unitPrice=34.0,
                totalPrice=34.0,
                customMessage="¡Feliz Cumpleaños!",
            ),
            OrderItemSchema(
                id="item-2",
                productId="prod-macarons-prestige",
                productName="Coffret Prestige 12 Macarons",
                productImage="https://images.unsplash.com/photo-1569864321318-64445eb07464?auto=format&fit=crop&w=800&q=80",
                variantName="Caja x 12 unidades",
                quantity=1,
                unitPrice=24.0,
                totalPrice=24.0,
            ),
        ],
        subtotal=58.0,
        tax=5.8,
        deliveryFee=4.5,
        discount=0.0,
        total=68.3,
        paymentStatus="paid",
        paymentMethod="card",
        createdAt="2026-09-25T09:30:00Z",
    )
]

@router.get("", response_model=List[OrderSchema])
def list_orders(x_tenant_id: str = Header(default="default-atelier")):
    return ORDERS_DB

@router.get("/{order_id}", response_model=OrderSchema)
def get_order(order_id: str, x_tenant_id: str = Header(default="default-atelier")):
    for o in ORDERS_DB:
        if o.id == order_id or o.orderNumber == order_id:
            return o
    raise HTTPException(status_code=404, detail="Pedido no encontrado.")

@router.post("", response_model=OrderSchema, status_code=201)
def create_order(payload: CreateOrderInput, x_tenant_id: str = Header(default="default-atelier")):
    subtotal = 0.0
    items: List[OrderItemSchema] = []

    for idx, item_input in enumerate(payload.items):
        item_price = 35.0  # Base estimated price
        total_item_price = item_price * item_input.quantity
        subtotal += total_item_price
        items.append(
            OrderItemSchema(
                id=f"item-{len(items) + 1}",
                productId=item_input.productId,
                productName="Pieza de Alta Pastelería",
                productImage="https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=800&q=80",
                variantId=item_input.variantId,
                quantity=item_input.quantity,
                unitPrice=item_price,
                totalPrice=total_item_price,
                customMessage=item_input.customMessage,
            )
        )

    delivery_fee = 4.5 if payload.deliveryType == 'delivery' else 0.0
    tax = round(subtotal * 0.10, 2)
    total = round(subtotal + tax + delivery_fee, 2)

    new_order = OrderSchema(
        id=f"ord-{len(ORDERS_DB) + 1001}",
        orderNumber=f"PAST-2026-{len(ORDERS_DB) + 43:04d}",
        customerName=payload.customerName,
        customerEmail=payload.customerEmail,
        customerPhone=payload.customerPhone,
        items=items,
        status="confirmed",
        deliveryType=payload.deliveryType,
        scheduledDate=payload.scheduledDate,
        scheduledTime=payload.scheduledTime or "10:00 - 12:00",
        subtotal=subtotal,
        tax=tax,
        deliveryFee=delivery_fee,
        discount=0.0,
        total=total,
        paymentStatus="paid",
        paymentMethod=payload.paymentMethod,
        notes=payload.notes,
        createdAt=datetime.utcnow().isoformat() + "Z",
    )
    ORDERS_DB.insert(0, new_order)
    return new_order
