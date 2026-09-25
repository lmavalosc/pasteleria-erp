import React from 'react';
import { theme } from '../theme';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  hoverable?: boolean;
  bordered?: boolean;
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

export const Card: React.FC<CardProps> = ({
  children,
  hoverable = true,
  bordered = true,
  padding = 'md',
  className = '',
  style,
  ...props
}) => {
  const paddings = {
    none: '0',
    sm: '12px',
    md: '20px',
    lg: '32px',
  };

  return (
    <div
      className={`pasteleria-card ${hoverable ? 'hoverable' : ''} ${className}`}
      style={{
        backgroundColor: theme.colors.neutral.white,
        borderRadius: theme.radii.lg,
        border: bordered ? `1px solid ${theme.colors.neutral.border}` : 'none',
        boxShadow: theme.shadows.card,
        padding: paddings[padding],
        transition: 'transform 0.3s ease, box-shadow 0.3s ease',
        overflow: 'hidden',
        ...style,
      }}
      {...props}
    >
      {children}
    </div>
  );
};
