import createClient, { type Client } from 'openapi-fetch';
import type { paths, components } from '@pasteleria/shared-types';

export * from './client';
export * from './mock-data';
export type { paths, components };

export class ApiError extends Error {
  status: number;
  detail?: unknown;

  constructor(message: string, status: number, detail?: unknown) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail;
  }
}

export interface ApiClientOptions {
  baseUrl: string;
  tenantId?: string;
  accessToken?: string;
  headers?: Record<string, string>;
  fetch?: typeof fetch;
}

export function createApiClient(options: ApiClientOptions): Client<paths> {
  const client = createClient<paths>({
    baseUrl: options.baseUrl,
    fetch: options.fetch,
  });

  client.use({
    onRequest({ request }) {
      if (options.tenantId) {
        request.headers.set('X-Tenant-ID', options.tenantId);
      }

      if (options.accessToken) {
        request.headers.set('Authorization', `Bearer ${options.accessToken}`);
      }

      if (options.headers) {
        for (const [key, value] of Object.entries(options.headers)) {
          request.headers.set(key, value);
        }
      }

      return request;
    },
  });

  return client;
}

export function unwrap<T>(result: {
  data?: T;
  error?: unknown;
  response?: Response;
}): T {
  const status = result.response?.status ?? 0;

  if (!result.response?.ok) {
    throw new ApiError(
      `API request failed with status ${status}`,
      status,
      result.error ?? result.data
    );
  }

  if (result.data === undefined) {
    throw new ApiError('Unexpected empty response', status, undefined);
  }

  return result.data;
}

/**
 * Cliente OpenAPI tipado basado en openapi-fetch consumiendo los contratos de @pasteleria/shared-types
 */
export function createFetchClient(
  baseUrl: string = 'http://localhost:4000',
  defaultHeaders: Record<string, string> = {}
): Client<paths> {
  return createApiClient({
    baseUrl,
    headers: {
      'Content-Type': 'application/json',
      ...defaultHeaders,
    },
  });
}

export type TypedFetchClient = Client<paths>;

