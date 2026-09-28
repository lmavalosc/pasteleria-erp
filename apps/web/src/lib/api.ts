import { createClient, client, createApiClient } from "@repo/api-client";

export const api = createApiClient({
  baseUrl: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1",
  tenantId: process.env.NEXT_PUBLIC_TENANT_ID ?? "00000000-0000-0000-0000-000000000001",
});

export const apiClient = api;
export { client, createClient };
