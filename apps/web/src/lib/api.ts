import { createApiClient } from "@repo/api-client";

export const api = createApiClient({
  baseUrl: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1",
  tenantId: process.env.NEXT_PUBLIC_TENANT_ID,
});

// Backward compatibility alias for existing components
export const apiClient = api;
