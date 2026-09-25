import { createFetchClient } from '@pasteleria/api-client';
import { Platform } from 'react-native';

// Fallback IP for development emulators: 10.0.2.2 for Android Studio, localhost for iOS simulator/web
const DEFAULT_URL = Platform.select({
  android: 'http://10.0.2.2:4000/api/v1',
  ios: 'http://localhost:4000/api/v1',
  default: 'http://localhost:4000/api/v1',
});

const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || DEFAULT_URL;
const TENANT_ID = process.env.EXPO_PUBLIC_TENANT_ID || 'default-atelier';

export const apiClient = createFetchClient(API_BASE_URL, {
  'X-Tenant-ID': TENANT_ID,
});

export { API_BASE_URL, TENANT_ID };
