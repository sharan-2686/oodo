/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#6B1A2A',
          mid: '#8B2535',
          warm: '#B85C6E',
          50: '#fdf2f4',
          100: '#fce7ea',
        },
        ivory: '#FAF7F2',
        paper: '#F2EDE6',
        gold: {
          DEFAULT: '#C9A84C',
          light: '#E8D48B',
          dark: '#A07C2A',
        },
        ink: '#1C1410',
        muted: '#7A6860',
        border: '#E2D9D0',
        status: {
          success: '#2D6A4F',
          successBg: '#D8F3DC',
          warning: '#7B5E00',
          warningBg: '#FFF3CD',
          error: '#8B1A1A',
          errorBg: '#FFE5E5',
          info: '#1A3A5C',
          infoBg: '#E3F0FF',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['"Playfair Display"', 'Georgia', 'serif'],
      },
      boxShadow: {
        'glass-sm': '0 2px 8px rgba(28,20,16,0.06), 0 1px 3px rgba(28,20,16,0.04)',
        'glass-md': '0 4px 20px rgba(28,20,16,0.08), 0 2px 8px rgba(28,20,16,0.05), inset 0 1px 0 rgba(255,255,255,0.6)',
        'glass-lg': '0 8px 40px rgba(28,20,16,0.12), 0 4px 16px rgba(28,20,16,0.08), inset 0 1px 0 rgba(255,255,255,0.7)',
        'gold': '0 0 20px rgba(201,168,76,0.25)',
        'burgundy': '0 0 20px rgba(107,26,42,0.2)',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-in': 'slideIn 0.25s ease-out',
      },
      keyframes: {
        fadeIn: { from: { opacity: '0' }, to: { opacity: '1' } },
        slideUp: { from: { opacity: '0', transform: 'translateY(8px)' }, to: { opacity: '1', transform: 'translateY(0)' } },
        slideIn: { from: { opacity: '0', transform: 'translateX(-8px)' }, to: { opacity: '1', transform: 'translateX(0)' } },
      },
    },
  },
  plugins: [],
};
