import { Product, ProductVariant } from './products';
import { Address } from './users';

export type OrderStatus =
  | 'pending'
  | 'confirmed'
  | 'in_preparation'
  | 'ready_for_pickup'
  | 'out_for_delivery'
  | 'delivered'
  | 'cancelled';

export type PaymentStatus = 'pending' | 'paid' | 'failed' | 'refunded';

export type DeliveryType = 'pickup' | 'delivery';

export type PaymentMethod = 'card' | 'transfer' | 'cash_on_delivery' | 'mercadopago' | 'stripe';

export interface CartItem {
  id: string; // Unique cart item ID (can be uuid or `${productId}-${variantId}`)
  productId: string;
  product: Product;
  variantId?: string;
  variant?: ProductVariant;
  quantity: number;
  unitPrice: number;
  totalPrice: number;
  customMessage?: string; // Dedication on cake board or chocolate plaque
  specialInstructions?: string;
}

export interface OrderItem {
  id: string;
  productId: string;
  productName: string;
  productImage: string;
  variantId?: string;
  variantName?: string;
  quantity: number;
  unitPrice: number;
  totalPrice: number;
  customMessage?: string;
  specialInstructions?: string;
}

export interface Order {
  id: string;
  orderNumber: string;
  customerId?: string;
  customerName: string;
  customerEmail: string;
  customerPhone: string;
  items: OrderItem[];
  status: OrderStatus;
  deliveryType: DeliveryType;
  deliveryAddress?: Address;
  pickupTimeSlot?: string;
  scheduledDate: string; // ISO date YYYY-MM-DD
  scheduledTime?: string; // e.g. "14:00 - 16:00"
  subtotal: number;
  tax: number;
  deliveryFee: number;
  discount: number;
  total: number;
  paymentStatus: PaymentStatus;
  paymentMethod: PaymentMethod;
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

export interface CreateOrderRequest {
  customerName: string;
  customerEmail: string;
  customerPhone: string;
  deliveryType: DeliveryType;
  deliveryAddress?: Omit<Address, 'id' | 'isDefault'>;
  scheduledDate: string;
  scheduledTime?: string;
  items: {
    productId: string;
    variantId?: string;
    quantity: number;
    customMessage?: string;
    specialInstructions?: string;
  }[];
  paymentMethod: PaymentMethod;
  notes?: string;
}
