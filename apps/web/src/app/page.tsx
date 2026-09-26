import { api } from "@/lib/api";
import { unwrap, ApiError } from "@repo/api-client";

export const dynamic = 'force-dynamic';

export default async function Home() {
  try {
    const health = unwrap(await api.GET("/health"));

    return (
      <main className="flex min-h-screen flex-col items-center justify-center p-8 bg-neutral-50 text-neutral-900">
        <h1 className="mb-4 text-2xl font-bold">
          Paso 2 — Contrato OpenAPI conectado a Web
        </h1>

        <div className="w-full max-w-xl rounded border border-green-300 bg-green-50 p-4 text-green-900 shadow-sm">
          <p className="font-semibold flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-green-500 animate-pulse"></span>
            API OK
          </p>
          <pre className="mt-2 overflow-auto text-sm bg-white/70 p-3 rounded border border-green-200">
            {JSON.stringify(health, null, 2)}
          </pre>
        </div>
      </main>
    );
  } catch (error) {
    const message =
      error instanceof ApiError
        ? `${error.message} (status ${error.status})`
        : String(error);

    return (
      <main className="flex min-h-screen flex-col items-center justify-center p-8 bg-neutral-50 text-neutral-900">
        <h1 className="mb-4 text-2xl font-bold">
          Paso 2 — Contrato OpenAPI conectado a Web
        </h1>

        <div className="w-full max-w-xl rounded border border-red-300 bg-red-50 p-4 text-red-900 shadow-sm">
          <p className="font-semibold flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-red-500"></span>
            Error conectando con API
          </p>
          <p className="mt-2 text-sm">{message}</p>
        </div>
      </main>
    );
  }
}
