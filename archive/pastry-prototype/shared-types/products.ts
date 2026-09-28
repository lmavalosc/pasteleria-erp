export type StockStatus = 'in_stock' | 'low_stock' | 'out_of_stock' | 'pre_order_only';

export interface Category {
  id: string;
  name: string;
  slug: string;
  description: string;
  image: string;
  displayOrder: number;
}

export interface ProductVariant {
  id: string;
  name: string; // e.g. "6 porciones", "12 porciones", "Individual"
  portions: number;
  price: number;
  weightGrams?: number;
  sku: string;
  isAvailable: boolean;
}

export interface Product {
  id: string;
  name: string;
  slug: string;
  tagline: string;
  description: string;
  price: number; // Base price
  discountedPrice?: number;
  categoryId: string;
  category?: Category;
  images: string[];
  ingredients: string[];
  allergens: string[]; // e.g. ["Gluten", "Lácteos", "Frutos secos"]
  calories?: number;
  isGlutenFree: boolean;
  isVegan: boolean;
  isCustomizable: boolean;
  rating: number;
  reviewsCount: number;
  stockStatus: StockStatus;
  prepTimeMinutes: number; // For fresh pastry prep
  leadTimeHours?: number; // Pre-order required hours (e.g. 24h for complex cakes)
  variants: ProductVariant[];
  featured?: boolean;
}

export interface CustomCakeOption {
  id: string;
  name: string;
  extraPrice: number;
}

export interface CustomCakeTier {
  tierNumber: number;
  flavorId: string;
  flavorName: string;
  fillingId: string;
  fillingName: string;
}

export interface CustomCakeQuoteRequest {
  customerName: string;
  customerEmail: string;
  customerPhone: string;
  eventDate: string;
  guestCount: number;
  tiers: CustomCakeTier[];
  frostingType: 'buttercream' | 'ganache' | 'fondant' | 'merengue_suizo' | 'nata_fresca';
  spongeType: 'vainilla_bourbon' | 'chocolate_belga' | 'red_velvet' | 'zanahoria_especias' | 'limon_amapola';
  fillingType: 'frambuesa_silvestre' | 'dulce_de_leche' | 'crema_maracuya' | 'avellana_praline' | 'trufa_negra';
  themeDescription: string;
  referenceImages?: string[];
  notes?: string;
  budgetRange?: string;
}
