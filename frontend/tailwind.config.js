/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['"JetBrains Mono"', '"Cascadia Code"', 'Consolas', 'monospace'],
      },
      colors: {
        netra: {
          bg: '#020204',
          surface: '#0A0A0F',
          border: 'rgba(255,255,255,0.06)',
          accent: '#00BCEB',
          danger: '#EF4444',
          success: '#10B981',
          warning: '#F59E0B',
        }
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease forwards',
        'slide-up': 'slideUp 0.4s ease forwards',
        'slide-in': 'slideIn 0.3s ease forwards',
        'spin-slow': 'spinSlow 8s linear infinite',
        'blink': 'blinkCursor 1s step-end infinite',
        'shimmer': 'shimmer 1.5s linear infinite',
        'pulse-glow': 'pulseGlow 2s infinite',
      },
      keyframes: {
        fadeIn: { from: { opacity: '0' }, to: { opacity: '1' } },
        slideUp: { from: { opacity: '0', transform: 'translateY(12px)' }, to: { opacity: '1', transform: 'translateY(0)' } },
        slideIn: { from: { opacity: '0', transform: 'translateX(-12px)' }, to: { opacity: '1', transform: 'translateX(0)' } },
        spinSlow: { from: { transform: 'rotate(0deg)' }, to: { transform: 'rotate(360deg)' } },
        blinkCursor: { '0%, 100%': { opacity: '1' }, '50%': { opacity: '0' } },
        shimmer: { '0%': { backgroundPosition: '-200% center' }, '100%': { backgroundPosition: '200% center' } },
        pulseGlow: { '0%, 100%': { boxShadow: '0 0 0 0 rgba(16,185,129,0.4)' }, '50%': { boxShadow: '0 0 0 6px rgba(16,185,129,0)' } },
        marquee: { '0%': { transform: 'translateX(0%)' }, '100%': { transform: 'translateX(-100%)' } },
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}
