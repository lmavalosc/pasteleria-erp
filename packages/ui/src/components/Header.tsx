import React from 'react';
import { theme } from '../theme';
import { Button } from './Button';

export interface HeaderProps {
  cartCount?: number;
  onOpenCart?: () => void;
  brandName?: string;
}

export const Header: React.FC<HeaderProps> = ({
  cartCount = 0,
  onOpenCart,
  brandName = 'Maison du Délice',
}) => {
  return (
    <header
      style={{
        position: 'sticky',
        top: 0,
        zIndex: 50,
        backgroundColor: 'rgba(255, 249, 242, 0.92)',
        backdropFilter: 'blur(12px)',
        borderBottom: `1px solid ${theme.colors.neutral.border}`,
        padding: '16px 24px',
        transition: 'all 0.3s ease',
      }}
    >
      <div
        style={{
          maxWidth: '1200px',
          margin: '0 auto',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        {/* Brand Logo */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', textDecoration: 'none' }}>
          <span style={{ fontSize: '1.8rem', lineHeight: 1 }}>🍰</span>
          <div>
            <span
              style={{
                fontFamily: theme.fonts.heading,
                fontSize: '1.45rem',
                fontWeight: 700,
                color: theme.colors.neutral.cocoa,
                letterSpacing: '-0.02em',
                display: 'block',
              }}
            >
              {brandName}
            </span>
            <span
              style={{
                fontFamily: theme.fonts.body,
                fontSize: '0.68rem',
                letterSpacing: '0.18em',
                textTransform: 'uppercase',
                color: theme.colors.primary.goldDark,
                fontWeight: 600,
                display: 'block',
              }}
            >
              Haute Pâtisserie & Boulangerie
            </span>
          </div>
        </div>

        {/* Navigation links */}
        <nav style={{ display: 'flex', alignItems: 'center', gap: '28px' }}>
          <a
            href="#catalogo"
            style={{
              fontFamily: theme.fonts.body,
              color: theme.colors.neutral.textMain,
              textDecoration: 'none',
              fontSize: '0.92rem',
              fontWeight: 500,
            }}
          >
            Colección
          </a>
          <a
            href="#personalizados"
            style={{
              fontFamily: theme.fonts.body,
              color: theme.colors.neutral.textMain,
              textDecoration: 'none',
              fontSize: '0.92rem',
              fontWeight: 500,
            }}
          >
            Pasteles a Medida
          </a>
          <a
            href="#artesanos"
            style={{
              fontFamily: theme.fonts.body,
              color: theme.colors.neutral.textMain,
              textDecoration: 'none',
              fontSize: '0.92rem',
              fontWeight: 500,
            }}
          >
            Taller & Chef
          </a>
        </nav>

        {/* Action / Cart */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <Button
            variant="gold"
            size="sm"
            onClick={onOpenCart}
            leftIcon={<span>🛒</span>}
          >
            Bolsa ({cartCount})
          </Button>
        </div>
      </div>
    </header>
  );
};
