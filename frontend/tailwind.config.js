/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        gray: {
          950: '#0f172a', // slate-900
          900: '#1e293b', // slate-800
          800: '#334155', // slate-700
          500: '#64748b', // slate-500
          400: '#94a3b8', // slate-400
          100: '#f1f5f9', // slate-100
        },
        emerald: {
          500: '#10b981',
        },
        amber: {
          500: '#f59e0b',
        },
        red: {
          500: '#ef4444',
        },
        blue: {
          500: '#3b82f6',
        },
        purple: {
          500: '#a855f7',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['"Fira Code"', '"JetBrains Mono"', 'Consolas', 'monospace'],
      },
      fontSize: {
        xs: ['0.75rem', { lineHeight: '1rem' }],
        sm: ['0.875rem', { lineHeight: '1.25rem' }],
      }
    },
  },
  plugins: [],
}
