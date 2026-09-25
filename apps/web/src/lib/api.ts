import { createFetchClient } from '@pasteleria/api-client';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:4000/v1';
const TENANT_ID = process.env.NEXT_PUBLIC_TENANT_ID || 'default-atelier';

export const apiClient = createFetchClient(API_BASE_URL, {
  'X-Tenant-ID': TENANT_ID,
});
