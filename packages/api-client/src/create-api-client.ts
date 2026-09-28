import { createClient } from './client';

export interface CreateApiClientOptions {
  baseUrl: string;
  tenantId?: string;
  token?: string;
  headers?: Record<string, string>;
}

export function createApiClient(options: CreateApiClientOptions) {
  const customHeaders: Record<string, string> = {
    ...(options.tenantId ? { 'X-Tenant-ID': options.tenantId } : {}),
    ...(options.token ? { Authorization: `Bearer ${options.token}` } : {}),
    ...options.headers,
  };

  return createClient({
    baseUrl: options.baseUrl,
    headers: customHeaders,
  });
}
