'use client';

import React from 'react';
import { CartItem } from '@pasteleria/shared-types';
import { Button, PriceTag, theme } from '@pasteleria/ui';

export interface CartDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  items: CartItem[];
  onUpdateQuantity: (id: string, delta: number) => void;
  onRemoveItem: (id: string) => void;
  onCheckout: () => void;
}

export const CartDrawer: React.FC<CartDrawerProps> = ({
  isOpen,
  onClose,
  items,
  onUpdateQuantity,
  onRemoveItem,
  onCheckout,
}) => {
  if (!isOpen) return null;

  const subtotal = items.reduce((sum, item) => sum + item.totalPrice, 0);
  const deliveryFee = subtotal > 50 || items.length === 0 ? 0 : 4.5;
  const total = subtotal + deliveryFee;

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 100,
        display: 'flex',
        justifyContent: 'flex-end',
        backgroundColor: 'rgba(35, 22, 16, 0.55)',
        backdropFilter: 'blur(4px)',
      }}
      onClick={onClose}
    >
      <div
        style={{
          width: '100%',
          maxWidth: '440px',
          height: '100%',
          backgroundColor: '#FFFFFF',
          boxShadow: '-10px 0 30px rgba(0,0,0,0.15)',
          display: 'flex',
          flexDirection: 'column',
          animation: 'fadeIn 0.3s ease',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Drawer Header */}
        <div
          style={{
            padding: '24px',
            borderBottom: `1px solid ${theme.colors.neutral.border}`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            backgroundColor: theme.colors.neutral.cream,
          }}
        >
          <div>
            <h2 style={{ fontFamily: theme.fonts.heading, fontSize: '1.4rem', color: theme.colors.neutral.cocoa, margin: 0 }}>
              Tu Bolsa de Delicias
            </h2>
            <span style={{ fontSize: '0.85rem', color: theme.colors.neutral.textMuted }}>
              {items.length} {items.length === 1 ? 'producto seleccionado' : 'productos seleccionados'}
            </span>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              fontSize: '1.4rem',
              cursor: 'pointer',
              color: theme.colors.neutral.textMuted,
            }}
          >
            ✕
          </button>
        </div>

        {/* Drawer Items List */}
        <div style={{ flexGrow: 1, overflowY: 'auto', padding: '20px' }}>
          {items.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '60px 20px' }}>
              <span style={{ fontSize: '3rem', display: 'block', marginBottom: '12px' }}>🥐</span>
              <p style={{ fontFamily: theme.fonts.heading, fontSize: '1.2rem', color: theme.colors.neutral.cocoa }}>
                Tu bolsa está vacía
              </p>
              <p style={{ fontSize: '0.9rem', color: theme.colors.neutral.textMuted, marginTop: '8px' }}>
                Explora nuestras creaciones de alta pastelería y añade tus favoritas.
              </p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {items.map((item) => (
                <div
                  key={item.id}
                  style={{
                    display: 'flex',
                    gap: '14px',
                    padding: '12px',
                    backgroundColor: theme.colors.neutral.cream,
                    borderRadius: theme.radii.md,
                    border: `1px solid ${theme.colors.neutral.border}`,
                  }}
                >
                  <img
                    src={item.product.images[0] || 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=400&q=80'}
                    alt={item.product.name}
                    style={{ width: '70px', height: '70px', objectFit: 'cover', borderRadius: theme.radii.sm }}
                  />
                  <div style={{ flexGrow: 1 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <h4 style={{ fontFamily: theme.fonts.heading, fontSize: '0.95rem', margin: 0, color: theme.colors.neutral.cocoa }}>
                        {item.product.name}
                      </h4>
                      <button
                        onClick={() => onRemoveItem(item.id)}
                        style={{ background: 'none', border: 'none', color: '#999', cursor: 'pointer', fontSize: '0.9rem' }}
                      >
                        ✕
                      </button>
                    </div>
                    {item.variant && (
                      <span style={{ fontSize: '0.78rem', color: theme.colors.neutral.textMuted, display: 'block' }}>
                        {item.variant.name}
                      </span>
                    )}
                    {item.customMessage && (
                      <span style={{ fontSize: '0.75rem', color: theme.colors.primary.roseDark, fontStyle: 'italic', display: 'block' }}>
                        «{item.customMessage}»
                      </span>
                    )}

                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '10px' }}>
                      <div
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          border: `1px solid ${theme.colors.neutral.border}`,
                          borderRadius: theme.radii.full,
                          backgroundColor: '#FFF',
                        }}
                      >
                        <button
                          onClick={() => onUpdateQuantity(item.id, -1)}
                          style={{ border: 'none', background: 'none', padding: '2px 8px', cursor: 'pointer', fontSize: '0.9rem' }}
                        >
                          -
                        </button>
                        <span style={{ fontSize: '0.85rem', fontWeight: 600, padding: '0 4px' }}>
                          {item.quantity}
                        </span>
                        <button
                          onClick={() => onUpdateQuantity(item.id, 1)}
                          style={{ border: 'none', background: 'none', padding: '2px 8px', cursor: 'pointer', fontSize: '0.9rem' }}
                        >
                          +
                        </button>
                      </div>
                      <PriceTag price={item.totalPrice} size="sm" />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Drawer Footer with Calculations */}
        {items.length > 0 && (
          <div
            style={{
              padding: '24px',
              borderTop: `1px solid ${theme.colors.neutral.border}`,
              backgroundColor: theme.colors.neutral.cream,
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '0.9rem' }}>
              <span style={{ color: theme.colors.neutral.textMuted }}>Subtotal</span>
              <span style={{ fontWeight: 600 }}>{subtotal.toFixed(2)} €</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '14px', fontSize: '0.9rem' }}>
              <span style={{ color: theme.colors.neutral.textMuted }}>Envío refrigerado boutique</span>
              <span style={{ fontWeight: 600, color: deliveryFee === 0 ? theme.colors.status.success : undefined }}>
                {deliveryFee === 0 ? '¡Gratis (+50€)!' : `${deliveryFee.toFixed(2)} €`}
              </span>
            </div>
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                paddingTop: '12px',
                borderTop: `1px dashed ${theme.colors.neutral.border}`,
                marginBottom: '20px',
              }}
            >
              <span style={{ fontFamily: theme.fonts.heading, fontSize: '1.2rem', fontWeight: 700 }}>Total</span>
              <PriceTag price={total} size="lg" />
            </div>

            <Button
              variant="gold"
              size="lg"
              style={{ width: '100%' }}
              onClick={onCheckout}
            >
              Confirmar Pedido & Pago
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};
