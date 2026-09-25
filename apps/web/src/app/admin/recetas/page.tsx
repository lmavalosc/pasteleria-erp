'use client';

import React, { useState } from 'react';
import Link from 'next/link';

interface IngredienteEscandallo {
  id: string;
  nombre: string;
  cantidad: number; // en la unidad especificada
  unidad: string;
  costoUnitarioPPP: number; // por kg, litro o unidad
  mermaPorcentaje: number;
}

interface EmpaqueItem {
  nombre: string;
  cantidad: number;
  costoUnitario: number;
}

export default function RecetasPage() {
  // Estado de la preparación seleccionada
  const [nombreReceta, setNombreReceta] = useState('Torta Ópera de Autor');
  const [porciones, setPorciones] = useState(8);
  const [precioVentaNeto, setPrecioVentaNeto] = useState(28000);

  // Insumos de la ficha técnica según el flujo de producción
  const [ingredientes, setIngredientes] = useState<IngredienteEscandallo[]>([
    {
      id: 'ing-1',
      nombre: 'Harina Pastelera T55',
      cantidad: 0.35, // 350g
      unidad: 'kg',
      costoUnitarioPPP: 1000,
      mermaPorcentaje: 0,
    },
    {
      id: 'ing-2',
      nombre: 'Mantequilla 82% MG',
      cantidad: 0.25, // 250g
      unidad: 'kg',
      costoUnitarioPPP: 7500,
      mermaPorcentaje: 0,
    },
    {
      id: 'ing-3',
      nombre: 'Chocolate Belga 70%',
      cantidad: 0.30, // 300g
      unidad: 'kg',
      costoUnitarioPPP: 13000,
      mermaPorcentaje: 0,
    },
    {
      id: 'ing-4',
      nombre: 'Huevos de Campo (unidad)',
      cantidad: 5,
      unidad: 'un',
      costoUnitarioPPP: 200,
      mermaPorcentaje: 0,
    },
  ]);

  // Merma técnica global de horneado/elaboración
  const [mermaGlobalPorcentaje, setMermaGlobalPorcentaje] = useState(5.0);

  // Empaque y presentación de lujo
  const [empaqueCosto, setEmpaqueCosto] = useState(1500);

  // Cálculos dinámicos
  const costoInsumosNeto = ingredientes.reduce((acc, item) => {
    const costoBrutoItem = item.cantidad * (1 + item.mermaPorcentaje / 100) * item.costoUnitarioPPP;
    return acc + costoBrutoItem;
  }, 0);

  const costoMermaGlobal = (costoInsumosNeto * mermaGlobalPorcentaje) / 100;
  const costoInsumosTotal = costoInsumosNeto + costoMermaGlobal;
  const costoTotalBatch = costoInsumosTotal + empaqueCosto;
  const costoPorPorcion = porciones > 0 ? costoTotalBatch / porciones : 0;

  // Rentabilidad
  const margenBrutoMonto = precioVentaNeto - costoTotalBatch;
  const margenBrutoPorcentaje = precioVentaNeto > 0 ? (margenBrutoMonto / precioVentaNeto) * 100 : 0;
  const esMargenBajo = margenBrutoPorcentaje < 50.0;

  // Simulación de actualización de factura (Molino Central)
  const [facturaSimuladaAplicada, setFacturaSimuladaAplicada] = useState(false);

  const handleSimularFacturaProveedor = () => {
    if (!facturaSimuladaAplicada) {
      // Simula que la mantequilla subió a $8.500 y la harina bajó a $950 en la última factura
      setIngredientes((prev) =>
        prev.map((ing) => {
          if (ing.nombre.includes('Mantequilla')) return { ...ing, costoUnitarioPPP: 8500 };
          if (ing.nombre.includes('Harina')) return { ...ing, costoUnitarioPPP: 950 };
          return ing;
        })
      );
      setFacturaSimuladaAplicada(true);
    } else {
      // Revertir a valores base
      setIngredientes((prev) =>
        prev.map((ing) => {
          if (ing.nombre.includes('Mantequilla')) return { ...ing, costoUnitarioPPP: 7500 };
          if (ing.nombre.includes('Harina')) return { ...ing, costoUnitarioPPP: 1000 };
          return ing;
        })
      );
      setFacturaSimuladaAplicada(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 pb-6 border-b border-[#E8DFD5] gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs uppercase tracking-widest text-[#D4AF37] font-semibold">Taller de Producción</span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-amber-50 text-amber-800 border border-amber-200">
              Escandallos en Vivo
            </span>
          </div>
          <h1 className="text-3xl font-serif text-[#231610] mt-1">Costeo de Preparaciones & Fichas Técnicas</h1>
          <p className="text-sm text-[#7D7068] mt-1">
            Calcula el costo real de elaboración a partir de tus facturas de materias primas y analiza tu margen de utilidad.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            href="/admin/gastos"
            className="text-xs font-semibold px-4 py-2.5 rounded-lg border border-[#E8DFD5] text-[#231610] bg-white hover:bg-[#FFF9F2] transition-colors"
          >
            📋 Ver Facturas y Gastos
          </Link>
          <Link
            href="/"
            className="text-xs font-semibold px-4 py-2.5 rounded-lg bg-[#231610] text-[#FFF9F2] hover:bg-[#3D271D] transition-colors"
          >
            ← Volver a la Tienda
          </Link>
        </div>
      </div>

      {/* Pipeline Visual de 4 Pasos */}
      <div className="mb-10 bg-[#FFF9F2] border border-[#E8DFD5] rounded-2xl p-6 shadow-sm">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-[#7D7068] mb-4">
          Flujo de Datos Automatizado: De la Factura a la Vitrina
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 relative">
          {/* Paso 1 */}
          <div className="bg-white p-4 rounded-xl border border-[#E8DFD5] shadow-xs">
            <div className="flex items-center justify-between text-xs text-[#7D7068] mb-1 font-semibold">
              <span>1. Factura Proveedor</span>
              <span className="text-[#C86D74]">Bóveda</span>
            </div>
            <p className="text-sm font-medium text-[#231610]">Molino Central SpA</p>
            <p className="text-xs text-[#7D7068] mt-1">• 25 kg Harina ($25.000)</p>
            <p className="text-xs text-[#7D7068]">• 10 kg Mantequilla ($75.000)</p>
          </div>

          {/* Paso 2 */}
          <div className="bg-white p-4 rounded-xl border border-[#E8DFD5] shadow-xs">
            <div className="flex items-center justify-between text-xs text-[#7D7068] mb-1 font-semibold">
              <span>2. Materias Primas</span>
              <span className="text-amber-600">PPP Calculado</span>
            </div>
            <p className="text-sm font-medium text-[#231610]">Inventario del Tenant</p>
            <p className="text-xs text-[#7D7068] mt-1">• Harina: $1.000 / kg</p>
            <p className="text-xs text-[#7D7068]">• Mantequilla: $7.500 / kg</p>
          </div>

          {/* Paso 3 */}
          <div className="bg-white p-4 rounded-xl border border-[#E8DFD5] shadow-xs">
            <div className="flex items-center justify-between text-xs text-[#7D7068] mb-1 font-semibold">
              <span>3. Ficha Técnica</span>
              <span className="text-[#D4AF37]">Escandallo</span>
            </div>
            <p className="text-sm font-medium text-[#231610]">{nombreReceta}</p>
            <p className="text-xs text-[#7D7068] mt-1">• Insumos: ${costoInsumosTotal.toLocaleString('es-CL')}</p>
            <p className="text-xs text-[#7D7068]">• Empaque: ${empaqueCosto.toLocaleString('es-CL')}</p>
          </div>

          {/* Paso 4 */}
          <div className={`p-4 rounded-xl border shadow-xs ${esMargenBajo ? 'bg-rose-50 border-rose-200' : 'bg-emerald-50 border-emerald-200'}`}>
            <div className="flex items-center justify-between text-xs mb-1 font-semibold">
              <span className={esMargenBajo ? 'text-rose-800' : 'text-emerald-800'}>4. Margen & Precio</span>
              <span className={`text-xs px-2 py-0.5 rounded-full font-bold ${esMargenBajo ? 'bg-rose-200 text-rose-900' : 'bg-emerald-200 text-emerald-900'}`}>
                {margenBrutoPorcentaje.toFixed(1)}%
              </span>
            </div>
            <p className="text-sm font-medium text-[#231610]">Venta: ${precioVentaNeto.toLocaleString('es-CL')}</p>
            <p className={`text-xs mt-1 font-semibold ${esMargenBajo ? 'text-rose-700' : 'text-emerald-700'}`}>
              Ganancia: ${margenBrutoMonto.toLocaleString('es-CL')}
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Columna Izquierda / Centro: Ficha Técnica Interactiva */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-2xl border border-[#E8DFD5] p-6 shadow-sm">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-[#F7EEE3] gap-4">
              <div>
                <label className="text-xs text-[#7D7068] font-semibold uppercase tracking-wider block">Receta / Creación</label>
                <input
                  type="text"
                  value={nombreReceta}
                  onChange={(e) => setNombreReceta(e.target.value)}
                  className="font-serif text-xl text-[#231610] font-medium border-b border-transparent hover:border-[#D4AF37] focus:border-[#D4AF37] outline-none transition-colors"
                />
              </div>

              <div className="flex items-center gap-4">
                <div>
                  <label className="text-xs text-[#7D7068] block">Rendimiento (porciones)</label>
                  <input
                    type="number"
                    min="1"
                    value={porciones}
                    onChange={(e) => setPorciones(Math.max(1, parseInt(e.target.value) || 1))}
                    className="w-20 px-3 py-1.5 text-sm rounded-lg border border-[#E8DFD5] text-[#231610] text-center font-medium focus:ring-1 focus:ring-[#D4AF37] outline-none"
                  />
                </div>
                <div>
                  <label className="text-xs text-[#7D7068] block">Merma Técnica (%)</label>
                  <input
                    type="number"
                    step="0.5"
                    min="0"
                    value={mermaGlobalPorcentaje}
                    onChange={(e) => setMermaGlobalPorcentaje(parseFloat(e.target.value) || 0)}
                    className="w-20 px-3 py-1.5 text-sm rounded-lg border border-[#E8DFD5] text-[#231610] text-center font-medium focus:ring-1 focus:ring-[#D4AF37] outline-none"
                  />
                </div>
              </div>
            </div>

            {/* Tabla de Insumos */}
            <div className="mt-6 overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="text-xs uppercase tracking-wider text-[#7D7068] border-b border-[#E8DFD5]">
                    <th className="pb-3 font-semibold">Materia Prima / Insumo</th>
                    <th className="pb-3 font-semibold text-right">Cantidad Neta</th>
                    <th className="pb-3 font-semibold text-right">Costo Unit. (PPP)</th>
                    <th className="pb-3 font-semibold text-right">Subtotal Insumo</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#F7EEE3]">
                  {ingredientes.map((item) => {
                    const costoCalculado = item.cantidad * item.costoUnitarioPPP;
                    return (
                      <tr key={item.id} className="hover:bg-[#FFFDF9] transition-colors">
                        <td className="py-3 font-medium text-[#231610]">
                          {item.nombre}
                          <span className="block text-xs text-[#7D7068] font-normal">Costo base según última factura ingresada</span>
                        </td>
                        <td className="py-3 text-right">
                          <span className="font-semibold text-[#231610]">
                            {item.cantidad} {item.unidad}
                          </span>
                        </td>
                        <td className="py-3 text-right text-[#7D7068]">
                          ${item.costoUnitarioPPP.toLocaleString('es-CL')} / {item.unidad}
                        </td>
                        <td className="py-3 text-right font-semibold text-[#231610]">
                          ${costoCalculado.toLocaleString('es-CL', { maximumFractionDigits: 0 })}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
                <tfoot>
                  <tr className="border-t border-[#E8DFD5] text-[#7D7068]">
                    <td colSpan={3} className="pt-3 text-right text-xs">Subtotal Ingredientes:</td>
                    <td className="pt-3 text-right font-medium text-[#231610]">${costoInsumosNeto.toLocaleString('es-CL')}</td>
                  </tr>
                  <tr className="text-[#7D7068]">
                    <td colSpan={3} className="py-1 text-right text-xs">+ Merma Técnica de Cocción ({mermaGlobalPorcentaje}%):</td>
                    <td className="py-1 text-right font-medium text-[#C86D74]">+${costoMermaGlobal.toLocaleString('es-CL', { maximumFractionDigits: 0 })}</td>
                  </tr>
                  <tr className="text-[#7D7068]">
                    <td colSpan={3} className="py-1 text-right text-xs">+ Packaging y Caja de Lujo:</td>
                    <td className="py-1 text-right font-medium text-[#231610]">${empaqueCosto.toLocaleString('es-CL')}</td>
                  </tr>
                  <tr className="text-base font-semibold text-[#231610] border-t border-[#E8DFD5]">
                    <td colSpan={3} className="pt-3 text-right">Costo Total de la Preparación:</td>
                    <td className="pt-3 text-right text-[#231610]">${costoTotalBatch.toLocaleString('es-CL', { maximumFractionDigits: 0 })}</td>
                  </tr>
                </tfoot>
              </table>
            </div>

            {/* Botón interactivo de simulación de compra */}
            <div className="mt-8 pt-4 border-t border-[#E8DFD5] flex items-center justify-between">
              <span className="text-xs text-[#7D7068]">
                💡 Prueba cómo impacta el precio de los ingredientes en tu margen:
              </span>
              <button
                type="button"
                onClick={handleSimularFacturaProveedor}
                className={`text-xs font-semibold px-4 py-2 rounded-lg border transition-all ${
                  facturaSimuladaAplicada
                    ? 'bg-amber-100 text-amber-900 border-amber-300'
                    : 'bg-[#FFF9F2] text-[#231610] border-[#E8DFD5] hover:bg-[#F7EEE3]'
                }`}
              >
                {facturaSimuladaAplicada
                  ? '↺ Restaurar Costos de Insumos Base'
                  : '⚡ Simular Alza en Factura (Mantequilla +$1.000)'}
              </button>
            </div>
          </div>
        </div>

        {/* Columna Derecha: Tarjeta de Rentabilidad y Margen en Tiempo Real */}
        <div className="space-y-6">
          <div className="bg-white rounded-2xl border border-[#E8DFD5] p-6 shadow-sm sticky top-8">
            <span className="text-xs uppercase tracking-widest text-[#D4AF37] font-semibold block mb-2">
              Análisis Económico
            </span>
            <h3 className="font-serif text-2xl text-[#231610] mb-6">Rentabilidad de Vitrina</h3>

            {/* Input de Precio de Venta */}
            <div className="mb-6">
              <label className="text-xs text-[#7D7068] font-semibold uppercase block mb-1">
                Precio de Venta al Cliente (CLP)
              </label>
              <div className="relative">
                <span className="absolute left-3 top-2.5 text-sm text-[#7D7068] font-semibold">$</span>
                <input
                  type="number"
                  step="500"
                  value={precioVentaNeto}
                  onChange={(e) => setPrecioVentaNeto(parseFloat(e.target.value) || 0)}
                  className="w-full pl-7 pr-3 py-2 text-lg rounded-xl border border-[#E8DFD5] text-[#231610] font-serif font-semibold focus:ring-2 focus:ring-[#D4AF37] outline-none"
                />
              </div>
              <p className="text-xs text-[#7D7068] mt-1">Precio actual en catálogo web y mostrador</p>
            </div>

            {/* Desglose de Resultados */}
            <div className="space-y-3 text-sm pb-6 border-b border-[#F7EEE3]">
              <div className="flex justify-between text-[#7D7068]">
                <span>Costo Total Elaboración:</span>
                <span className="font-semibold text-[#231610]">${costoTotalBatch.toLocaleString('es-CL', { maximumFractionDigits: 0 })}</span>
              </div>
              <div className="flex justify-between text-[#7D7068]">
                <span>Costo Unitario por Porción:</span>
                <span className="font-semibold text-[#231610]">${costoPorPorcion.toLocaleString('es-CL', { maximumFractionDigits: 0 })}</span>
              </div>
              <div className="flex justify-between text-[#7D7068]">
                <span>Margen Bruto en Dinero:</span>
                <span className={`font-semibold ${margenBrutoMonto >= 0 ? 'text-emerald-700' : 'text-rose-700'}`}>
                  ${margenBrutoMonto.toLocaleString('es-CL', { maximumFractionDigits: 0 })}
                </span>
              </div>
            </div>

            {/* Gauge / Indicador de Porcentaje */}
            <div className="pt-6">
              <div className="flex justify-between items-end mb-2">
                <span className="text-xs uppercase tracking-wider font-semibold text-[#7D7068]">Porcentaje de Margen</span>
                <span className={`text-2xl font-serif font-bold ${esMargenBajo ? 'text-rose-700' : 'text-emerald-700'}`}>
                  {margenBrutoPorcentaje.toFixed(1)}%
                </span>
              </div>

              {/* Barra de progreso visual */}
              <div className="w-full bg-[#F7EEE3] h-3 rounded-full overflow-hidden">
                <div
                  className={`h-full transition-all duration-500 rounded-full ${
                    esMargenBajo ? 'bg-rose-500' : 'bg-emerald-600'
                  }`}
                  style={{ width: `${Math.min(100, Math.max(0, margenBrutoPorcentaje))}%` }}
                />
              </div>

              {/* Alerta de margen bajo */}
              {esMargenBajo ? (
                <div className="mt-4 p-3 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-800 flex items-start gap-2">
                  <span>⚠️</span>
                  <div>
                    <span className="font-semibold block">Alerta: Margen por debajo del 50%</span>
                    El costo de los insumos compromete tu rentabilidad. Te sugerimos subir el precio a{' '}
                    <strong className="underline">
                      ${Math.ceil((costoTotalBatch * 2) / 1000) * 1000} CLP
                    </strong>{' '}
                    para alcanzar el 50% de ganancia.
                  </div>
                </div>
              ) : (
                <div className="mt-4 p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-xs text-emerald-800 flex items-start gap-2">
                  <span>✅</span>
                  <div>
                    <span className="font-semibold block">Margen Saludable (&gt; 50%)</span>
                    Esta preparación cubre holgadamente costos fijos, mano de obra y deja excelente margen para el taller.
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
