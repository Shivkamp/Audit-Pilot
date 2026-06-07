/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      colors: {
        // Audit Blue — primary brand
        primary: {
          DEFAULT: '#2563EB',
          dark: '#1E40AF',
          light: '#DBEAFE',
          hover: '#1D4ED8',
        },
        // Evidence Teal — secondary accent
        accent: {
          DEFAULT: '#14B8A6',
          dark: '#0F766E',
          light: '#CCFBF1',
          hover: '#0D9488',
        },
        // AI accent — sparingly
        ai: {
          DEFAULT: '#7C3AED',
          light: '#EDE9FE',
        },
        // Semantic
        success: {
          DEFAULT: '#16A34A',
          light: '#DCFCE7',
          dark: '#15803D',
        },
        warning: {
          DEFAULT: '#F59E0B',
          light: '#FEF3C7',
          dark: '#D97706',
        },
        danger: {
          DEFAULT: '#DC2626',
          light: '#FEE2E2',
          dark: '#B91C1C',
        },
        critical: {
          DEFAULT: '#991B1B',
          light: '#FEE2E2',
        },
        // Surfaces
        bg: '#F8FAFC',
        surface: '#FFFFFF',
        'surface-soft': '#F1F5F9',
        border: '#E2E8F0',
        'border-strong': '#CBD5E1',
        // Text
        'text-primary': '#0F172A',
        'text-secondary': '#475569',
        muted: '#64748B',
        faint: '#94A3B8',
        // Sidebar stays dark slate
        sidebar: {
          bg: '#0F172A',
          hover: '#1E293B',
          active: '#1E3A5F',
          border: '#1E293B',
          text: '#94A3B8',
          'text-active': '#60A5FA',
          'text-hover': '#E2E8F0',
        },
      },
      boxShadow: {
        'card': '0 1px 3px 0 rgb(0 0 0 / 0.07), 0 1px 2px -1px rgb(0 0 0 / 0.07)',
        'card-hover': '0 4px 12px 0 rgb(0 0 0 / 0.10), 0 2px 4px -1px rgb(0 0 0 / 0.06)',
        'card-lg': '0 8px 24px 0 rgb(0 0 0 / 0.08), 0 2px 6px -2px rgb(0 0 0 / 0.05)',
        'drawer': '0 20px 60px -12px rgb(0 0 0 / 0.25)',
        'dialog': '-8px 8px 40px -8px rgb(0 0 0 / 0.20)',
      },
      borderRadius: {
        'xl': '0.75rem',
        '2xl': '1rem',
        '3xl': '1.5rem',
      },
      animation: {
        'shimmer': 'shimmer 1.6s linear infinite',
        'pulse-dot': 'pulse-dot 2s cubic-bezier(0.4,0,0.6,1) infinite',
        'fade-in': 'fade-in 0.22s ease-out',
        'slide-in-up': 'slide-in-up 0.22s ease-out',
        'slide-in-right': 'slide-in-right 0.22s ease-out',
      },
      keyframes: {
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        'pulse-dot': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.4' },
        },
        'fade-in': {
          from: { opacity: '0' },
          to: { opacity: '1' },
        },
        'slide-in-up': {
          from: { opacity: '0', transform: 'translateY(8px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        'slide-in-right': {
          from: { opacity: '0', transform: 'translateX(16px)' },
          to: { opacity: '1', transform: 'translateX(0)' },
        },
      },
      transitionTimingFunction: {
        'enterprise': 'cubic-bezier(0.16, 1, 0.3, 1)',
      },
    },
  },
  plugins: [],
}
