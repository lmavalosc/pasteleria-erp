import React from 'react';
import { theme } from '../theme';

export interface BadgeProps {
  variant?: 'gold' | 'rose' | 'vegan' | 'glutenFree' | 'cocoa' | 'default';
  children: React.ReactNode;
  size?: 'sm' | 'md';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  variant = 'default',
  children,
  size = 'md',
  className = '',
}) => {
  const variantStyles: Record<string, React.CSSProperties> = {
    gold: {
      backgroundColor: theme.colors.primary.goldLight,
      color: theme.colors.primary.goldDark,
      border: `1px solid ${theme.colors.primary.gold}`,
    },
    rose: {
      backgroundColor: theme.colors.primary.roseLight,
      color: theme.colors.primary.roseDark,
      border: `1px solid ${theme.colors.primary.rose}`,
    },
    vegan: {
      backgroundColor: '#E8F5E9',
      color: '#2E7D32',
      border: '1px solid #A5D6A7',
    },
    glutenFree: {
      backgroundColor: '#FFF3E0',
      color: '#E65100',
      border: '1px solid #FFCC80',
    },
    cocoa: {
      backgroundColor: theme.colors.neutral.creamDark,
      color: theme.colors.neutral.cocoa,
      border: `1px solid ${theme.colors.neutral.border}`,
    },
    default: {
      backgroundColor: '#F3F4F6',
      color: '#374151',
      border: '1px solid #E5E7EB',
    },
  };

  const sizeStyles: Record<string, React.CSSProperties> = {
    sm: { padding: '2px 8px', fontSize: '0.72rem' },
    md: { padding: '4px 12px', fontSize: '0.8rem' },
  };

  return (
    <span
      className={`pasteleria-badge ${className}`}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '4px',
        fontWeight: 600,
        borderRadius: theme.radii.full,
        fontFamily: theme.fonts.body,
        letterSpacing: '0.03em',
        textTransform: 'uppercase',
        ...sizeStyles[size],
        ...variantStyles[variant],
      }}
    >
      {children}
    </span>
  );
};
