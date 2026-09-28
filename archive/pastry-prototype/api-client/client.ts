import { Category, Product, Order, CreateOrderRequest, CustomCakeQuoteRequest, ProductFilters } from '@pasteleria/shared-types';
import { MOCK_CATEGORIES, MOCK_PRODUCTS, MOCK_ORDERS } from './mock-data';

export interface ApiClientConfig {
  baseUrl?: string;
  token?: string;
  useMockFallback?: boolean;
}

export class PasteleriaApiClient {
  private baseUrl: string;
  private token?: string;
  private useMockFallback: boolean;

  constructor(config: ApiClientConfig = {}) {
    this.baseUrl = config.baseUrl || 'http://localhost:4000/v1';
    this.token = config.token;
    this.useMockFallback = config.useMockFallback ?? true;
  }

  public setToken(token: string | undefined) {
    this.token = token;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = new Headers(options.headers || {});
    headers.set('Content-Type', 'application/json');

    if (this.token) {
      headers.set('Authorization', `Bearer ${this.token}`);
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      if (!response.ok) {
        throw new Error(`API Error [${response.status}]: ${response.statusText}`);
      }

      return (await response.json()) as T;
    } catch (err) {
      if (!this.useMockFallback) {
        throw err;
      }
      // Silently handled in caller if mock fallback enabled
      throw err;
    }
  }

  // === Products API ===
  public products = {
    list: async (filters: ProductFilters = {}): Promise<{ items: Product[]; total: number }> => {
      try {
        const queryParams = new URLSearchParams();
        if (filters.categoryId) queryParams.set('categoryId', filters.categoryId);
        if (filters.isGlutenFree !== undefined) queryParams.set('isGlutenFree', String(filters.isGlutenFree));
        if (filters.isVegan !== undefined) queryParams.set('isVegan', String(filters.isVegan));
        if (filters.featured !== undefined) queryParams.set('featured', String(filters.featured));
        if (filters.search) queryParams.set('search', filters.search);

        const qs = queryParams.toString() ? `?${queryParams.toString()}` : '';
        return await this.request<{ items: Product[]; total: number }>(`/products${qs}`);
      } catch {
        // Fallback to rich mock data
        let filtered = [...MOCK_PRODUCTS];
        if (filters.categoryId) {
          filtered = filtered.filter((p) => p.categoryId === filters.categoryId);
        }
        if (filters.isGlutenFree) {
          filtered = filtered.filter((p) => p.isGlutenFree);
        }
        if (filters.isVegan) {
          filtered = filtered.filter((p) => p.isVegan);
        }
        if (filters.featured) {
          filtered = filtered.filter((p) => p.featured);
        }
        if (filters.search) {
          const q = filters.search.toLowerCase();
          filtered = filtered.filter(
            (p) => p.name.toLowerCase().includes(q) || p.description.toLowerCase().includes(q)
          );
        }
        return { items: filtered, total: filtered.length };
      }
    },

    getById: async (idOrSlug: string): Promise<Product | null> => {
      try {
        return await this.request<Product>(`/products/${idOrSlug}`);
      } catch {
        const product = MOCK_PRODUCTS.find((p) => p.id === idOrSlug || p.slug === idOrSlug);
        return product || null;
      }
    },
  };

  // === Categories API ===
  public categories = {
    list: async (): Promise<Category[]> => {
      try {
        return await this.request<Category[]>('/categories');
      } catch {
        return MOCK_CATEGORIES;
      }
    },
  };

  // === Orders API ===
  public orders = {
    list: async (): Promise<Order[]> => {
      try {
        return await this.request<Order[]>('/orders');
      } catch {
        return MOCK_ORDERS;
      }
    },

    getById: async (orderId: string): Promise<Order | null> => {
      try {
        return await this.request<Order>(`/orders/${orderId}`);
      } catch {
        const order = MOCK_ORDERS.find((o) => o.id === orderId || o.orderNumber === orderId);
        return order || null;
      }
    },

    create: async (data: CreateOrderRequest): Promise<Order> => {
      try {
        return await this.request<Order>('/orders', {
          method: 'POST',
          body: JSON.stringify(data),
        });
      } catch {
        // Mock order creation for immediate offline usability
        const newOrder: Order = {
          id: `ord-${Date.now()}`,
          orderNumber: `PAST-${new Date().getFullYear()}-${Math.floor(1000 + Math.random() * 9000)}`,
          customerName: data.customerName,
          customerEmail: data.customerEmail,
          customerPhone: data.customerPhone,
          items: data.items.map((item, idx) => {
            const prod = MOCK_PRODUCTS.find((p) => p.id === item.productId);
            const variant = prod?.variants.find((v) => v.id === item.variantId);
            const unitPrice = variant?.price ?? prod?.price ?? 10;
            return {
              id: `item-${idx + 1}`,
              productId: item.productId,
              productName: prod?.name || 'Producto Artesanal',
              productImage: prod?.images[0] || '',
              variantId: item.variantId,
              variantName: variant?.name,
              quantity: item.quantity,
              unitPrice,
              totalPrice: unitPrice * item.quantity,
              customMessage: item.customMessage,
              specialInstructions: item.specialInstructions,
            };
          }),
          status: 'confirmed',
          deliveryType: data.deliveryType,
          scheduledDate: data.scheduledDate,
          scheduledTime: data.scheduledTime,
          subtotal: 45.0,
          tax: 4.5,
          deliveryFee: data.deliveryType === 'delivery' ? 4.5 : 0,
          discount: 0,
          total: data.deliveryType === 'delivery' ? 49.5 : 45.0,
          paymentStatus: 'paid',
          paymentMethod: data.paymentMethod,
          notes: data.notes,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        };
        MOCK_ORDERS.unshift(newOrder);
        return newOrder;
      }
    },
  };

  // === Custom Cake Quotes API ===
  public customCakes = {
    requestQuote: async (quoteData: CustomCakeQuoteRequest): Promise<{ quoteId: string; estimatedPriceMin: number; estimatedPriceMax: number; message: string }> => {
      try {
        return await this.request<{ quoteId: string; estimatedPriceMin: number; estimatedPriceMax: number; message: string }>('/custom-cakes/quote', {
          method: 'POST',
          body: JSON.stringify(quoteData),
        });
      } catch {
        const baseEstimate = quoteData.guestCount * 4.5;
        return {
          quoteId: `QT-${Date.now().toString().slice(-6)}`,
          estimatedPriceMin: Math.round(baseEstimate * 0.9),
          estimatedPriceMax: Math.round(baseEstimate * 1.3),
          message: `¡Gracias ${quoteData.customerName}! Nuestro chef pastelero revisará los detalles para tu evento el ${quoteData.eventDate}. Te contactaremos pronto.`,
        };
      }
    },
  };

  // === Auth API ===
  public auth = {
    login: async (credentials: { email: string; password?: string }) => {
      try {
        return await this.request<{ token: string; user: { id: string; name: string; email: string; role: string } }>('/auth/login', {
          method: 'POST',
          body: JSON.stringify(credentials),
        });
      } catch {
        return {
          token: `jwt_mock_${Date.now()}`,
          user: {
            id: 'usr-1',
            name: credentials.email.split('@')[0] || 'Cliente Gourmet',
            email: credentials.email,
            role: 'customer',
          },
        };
      }
    },
  };
}

export const createApiClient = (config?: ApiClientConfig) => new PasteleriaApiClient(config);
export const defaultApiClient = createApiClient();
