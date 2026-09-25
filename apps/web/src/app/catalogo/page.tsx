import Link from 'next/link';
import { theme } from '@pasteleria/ui';

export default function CatalogPage() {
  return (
    <div className="max-w-6xl mx-auto px-4 py-12">
      <div className="flex items-center justify-between mb-8 pb-4 border-b border-[#E8DFD5]">
        <div>
          <span className="text-xs uppercase tracking-widest text-[#D4AF37] font-semibold">Haute Pâtisserie</span>
          <h1 className="text-3xl font-serif text-[#231610] mt-1">Catálogo de Alta Repostería</h1>
        </div>
        <Link 
          href="/"
          className="text-sm font-medium text-[#231610] hover:text-[#D4AF37] transition-colors"
        >
          ← Volver al Inicio
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[
          { name: 'Ópera Clásica de París', price: '$18.500', desc: 'Bizcocho joconde, ganache de chocolate 70% y crema de mantequilla al café.' },
          { name: 'Tarta de Frambuesas & Pistacho', price: '$16.900', desc: 'Masa sablée crujiente, frangipane de pistacho de Sicilia y frambuesas frescas.' },
          { name: 'Eclair de Vainilla Bourbon', price: '$4.200', desc: 'Pasta choux horneada al punto, cremosa vainilla de Madagascar y glaseado fino.' }
        ].map((item, idx) => (
          <div key={idx} className="bg-white rounded-xl p-6 border border-[#E8DFD5] shadow-sm hover:shadow-md transition-shadow">
            <div className="h-44 bg-[#F7EEE3] rounded-lg mb-4 flex items-center justify-center text-[#D4AF37] font-serif text-lg">
              [Foto de Alta Repostería]
            </div>
            <h3 className="text-xl font-serif text-[#231610]">{item.name}</h3>
            <p className="text-sm text-[#7D7068] mt-2 mb-4 leading-relaxed">{item.desc}</p>
            <div className="flex items-center justify-between pt-3 border-t border-[#F7EEE3]">
              <span className="font-semibold text-lg text-[#231610]">{item.price}</span>
              <button className="px-4 py-2 bg-[#231610] text-[#FFF9F2] text-xs uppercase tracking-wider rounded-md hover:bg-[#D4AF37] transition-colors">
                Solicitar
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
