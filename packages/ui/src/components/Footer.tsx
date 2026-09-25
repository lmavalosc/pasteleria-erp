import React from 'react';
import { theme } from '../theme';

export const Footer: React.FC = () => {
  return (
    <footer
      style={{
        backgroundColor: theme.colors.neutral.cocoa,
        color: '#FFF9F2',
        padding: '60px 24px 30px',
        borderTop: `1px solid rgba(212, 175, 55, 0.25)`,
        marginTop: '80px',
      }}
    >
      <div
        style={{
          maxWidth: '1200px',
          margin: '0 auto',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
          gap: '40px',
          marginBottom: '50px',
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
            <span style={{ fontSize: '1.8rem' }}>🍰</span>
            <span style={{ fontFamily: theme.fonts.heading, fontSize: '1.4rem', fontWeight: 700, color: theme.colors.primary.goldLight }}>
              Maison du Délice
            </span>
          </div>
          <p style={{ color: '#D2C5BD', fontSize: '0.9rem', lineHeight: 1.6 }}>
            Alta repostería francesa y pastelería contemporánea elaborada a mano diariamente con mantequilla AOP, chocolates Grand Cru y frutas frescas de temporada.
          </p>
        </div>

        <div>
          <h4 style={{ fontFamily: theme.fonts.heading, color: theme.colors.primary.gold, fontSize: '1.1rem', marginBottom: '16px' }}>
            Horario Boutique & Taller
          </h4>
          <p style={{ color: '#D2C5BD', fontSize: '0.88rem', lineHeight: 1.8, margin: 0 }}>
            Lunes a Sábado: 08:30 – 20:30<br />
            Domingos y Festivos: 09:00 – 15:00<br />
            Pedidos Especiales: Con 48h de antelación
          </p>
        </div>

        <div>
          <h4 style={{ fontFamily: theme.fonts.heading, color: theme.colors.primary.gold, fontSize: '1.1rem', marginBottom: '16px' }}>
            Atelier & Retiros
          </h4>
          <p style={{ color: '#D2C5BD', fontSize: '0.88rem', lineHeight: 1.8, margin: 0 }}>
            Avenida de los Maestros Pasteleros, 14<br />
            Tel: +34 912 345 678<br />
            Email: atelier@maisondudelice.com
          </p>
        </div>

        <div>
          <h4 style={{ fontFamily: theme.fonts.heading, color: theme.colors.primary.gold, fontSize: '1.1rem', marginBottom: '16px' }}>
            Compromiso & Calidad
          </h4>
          <p style={{ color: '#D2C5BD', fontSize: '0.88rem', lineHeight: 1.6, margin: 0 }}>
            Sin conservantes artificiales ni aditivos sintéticos. Ingredientes orgánicos certificados y comercio justo de cacao.
          </p>
        </div>
      </div>

      <div
        style={{
          maxWidth: '1200px',
          margin: '0 auto',
          paddingTop: '24px',
          borderTop: '1px solid rgba(255, 255, 255, 0.1)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '12px',
          fontSize: '0.82rem',
          color: '#A99B92',
        }}
      >
        <span>© {new Date().getFullYear()} Maison du Délice Pâtisserie. Todos los derechos reservados.</span>
        <span>Monorepo Turborepo · Web (Next.js 14) + Mobile (Expo)</span>
      </div>
    </footer>
  );
};
