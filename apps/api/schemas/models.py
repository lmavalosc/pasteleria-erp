from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class CategorySchema(BaseModel):
    id: str
    name: str
    slug: str
    description: str
    image: str
    displayOrder: int

class ProductVariantSchema(BaseModel):
    id: str
    name: str
    portions: int
    price: float
    weightGrams: Optional[int] = None
    sku: str
    isAvailable: bool = True

class ProductSchema(BaseModel):
    id: str
    name: str
    slug: str
    tagline: str
    description: str
    price: float
    discountedPrice: Optional[float] = None
    categoryId: str
    category: Optional[CategorySchema] = None
    images: List[str]
    ingredients: List[str]
    allergens: List[str]
    calories: Optional[int] = None
    isGlutenFree: bool = False
    isVegan: bool = False
    isCustomizable: bool = False
    rating: float = 5.0
    reviewsCount: int = 0
    stockStatus: Literal['in_stock', 'low_stock', 'out_of_stock', 'pre_order_only'] = 'in_stock'
    prepTimeMinutes: int = 30
    variants: List[ProductVariantSchema] = []
    featured: bool = False

class PaginatedProductsResponse(BaseModel):
    items: List[ProductSchema]
    total: int
    page: int
    pageSize: int
    totalPages: int

class OrderItemSchema(BaseModel):
    id: str
    productId: str
    productName: str
    productImage: str
    variantId: Optional[str] = None
    variantName: Optional[str] = None
    quantity: int
    unitPrice: float
    totalPrice: float
    customMessage: Optional[str] = None

class OrderSchema(BaseModel):
    id: str
    orderNumber: str
    customerName: str
    customerEmail: str
    customerPhone: Optional[str] = None
    items: List[OrderItemSchema]
    status: Literal['pending', 'confirmed', 'in_preparation', 'ready_for_pickup', 'out_for_delivery', 'delivered', 'cancelled']
    deliveryType: Literal['pickup', 'delivery']
    scheduledDate: str
    scheduledTime: Optional[str] = None
    subtotal: float
    tax: float
    deliveryFee: float
    discount: float
    total: float
    paymentStatus: Literal['pending', 'paid', 'failed', 'refunded']
    paymentMethod: str
    notes: Optional[str] = None
    createdAt: str

class CreateOrderItemInput(BaseModel):
    productId: str
    variantId: Optional[str] = None
    quantity: int = Field(default=1, ge=1)
    customMessage: Optional[str] = None
    specialInstructions: Optional[str] = None

class CreateOrderInput(BaseModel):
    customerName: str
    customerEmail: str
    customerPhone: Optional[str] = None
    deliveryType: Literal['pickup', 'delivery']
    deliveryAddress: Optional[dict] = None
    scheduledDate: str
    scheduledTime: Optional[str] = None
    items: List[CreateOrderItemInput]
    paymentMethod: str = 'card'
    notes: Optional[str] = None

class CustomCakeQuoteInput(BaseModel):
    customerName: str
    customerEmail: str
    customerPhone: Optional[str] = None
    eventDate: str
    guestCount: int = Field(default=20, ge=10)
    frostingType: str
    spongeType: str
    fillingType: Optional[str] = None
    themeDescription: Optional[str] = None
    notes: Optional[str] = None

class CustomCakeQuoteResponse(BaseModel):
    quoteId: str
    estimatedPriceMin: float
    estimatedPriceMax: float
    message: str

class LoginInput(BaseModel):
    email: str
    password: Optional[str] = None

class AuthResponse(BaseModel):
    token: str
    user: dict
