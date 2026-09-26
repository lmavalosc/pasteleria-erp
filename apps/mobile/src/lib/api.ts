import { createApiClient } from "@pasteleria/api-client";

export const api = createApiClient({
  baseUrl:
    process.env.EXPO_PUBLIC_API_URL ?? "http://10.0.2.2:8000/api/v1",
  tenantId: process.env.EXPO_PUBLIC_TENANT_ID,
});
