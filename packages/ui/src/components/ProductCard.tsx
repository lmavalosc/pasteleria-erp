import React from 'react';
import { Card } from './Card';
import { Badge } from './Badge';
import { PriceTag } from './PriceTag';
import { RatingStars } from './RatingStars';
import { Button } from './Button';
import { theme } from '../theme';

export interface Product {
  id?: string;
  name: string;
  description?: string;
  tagline?: string;
  price: number;
  discountedPrice?: number;
  images: string[];
  featured?: boolean;
  isGlutenFree?: boolean;
  isVegan?: boolean;
  rating: number;
  reviewsCount?: number;
}

export interface ProductCardProps {
  product: Product;
  onAddToCart?: (product: Product) => void;
  onSelect?: (product: Product) => void;
}

export const ProductCard: React.FC<ProductCardProps> = ({
  product,
  onAddToCart,
  onSelect,
}) => {
  return (
    <Card
      padding="none"
      onClick={() => onSelect?.(product)}
      style={{
        display: 'flex',
        flexDirection: 'column',
        cursor: onSelect ? 'pointer' : 'default',
        position: 'relative',
        height: '100%',
      }}
    >
      {/* Product Image Container */}
      <div
        style={{
          position: 'relative',
          width: '100%',
          paddingTop: '75%', // 4:3 Aspect Ratio
          overflow: 'hidden',
          backgroundColor: theme.colors.neutral.creamDark,
        }}
      >
        <img
          src={product.images[0] || 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=800&q=80'}
          alt={product.name}
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            transition: 'transform 0.5s ease',
          }}
          className="product-img-hover"
        />

        {/* Badges Overlay */}
        <div
          style={{
            position: 'absolute',
            top: '12px',
            left: '12px',
            display: 'flex',
            flexDirection: 'column',
            gap: '6px',
            zIndex: 2,
          }}
        >
          {product.featured && <Badge variant="gold" size="sm">★ Autor</Badge>}
          {product.isGlutenFree && <Badge variant="glutenFree" size="sm">Sin Gluten</Badge>}
          {product.isVegan && <Badge variant="vegan" size="sm">Vegano</Badge>}
        </div>
      </div>

      {/* Product Content */}
      <div
        style={{
          padding: '20px',
          display: 'flex',
          flexDirection: 'column',
          flexGrow: 1,
          justifyContent: 'space-between',
          gap: '12px',
        }}
      >
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
            <RatingStars rating={product.rating} reviewsCount={product.reviewsCount} />
          </div>

          <h3
            style={{
              fontFamily: theme.fonts.heading,
              fontSize: '1.2rem',
              color: theme.colors.neutral.cocoa,
              margin: '0 0 6px 0',
              fontWeight: 600,
              lineHeight: 1.3,
            }}
          >
            {product.name}
          </h3>

          <p
            style={{
              fontFamily: theme.fonts.body,
              fontSize: '0.88rem',
              color: theme.colors.neutral.textMuted,
              margin: 0,
              lineHeight: 1.45,
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical',
              overflow: 'hidden',
            }}
          >
            {product.tagline || product.description}
          </p>
        </div>

        {/* Price & Action */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            paddingTop: '12px',
            borderTop: `1px solid ${theme.colors.neutral.border}`,
          }}
        >
          <PriceTag
            price={product.price}
            discountedPrice={product.discountedPrice}
            size="md"
          />

          <Button
            size="sm"
            variant="primary"
            onClick={(e) => {
              e.stopPropagation();
              onAddToCart?.(product);
            }}
          >
            Agregar +
          </Button>
        </div>
      </div>
    </Card>
  );
};
