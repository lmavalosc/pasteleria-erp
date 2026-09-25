import React from 'react';
import { theme } from '../theme';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'gold' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  children: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  isLoading = false,
  leftIcon,
  rightIcon,
  children,
  className = '',
  disabled,
  style,
  ...props
}) => {
  const baseStyle: React.CSSProperties = {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    fontFamily: theme.fonts.body,
    fontWeight: 600,
    borderRadius: theme.radii.full,
    cursor: disabled || isLoading ? 'not-allowed' : 'pointer',
    opacity: disabled || isLoading ? 0.65 : 1,
    transition: 'all 0.25s cubic-bezier(0.16, 1, 0.3, 1)',
    border: '1px solid transparent',
    outline: 'none',
    textDecoration: 'none',
    letterSpacing: '0.02em',
  };

  const sizeStyles: Record<string, React.CSSProperties> = {
    sm: { padding: '6px 14px', fontSize: '0.85rem' },
    md: { padding: '10px 22px', fontSize: '0.95rem' },
    lg: { padding: '14px 30px', fontSize: '1.05rem' },
  };

  const variantStyles: Record<string, React.CSSProperties> = {
    primary: {
      backgroundColor: theme.colors.primary.rose,
      color: '#FFFFFF',
      boxShadow: '0 4px 14px rgba(200, 109, 116, 0.25)',
    },
    gold: {
      backgroundColor: theme.colors.primary.gold,
      color: '#231610',
      boxShadow: theme.shadows.goldGlow,
      fontWeight: 700,
    },
    secondary: {
      backgroundColor: theme.colors.neutral.cocoa,
      color: '#FFF9F2',
      boxShadow: '0 4px 14px rgba(35, 22, 16, 0.2)',
    },
    outline: {
      backgroundColor: 'transparent',
      borderColor: theme.colors.neutral.border,
      color: theme.colors.neutral.textMain,
    },
    ghost: {
      backgroundColor: 'transparent',
      color: theme.colors.primary.rose,
    },
  };

  return (
    <button
      disabled={disabled || isLoading}
      style={{
        ...baseStyle,
        ...sizeStyles[size],
        ...variantStyles[variant],
        ...style,
      }}
      className={`pasteleria-btn pasteleria-btn-${variant} ${className}`}
      {...props}
    >
      {isLoading ? (
        <span style={{ display: 'inline-block', animation: 'spin 1s linear infinite' }}>⌛</span>
      ) : (
        leftIcon
      )}
      {children}
      {!isLoading && rightIcon}
    </button>
  );
};
