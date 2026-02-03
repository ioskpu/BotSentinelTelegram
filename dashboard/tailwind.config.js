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
        crypto: {
          bg: '#0f0f23',
          'bg-secondary': '#1a1a2e',
          'bg-tertiary': '#252542',
          accent: '#00d9ff',
          'accent-hover': '#00b8d9',
          gain: '#00ff88',
          'gain-dim': '#00cc6a',
          loss: '#ff4757',
          'loss-dim': '#cc3a47',
          text: '#ffffff',
          'text-secondary': '#a0a0b0',
          'text-muted': '#6b6b7b',
          border: '#2a2a4a',
          purple: '#8b5cf6',
          'purple-dim': '#7c3aed',
          'purple-light': '#a78bfa',
          blue: '#3b82f6',
          'blue-dim': '#2563eb',
          warning: '#f59e0b',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      boxShadow: {
        'crypto': '0 4px 20px rgba(0, 217, 255, 0.15)',
        'crypto-lg': '0 8px 40px rgba(0, 217, 255, 0.2)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 5px rgba(0, 217, 255, 0.5)' },
          '100%': { boxShadow: '0 0 20px rgba(0, 217, 255, 0.8)' },
        },
      },
    },
  },
  plugins: [],
}
