import React from 'react';
import { theme } from '../theme';

export interface PriceTagProps {
  price: number;
  discountedPrice?: number;
  currency?: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const PriceTag: React.FC<PriceTagProps> = ({
  price,
  discountedPrice,
  currency = '€',
  size = 'md',
  className = '',
}) => {
  const fontSizes = {
    sm: { main: '1rem', strike: '0.8rem' },
    md: { main: '1.25rem', strike: '0.95rem' },
    lg: { main: '1.65rem', strike: '1.15rem' },
  };

  const hasDiscount = discountedPrice !== undefined && discountedPrice < price;

  return (
    <div
      className={`pasteleria-pricetag ${className}`}
      style={{
        display: 'inline-flex',
        alignItems: 'baseline',
        gap: '6px',
        fontFamily: theme.fonts.body,
      }}
    >
      {hasDiscount ? (
        <>
          <span
            style={{
              fontSize: fontSizes[size].main,
              fontWeight: 700,
              color: theme.colors.primary.rose,
            }}
          >
            {discountedPrice.toFixed(2)} {currency}
          </span>
          <span
            style={{
              fontSize: fontSizes[size].strike,
              textDecoration: 'line-through',
              color: theme.colors.neutral.textMuted,
            }}
          >
            {price.toFixed(2)} {currency}
          </span>
        </>
      ) : (
        <span
          style={{
            fontSize: fontSizes[size].main,
            fontWeight: 700,
            color: theme.colors.neutral.cocoa,
          }}
        >
          {price.toFixed(2)} {currency}
        </span>
      )}
    </div>
  );
};
