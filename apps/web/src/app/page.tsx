import Link from 'next/link';
import { api } from '@/lib/api';
import { getHealth } from '@pasteleria/api-client';

export const dynamic = 'force-dynamic';

export default async function Home() {
  let healthStatus = 'desconectado';
  let apiVersion = '1.0.0-fase1';

  try {
    const res: any = await getHealth({ client: api });
    if (res && res.data) {
      healthStatus = res.data.status || 'ok';
      apiVersion = res.data.version || '1.0.0-fase1';
    }
  } catch {
    healthStatus = 'desconectado';
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center text-gray-900 p-8">
      <div className="max-w-4xl w-full">
        <header className="mb-8 text-center">
          <h1 className="text-4xl font-bold mb-2">Núcleo Contable ERP</h1>
          <p className="text-gray-600">Base Fase 1: Contabilidad, DTE, Gastos y Documentos.</p>
          <div className="mt-4 inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white border border-gray-200 text-sm">
            <span
              className={`w-2.5 h-2.5 rounded-full ${
                healthStatus === 'ok' ? 'bg-green-500' : 'bg-amber-500'
              }`}
            />
            <span>
              Backend API:{' '}
              <strong className="capitalize">{healthStatus}</strong> (v{apiVersion})
            </span>
          </div>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h2 className="text-xl font-semibold mb-2">Contabilidad</h2>
            <p className="text-sm text-gray-500">
              Plan de cuentas, asientos de partida doble y balances contables.
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h2 className="text-xl font-semibold mb-2">Facturación / DTE</h2>
            <p className="text-sm text-gray-500">
              Emisión de DTE tributario según contrato oficial Fase 1.
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h2 className="text-xl font-semibold mb-2">Gastos & Documentos</h2>
            <p className="text-sm text-gray-500">
              Registro de gastos operacionales y custodia de archivos adjuntos.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
