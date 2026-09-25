import React from 'react';
import { theme } from '../theme';

export interface RatingStarsProps {
  rating: number;
  reviewsCount?: number;
  showScore?: boolean;
}

export const RatingStars: React.FC<RatingStarsProps> = ({
  rating,
  reviewsCount,
  showScore = true,
}) => {
  const fullStars = Math.floor(rating);
  const hasHalf = rating % 1 >= 0.5;

  return (
    <div
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '4px',
        fontSize: '0.85rem',
        fontFamily: theme.fonts.body,
      }}
    >
      <div style={{ color: theme.colors.primary.gold, display: 'inline-flex', gap: '2px' }}>
        {[...Array(5)].map((_, i) => {
          if (i < fullStars) {
            return <span key={i}>★</span>;
          }
          if (i === fullStars && hasHalf) {
            return <span key={i}>★</span>;
          }
          return (
            <span key={i} style={{ color: theme.colors.neutral.border }}>
              ★
            </span>
          );
        })}
      </div>
      {showScore && (
        <span style={{ fontWeight: 600, color: theme.colors.neutral.textMain, marginLeft: '2px' }}>
          {rating.toFixed(1)}
        </span>
      )}
      {reviewsCount !== undefined && (
        <span style={{ color: theme.colors.neutral.textMuted, fontSize: '0.78rem' }}>
          ({reviewsCount})
        </span>
      )}
    </div>
  );
};
