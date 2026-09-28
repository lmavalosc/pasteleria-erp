export type UserRole = 'customer' | 'admin' | 'pastry_chef' | 'delivery';

export interface Address {
  id: string;
  street: string;
  number: string;
  apartment?: string;
  city: string;
  state: string;
  postalCode: string;
  country: string;
  referenceNotes?: string;
  isDefault?: boolean;
}

export interface User {
  id: string;
  name: string;
  email: string;
  phone?: string;
  role: UserRole;
  avatarUrl?: string;
  addresses: Address[];
  createdAt: string;
  updatedAt: string;
}

export interface AuthCredentials {
  email: string;
  password?: string;
  code?: string;
}

export interface AuthResponse {
  user: User;
  token: string;
  refreshToken?: string;
}
