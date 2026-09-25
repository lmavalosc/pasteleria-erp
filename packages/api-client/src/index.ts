import createClient, { type Client } from 'openapi-fetch';
import type { paths, components } from '@pasteleria/shared-types';

export * from './client';
export * from './mock-data';
export type { paths, components };

/**
 * Cliente OpenAPI tipado basado en openapi-fetch consumiendo los contratos de @pasteleria/shared-types
 */
export function createFetchClient(
  baseUrl: string = 'http://localhost:4000',
  defaultHeaders: Record<string, string> = {}
): Client<paths> {
  return createClient<paths>({
    baseUrl,
    headers: {
      'Content-Type': 'application/json',
      ...defaultHeaders,
    },
  });
}

export type TypedFetchClient = Client<paths>;
