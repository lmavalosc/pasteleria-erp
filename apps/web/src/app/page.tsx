import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center text-gray-900 p-8">
      <h1 className="text-4xl font-bold mb-4">Ncleo Contable ERP</h1>
      <p className="mb-8 text-gray-600">Bienvenido al sistema de gestin (Fase 1).</p>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl w-full">
        <Link href="/accounting" className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition">
          <h2 className="text-xl font-semibold mb-2">Contabilidad</h2>
          <p className="text-sm text-gray-500">Plan de cuentas, asientos de partida doble, balances.</p>
        </Link>
        <Link href="/invoices" className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition">
          <h2 className="text-xl font-semibold mb-2">Facturacin / DTE</h2>
          <p className="text-sm text-gray-500">Emisin de facturas, CAF, folios.</p>
        </Link>
        <Link href="/expenses" className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition">
          <h2 className="text-xl font-semibold mb-2">Gastos</h2>
          <p className="text-sm text-gray-500">Registro de gastos y digitalizacin de comprobantes.</p>
        </Link>
      </div>
    </div>
  );
}
