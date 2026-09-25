'use client';

import React, { useState } from 'react';
import Link from 'next/link';

interface InsumoDetalleForm {
  nombre: string;
  cantidad: number;
  unidad: string;
  precioUnitario: number;
}

export default function GastosPage() {
  const [proveedor, setProveedor] = useState('Molino Central SpA');
  const [folio, setFolio] = useState('FAC-8842');
  const [categoria, setCategoria] = useState('materias_primas');
  const [metodoPago, setMetodoPago] = useState('transferencia');
  
  // Lista de insumos adquiridos en la factura
  const [insumos, setInsumos] = useState<InsumoDetalleForm[]>([
    { nombre: 'Harina Pastelera T55', cantidad: 25, unidad: 'kg', precioUnitario: 1000 },
    { nombre: 'Mantequilla 82% MG', cantidad: 10, unidad: 'kg', precioUnitario: 7500 },
  ]);

  const [nuevoInsumoNombre, setNuevoInsumoNombre] = useState('');
  const [nuevoInsumoCantidad, setNuevoInsumoCantidad] = useState(1);
  const [nuevoInsumoUnidad, setNuevoInsumoUnidad] = useState('kg');
  const [nuevoInsumoPrecio, setNuevoInsumoPrecio] = useState(5000);

  const [gastosRegistrados, setGastosRegistrados] = useState([
    {
      id: 'gasto-1',
      fecha: '2026-09-25',
      proveedor: 'Molino Central SpA',
      folio: 'FAC-8842',
      categoria: 'Materias Primas',
      montoNeto: 100000,
      montoIva: 19000,
      montoTotal: 119000,
      estado: 'Aprobado',
      detalle: '25 kg Harina ($25.000) + 10 kg Mantequilla ($75.000)',
    },
    {
      id: 'gasto-2',
      fecha: '2026-09-24',
      proveedor: 'Packaging Gourmet Chile',
      folio: 'BOL-1102',
      categoria: 'Packaging',
      montoNeto: 45000,
      montoIva: 8550,
      montoTotal: 53550,
      estado: 'Aprobado',
      detalle: '100 Cajas de lujo para tortas medianas',
    },
  ]);

  const [mensajeExito, setMensajeExito] = useState(false);

  // Cálculos de la factura actual
  const montoNeto = insumos.reduce((acc, item) => acc + item.cantidad * item.precioUnitario, 0);
  const montoIva = Math.round(montoNeto * 0.19);
  const montoTotal = montoNeto + montoIva;

  const agregarInsumo = () => {
    if (!nuevoInsumoNombre.trim()) return;
    setInsumos([
      ...insumos,
      {
        nombre: nuevoInsumoNombre,
        cantidad: nuevoInsumoCantidad,
        unidad: nuevoInsumoUnidad,
        precioUnitario: nuevoInsumoPrecio,
      },
    ]);
    setNuevoInsumoNombre('');
    setNuevoInsumoCantidad(1);
    setNuevoInsumoPrecio(5000);
  };

  const eliminarInsumo = (index: number) => {
    setInsumos(insumos.filter((_, i) => i !== index));
  };

  const handleRegistrarFactura = (e: React.FormEvent) => {
    e.preventDefault();
    if (insumos.length === 0) return;

    const resumenDetalle = insumos.map((i) => `${i.cantidad} ${i.unidad} ${i.nombre}`).join(' + ');

    const nuevoGasto = {
      id: `gasto-${Date.now()}`,
      fecha: new Date().toISOString().split('T')[0],
      proveedor,
      folio,
      categoria: categoria === 'materias_primas' ? 'Materias Primas' : 'Servicios',
      montoNeto,
      montoIva,
      montoTotal,
      estado: 'Pendiente Aprobación',
      detalle: resumenDetalle,
    };

    setGastosRegistrados([nuevoGasto, ...gastosRegistrados]);
    setMensajeExito(true);
    setTimeout(() => setMensajeExito(false), 4000);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 pb-6 border-b border-[#E8DFD5] gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs uppercase tracking-widest text-[#C86D74] font-semibold">Administración & Finanzas</span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-rose-50 text-rose-800 border border-rose-200">
              Egresos con Insumos
            </span>
          </div>
          <h1 className="text-3xl font-serif text-[#231610] mt-1">Facturas de Proveedor & Materias Primas</h1>
          <p className="text-sm text-[#7D7068] mt-1">
            Cada insumo registrado actualiza automáticamente el Precio Promedio Ponderado (PPP) para costear tus recetas.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            href="/admin/recetas"
            className="text-xs font-semibold px-4 py-2.5 rounded-lg bg-[#231610] text-[#FFF9F2] hover:bg-[#3D271D] transition-colors"
          >
            🍰 Ir al Escandallo de Recetas →
          </Link>
        </div>
      </div>

      {mensajeExito && (
        <div className="mb-6 p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-sm flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span>✅</span>
            <span>
              <strong>¡Factura registrada con éxito!</strong> Los insumos fueron ingresados y el costo promedio de tus recetas ya fue recalculado.
            </span>
          </div>
          <Link href="/admin/recetas" className="text-xs font-semibold underline text-emerald-900">
            Ver impacto en recetas
          </Link>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-10">
        {/* Formulario de Carga */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-[#E8DFD5] p-6 shadow-sm">
          <h2 className="text-xl font-serif text-[#231610] mb-4">Ingreso de Factura / Boleta de Compra</h2>
          <form onSubmit={handleRegistrarFactura} className="space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-semibold uppercase text-[#7D7068] block mb-1">Proveedor</label>
                <input
                  type="text"
                  value={proveedor}
                  onChange={(e) => setProveedor(e.target.value)}
                  className="w-full px-3 py-2 text-sm rounded-lg border border-[#E8DFD5] text-[#231610] focus:ring-1 focus:ring-[#D4AF37] outline-none"
                  required
                />
              </div>
              <div>
                <label className="text-xs font-semibold uppercase text-[#7D7068] block mb-1">Folio / Número Factura</label>
                <input
                  type="text"
                  value={folio}
                  onChange={(e) => setFolio(e.target.value)}
                  className="w-full px-3 py-2 text-sm rounded-lg border border-[#E8DFD5] text-[#231610] focus:ring-1 focus:ring-[#D4AF37] outline-none"
                  required
                />
              </div>
            </div>

            {/* Insumos Adquiridos */}
            <div className="border-t border-[#F7EEE3] pt-4">
              <div className="flex items-center justify-between mb-3">
                <label className="text-xs font-semibold uppercase text-[#7D7068] tracking-wider">
                  Materias Primas e Insumos en la Factura
                </label>
                <span className="text-xs text-amber-700 font-medium bg-amber-50 px-2 py-0.5 rounded">
                  Impacta costo en tiempo real
                </span>
              </div>

              {/* Lista actual de insumos */}
              <div className="space-y-2 mb-4">
                {insumos.map((item, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-3 rounded-lg bg-[#FFF9F2] border border-[#E8DFD5] text-sm"
                  >
                    <div>
                      <span className="font-medium text-[#231610]">{item.nombre}</span>
                      <span className="text-xs text-[#7D7068] ml-2">
                        ({item.cantidad} {item.unidad} × ${item.precioUnitario.toLocaleString('es-CL')})
                      </span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="font-semibold text-[#231610]">
                        ${(item.cantidad * item.precioUnitario).toLocaleString('es-CL')}
                      </span>
                      <button
                        type="button"
                        onClick={() => eliminarInsumo(index)}
                        className="text-rose-600 hover:text-rose-800 text-xs font-bold px-2 py-1"
                      >
                        ✕
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              {/* Agregar nuevo insumo */}
              <div className="p-4 bg-[#FBF8F5] rounded-xl border border-dashed border-[#E8DFD5] grid grid-cols-1 sm:grid-cols-5 gap-3 items-end">
                <div className="sm:col-span-2">
                  <label className="text-xs text-[#7D7068] block mb-1">Insumo</label>
                  <input
                    type="text"
                    placeholder="Ej: Chocolate 70%, Vainilla..."
                    value={nuevoInsumoNombre}
                    onChange={(e) => setNuevoInsumoNombre(e.target.value)}
                    className="w-full px-3 py-1.5 text-xs rounded-lg border border-[#E8DFD5] bg-white text-[#231610]"
                  />
                </div>
                <div>
                  <label className="text-xs text-[#7D7068] block mb-1">Cantidad</label>
                  <input
                    type="number"
                    min="0.1"
                    step="0.1"
                    value={nuevoInsumoCantidad}
                    onChange={(e) => setNuevoInsumoCantidad(parseFloat(e.target.value) || 0)}
                    className="w-full px-3 py-1.5 text-xs rounded-lg border border-[#E8DFD5] bg-white text-[#231610]"
                  />
                </div>
                <div>
                  <label className="text-xs text-[#7D7068] block mb-1">Precio Unit. ($)</label>
                  <input
                    type="number"
                    step="100"
                    value={nuevoInsumoPrecio}
                    onChange={(e) => setNuevoInsumoPrecio(parseFloat(e.target.value) || 0)}
                    className="w-full px-3 py-1.5 text-xs rounded-lg border border-[#E8DFD5] bg-white text-[#231610]"
                  />
                </div>
                <div>
                  <button
                    type="button"
                    onClick={agregarInsumo}
                    className="w-full py-1.5 px-3 bg-[#231610] text-[#FFF9F2] text-xs font-semibold rounded-lg hover:bg-[#3D271D]"
                  >
                    + Agregar
                  </button>
                </div>
              </div>
            </div>

            {/* Totales y Envío */}
            <div className="border-t border-[#F7EEE3] pt-4 flex flex-col sm:flex-row items-center justify-between gap-4">
              <div className="text-sm">
                <span className="text-[#7D7068]">Neto: </span>
                <span className="font-semibold text-[#231610] mr-4">${montoNeto.toLocaleString('es-CL')}</span>
                <span className="text-[#7D7068]">IVA (19%): </span>
                <span className="font-semibold text-[#231610] mr-4">${montoIva.toLocaleString('es-CL')}</span>
                <span className="text-[#7D7068]">Total: </span>
                <span className="font-bold text-[#C86D74] text-base">${montoTotal.toLocaleString('es-CL')}</span>
              </div>
              <button
                type="submit"
                disabled={insumos.length === 0}
                className="w-full sm:w-auto px-6 py-2.5 rounded-lg bg-[#C86D74] text-white font-semibold text-sm hover:bg-[#b0585f] transition-colors disabled:opacity-50"
              >
                💾 Guardar Factura y Actualizar Costos
              </button>
            </div>
          </form>
        </div>

        {/* Bóveda y Comprobante */}
        <div className="space-y-6">
          <div className="bg-white rounded-2xl border border-[#E8DFD5] p-6 shadow-sm">
            <h3 className="text-sm font-semibold uppercase text-[#7D7068] mb-3">Adjuntar Documento Digital</h3>
            <div className="border-2 border-dashed border-[#E8DFD5] rounded-xl p-6 text-center bg-[#FFF9F2] hover:bg-[#F7EEE3] transition-colors cursor-pointer">
              <div className="text-2xl mb-2">📄</div>
              <p className="text-xs font-medium text-[#231610]">Factura_Molino_Central_8842.pdf</p>
              <p className="text-[11px] text-[#7D7068] mt-1">Hash SHA-256 verificado en bóveda segura</p>
              <span className="inline-block mt-3 text-[10px] bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded">
                ✓ Documento Vinculado
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Historial de Gastos */}
      <div className="bg-white rounded-2xl border border-[#E8DFD5] overflow-hidden shadow-sm">
        <div className="px-6 py-4 border-b border-[#E8DFD5] bg-[#FFF9F2] flex items-center justify-between">
          <h3 className="font-serif text-[#231610] font-medium">Facturas y Gastos en el Libro de Compras</h3>
          <span className="text-xs bg-[#F7EEE3] text-[#7D7068] px-2.5 py-1 rounded-full">Filtrado por Tenant Activo</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-[#FFF9F2] text-[#7D7068] border-b border-[#E8DFD5] text-xs uppercase tracking-wider">
              <tr>
                <th className="px-6 py-3 font-semibold">Fecha</th>
                <th className="px-6 py-3 font-semibold">Proveedor & Folio</th>
                <th className="px-6 py-3 font-semibold">Detalle de Insumos</th>
                <th className="px-6 py-3 font-semibold text-right">Total Factura</th>
                <th className="px-6 py-3 font-semibold text-center">Estado</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E8DFD5]">
              {gastosRegistrados.map((g) => (
                <tr key={g.id} className="hover:bg-[#FFFDF9] transition-colors">
                  <td className="px-6 py-4 text-[#7D7068]">{g.fecha}</td>
                  <td className="px-6 py-4">
                    <span className="font-medium text-[#231610] block">{g.proveedor}</span>
                    <span className="text-xs text-[#7D7068]">{g.folio}</span>
                  </td>
                  <td className="px-6 py-4 text-xs text-[#7D7068] max-w-xs">{g.detalle}</td>
                  <td className="px-6 py-4 font-semibold text-[#231610] text-right">
                    ${g.montoTotal.toLocaleString('es-CL')} CLP
                  </td>
                  <td className="px-6 py-4 text-center">
                    <span className="px-2.5 py-1 text-xs rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
                      {g.estado}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
