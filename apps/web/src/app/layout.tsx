import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Maison du Délice | Alta Pastelería & Repostería de Autor',
  description: 'Descubre nuestra exclusiva colección de pasteles de autor, tartas finas, macarons parisinos y viennoiserie artesanal horneada a diario.',
  keywords: ['pasteleria', 'alta reposteria', 'tartas artesanales', 'macarons', 'pasteles a medida', 'gourmet'],
  authors: [{ name: 'Maison du Délice Atelier' }],
  viewport: 'width=device-width, initial-scale=1',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body>{children}</body>
    </html>
  );
}
