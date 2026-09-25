/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
    '../../packages/ui/src/**/*.{js,ts,jsx,tsx}'
  ],
  theme: {
    extend: {
      colors: {
        gold: {
          light: '#F3E5AB',
          DEFAULT: '#D4AF37',
          dark: '#997F24',
        },
        rose: {
          light: '#F7E7E9',
          DEFAULT: '#C86D74',
          dark: '#8A3B43',
        },
        cocoa: {
          light: '#3D281F',
          DEFAULT: '#231610',
        },
        cream: {
          DEFAULT: '#FFF9F2',
          dark: '#F7EEE3',
        },
      },
      fontFamily: {
        heading: ["'Playfair Display'", 'Georgia', 'serif'],
        body: ["'Outfit'", '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
