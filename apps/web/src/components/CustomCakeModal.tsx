'use client';

import React, { useState } from 'react';
import { Button, theme } from '@pasteleria/ui';
import { defaultApiClient } from '@pasteleria/api-client';

export interface CustomCakeModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const CustomCakeModal: React.FC<CustomCakeModalProps> = ({ isOpen, onClose }) => {
  const [guestCount, setGuestCount] = useState(25);
  const [spongeType, setSpongeType] = useState('chocolate_belga');
  const [fillingType, setFillingType] = useState('frambuesa_silvestre');
  const [frostingType, setFrostingType] = useState('merengue_suizo');
  const [eventDate, setEventDate] = useState('2026-10-15');
  const [customerName, setCustomerName] = useState('');
  const [customerEmail, setCustomerEmail] = useState('');
  const [notes, setNotes] = useState('');
  const [quoteResult, setQuoteResult] = useState<{ quoteId: string; estimatedPriceMin: number; estimatedPriceMax: number; message: string } | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const res = await defaultApiClient.customCakes.requestQuote({
        customerName: customerName || 'Cliente Gourmet',
        customerEmail: customerEmail || 'cliente@ejemplo.com',
        customerPhone: '+34 600 000 000',
        eventDate,
        guestCount,
        tiers: [{ tierNumber: 1, flavorId: spongeType, flavorName: spongeType, fillingId: fillingType, fillingName: fillingType }],
        spongeType: spongeType as any,
        fillingType: fillingType as any,
        frostingType: frostingType as any,
        themeDescription: 'Celebración especial con diseño de alta repostería',
        notes,
      });
      setQuoteResult(res);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 110,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: 'rgba(35, 22, 16, 0.65)',
        backdropFilter: 'blur(6px)',
        padding: '20px',
      }}
      onClick={onClose}
    >
      <div
        style={{
          backgroundColor: '#FFFFFF',
          borderRadius: theme.radii.lg,
          maxWidth: '560px',
          width: '100%',
          maxHeight: '90vh',
          overflowY: 'auto',
          padding: '32px',
          boxShadow: '0 25px 50px rgba(0,0,0,0.25)',
          position: 'relative',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <button
          onClick={onClose}
          style={{ position: 'absolute', top: '20px', right: '20px', background: 'none', border: 'none', fontSize: '1.2rem', cursor: 'pointer' }}
        >
          ✕
        </button>

        <div style={{ textAlign: 'center', marginBottom: '24px' }}>
          <span style={{ fontSize: '2.5rem' }}>🎂</span>
          <h2 style={{ fontFamily: theme.fonts.heading, fontSize: '1.6rem', color: theme.colors.neutral.cocoa, marginTop: '8px' }}>
            Pasteles de Autor a Medida
          </h2>
          <p style={{ color: theme.colors.neutral.textMuted, fontSize: '0.9rem' }}>
            Diseñamos el pastel de tus sueños para bodas, aniversarios y eventos exclusivos.
          </p>
        </div>

        {quoteResult ? (
          <div style={{ textAlign: 'center', padding: '20px', backgroundColor: theme.colors.neutral.cream, borderRadius: theme.radii.md }}>
            <span style={{ fontSize: '2rem' }}>✨</span>
            <h3 style={{ fontFamily: theme.fonts.heading, color: theme.colors.primary.roseDark, margin: '10px 0' }}>
              Cotización #{quoteResult.quoteId}
            </h3>
            <p style={{ fontSize: '0.95rem', color: theme.colors.neutral.textMain, marginBottom: '16px' }}>
              {quoteResult.message}
            </p>
            <div style={{ padding: '16px', backgroundColor: '#FFF', borderRadius: theme.radii.md, border: `1px solid ${theme.colors.neutral.border}` }}>
              <span style={{ fontSize: '0.85rem', color: theme.colors.neutral.textMuted }}>Presupuesto estimado:</span>
              <div style={{ fontFamily: theme.fonts.heading, fontSize: '1.5rem', color: theme.colors.neutral.cocoa, fontWeight: 700 }}>
                {quoteResult.estimatedPriceMin} € – {quoteResult.estimatedPriceMax} €
              </div>
            </div>
            <Button variant="primary" style={{ marginTop: '20px' }} onClick={onClose}>
              Cerrar y Continuar
            </Button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '4px' }}>
                Tu Nombre completo
              </label>
              <input
                required
                type="text"
                placeholder="Ej. Sofía Martínez"
                value={customerName}
                onChange={(e) => setCustomerName(e.target.value)}
                style={{ width: '100%', padding: '10px 14px', borderRadius: theme.radii.md, border: `1px solid ${theme.colors.neutral.border}` }}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '4px' }}>
                Correo electrónico
              </label>
              <input
                required
                type="email"
                placeholder="sofia@ejemplo.com"
                value={customerEmail}
                onChange={(e) => setCustomerEmail(e.target.value)}
                style={{ width: '100%', padding: '10px 14px', borderRadius: theme.radii.md, border: `1px solid ${theme.colors.neutral.border}` }}
              />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '4px' }}>
                  Fecha del Evento
                </label>
                <input
                  required
                  type="date"
                  value={eventDate}
                  onChange={(e) => setEventDate(e.target.value)}
                  style={{ width: '100%', padding: '10px', borderRadius: theme.radii.md, border: `1px solid ${theme.colors.neutral.border}` }}
                />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '4px' }}>
                  Nº Estimado de Invitados
                </label>
                <input
                  type="number"
                  min="10"
                  max="300"
                  value={guestCount}
                  onChange={(e) => setGuestCount(Number(e.target.value))}
                  style={{ width: '100%', padding: '10px', borderRadius: theme.radii.md, border: `1px solid ${theme.colors.neutral.border}` }}
                />
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '4px' }}>
                  Bizcocho Base
                </label>
                <select
                  value={spongeType}
                  onChange={(e) => setSpongeType(e.target.value)}
                  style={{ width: '100%', padding: '10px', borderRadius: theme.radii.md, border: `1px solid ${theme.colors.neutral.border}` }}
                >
                  <option value="chocolate_belga">Chocolate Belga 70%</option>
                  <option value="vainilla_bourbon">Vainilla Bourbon</option>
                  <option value="red_velvet">Red Velvet Clásico</option>
                  <option value="limon_amapola">Limón & Semillas Amapola</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '4px' }}>
                  Relleno Gourmet
                </label>
                <select
                  value={fillingType}
                  onChange={(e) => setFillingType(e.target.value)}
                  style={{ width: '100%', padding: '10px', borderRadius: theme.radii.md, border: `1px solid ${theme.colors.neutral.border}` }}
                >
                  <option value="frambuesa_silvestre">Frambuesa Silvestre</option>
                  <option value="avellana_praline">Praliné de Avellana</option>
                  <option value="crema_maracuya">Crema de Maracuyá</option>
                  <option value="trufa_negra">Trufa Negra Suave</option>
                </select>
              </div>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '4px' }}>
                Detalles del diseño o temática deseada
              </label>
              <textarea
                rows={3}
                placeholder="Flores naturales preservadas, estilo minimalista, paleta tonos pastel..."
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                style={{ width: '100%', padding: '10px 14px', borderRadius: theme.radii.md, border: `1px solid ${theme.colors.neutral.border}`, fontFamily: 'inherit' }}
              />
            </div>

            <Button
              type="submit"
              variant="gold"
              size="lg"
              isLoading={isSubmitting}
              style={{ width: '100%', marginTop: '8px' }}
            >
              Solicitar Cotización y Propuesta
            </Button>
          </form>
        )}
      </div>
    </div>
  );
};
