export const theme = {
  colors: {
    primary: {
      gold: '#D4AF37',
      goldLight: '#F3E5AB',
      goldDark: '#997F24',
      rose: '#C86D74',
      roseLight: '#F7E7E9',
      roseDark: '#8A3B43',
    },
    neutral: {
      cocoa: '#231610',
      cocoaLight: '#3D281F',
      cream: '#FFF9F2',
      creamDark: '#F7EEE3',
      textMain: '#2C221E',
      textMuted: '#7D7068',
      border: '#E8DFD5',
      white: '#FFFFFF',
    },
    accent: {
      pistachio: '#799E6C',
      berry: '#9F2B48',
      caramel: '#C67D38',
      vanilla: '#FDF6E2',
    },
    status: {
      success: '#2E7D32',
      warning: '#ED6C02',
      error: '#D32F2F',
      info: '#0288D1',
    },
  },
  fonts: {
    heading: "'Playfair Display', Georgia, serif",
    body: "'Outfit', -apple-system, BlinkMacSystemFont, sans-serif",
  },
  radii: {
    sm: '6px',
    md: '12px',
    lg: '20px',
    full: '9999px',
  },
  shadows: {
    card: '0 10px 30px rgba(35, 22, 16, 0.06)',
    cardHover: '0 20px 40px rgba(35, 22, 16, 0.12)',
    goldGlow: '0 4px 20px rgba(212, 175, 55, 0.35)',
  },
} as const;

export type Theme = typeof theme;
