import Link from 'next/link';
import { apiClient } from '../lib/api';

async function getHealthStatus() {
  try {
    const { data, error } = await apiClient.GET('/health');
    if (error || !data) {
      return {
        status: 'error',
        service: 'FastAPI Service',
        tenant_id: 'unknown',
        timestamp: new Date().toISOString(),
      };
    }
    return data;
  } catch (err) {
    return {
      status: 'offline',
      service: 'FastAPI Service (Local)',
      tenant_id: 'default-atelier',
      timestamp: new Date().toISOString(),
    };
  }
}

export default async function HomePage() {
  const health = await getHealthStatus();

  return (
    <div className="min-h-screen bg-[#FFF9F2] text-[#2C221E]">
      {/* Top Bar Navigation */}
      <header className="border-b border-[#E8DFD5] bg-white/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="w-8 h-8 rounded-full bg-[#D4AF37] flex items-center justify-center text-white font-serif font-bold text-sm">
              M
            </span>
            <span className="font-serif text-xl font-bold tracking-tight text-[#231610]">
              Maison du Délice
            </span>
          </div>

          <nav className="flex items-center gap-6 text-sm font-medium">
            <Link href="/catalogo" className="hover:text-[#D4AF37] transition-colors">
              Catálogo Clientes
            </Link>
            <Link href="/admin/gastos" className="hover:text-[#D4AF37] transition-colors">
              Rendición Gastos
            </Link>
            <Link href="/admin/recetas" className="hover:text-[#D4AF37] transition-colors">
              Escandallos & Costeo
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-6xl mx-auto px-4 py-16">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <span className="text-xs uppercase tracking-widest text-[#D4AF37] font-semibold bg-[#F3E5AB]/40 px-3 py-1 rounded-full border border-[#D4AF37]/30">
            Plataforma Multi-Tenant • Fase 1
          </span>
          <h1 className="text-4xl md:text-5xl font-serif text-[#231610] mt-4 mb-4 tracking-tight leading-tight">
            Alta Pastelería & Gestión Integral de Taller
          </h1>
          <p className="text-base text-[#7D7068] leading-relaxed">
            Plataforma desacoplada conectada a FastAPI mediante clientes OpenAPI tipados,
            con soporte de partida doble, trazabilidad documental y costeo técnico por porción.
          </p>
        </div>

        {/* Backend Health Check Widget */}
        <div className="max-w-md mx-auto bg-white rounded-2xl p-6 border border-[#E8DFD5] shadow-sm mb-16">
          <div className="flex items-center justify-between pb-3 border-b border-[#F7EEE3]">
            <span className="text-xs font-semibold uppercase tracking-wider text-[#7D7068]">
              Estado del Backend FastAPI
            </span>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
              {health.status.toUpperCase()}
            </span>
          </div>

          <div className="mt-4 space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-[#7D7068]">Servicio:</span>
              <span className="font-mono text-[#231610]">{health.service}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-[#7D7068]">Tenant Activo:</span>
              <span className="font-mono text-[#D4AF37] font-semibold">{health.tenant_id}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-[#7D7068]">Timestamp:</span>
              <span className="font-mono text-[#7D7068]">{health.timestamp}</span>
            </div>
          </div>
        </div>

        {/* Módulos Disponibles */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Link
            href="/catalogo"
            className="group bg-white rounded-xl p-6 border border-[#E8DFD5] hover:border-[#D4AF37] transition-all hover:shadow-md"
          >
            <div className="w-10 h-10 rounded-lg bg-[#F7EEE3] flex items-center justify-center text-[#D4AF37] font-serif text-lg mb-4 group-hover:bg-[#D4AF37] group-hover:text-white transition-colors">
              P
            </div>
            <h3 className="font-serif text-xl text-[#231610] mb-2">Catálogo Clientes</h3>
            <p className="text-sm text-[#7D7068] leading-relaxed">
              Exploración de alta repostería con alérgenos, fichas técnicas y pedidos online.
            </p>
          </Link>

          <Link
            href="/admin/gastos"
            className="group bg-white rounded-xl p-6 border border-[#E8DFD5] hover:border-[#C86D74] transition-all hover:shadow-md"
          >
            <div className="w-10 h-10 rounded-lg bg-[#FCEEF0] flex items-center justify-center text-[#C86D74] font-serif text-lg mb-4 group-hover:bg-[#C86D74] group-hover:text-white transition-colors">
              G
            </div>
            <h3 className="font-serif text-xl text-[#231610] mb-2">Rendición de Gastos</h3>
            <p className="text-sm text-[#7D7068] leading-relaxed">
              Carga y validación de facturas con desglose de insumos y respaldo en bóveda.
            </p>
          </Link>

          <Link
            href="/admin/recetas"
            className="group bg-white rounded-xl p-6 border border-[#E8DFD5] hover:border-[#231610] transition-all hover:shadow-md"
          >
            <div className="w-10 h-10 rounded-lg bg-[#3D281F]/10 flex items-center justify-center text-[#231610] font-serif text-lg mb-4 group-hover:bg-[#231610] group-hover:text-white transition-colors">
              E
            </div>
            <h3 className="font-serif text-xl text-[#231610] mb-2">Escandallos & Costeo</h3>
            <p className="text-sm text-[#7D7068] leading-relaxed">
              Fichas técnicas con cálculo de merma, empaque de lujo y órdenes de horneado.
            </p>
          </Link>
        </div>
      </main>
    </div>
  );
}
