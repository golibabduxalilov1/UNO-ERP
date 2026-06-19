/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50:  '#EFF4FF',
          100: '#DEE9FE',
          200: '#C4D8FD',
          300: '#9BBCFB',
          400: '#6B97F8',
          500: '#366EF9',
          600: '#1F52E8',
          700: '#163CCC',
          800: '#1234A8',
          900: '#0F2887',
        },
        surface: {
          DEFAULT: '#F5F7FB',
          card:    '#FFFFFF',
          hover:   '#F9FAFB',
          sidebar: '#FFFFFF',
        },
        ink: {
          DEFAULT: '#1A2035',
          2:       '#374151',
          3:       '#6B7280',
          4:       '#9CA3AF',
          5:       '#D1D5DB',
        },
      },
      fontFamily: {
        sans:    ['Inter', 'system-ui', 'sans-serif'],
        display: ['"Plus Jakarta Sans"', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        sm:    '6px',
        DEFAULT: '8px',
        md:    '10px',
        lg:    '12px',
        xl:    '16px',
        '2xl': '20px',
        full:  '9999px',
      },
      animation: {
        'fade-in':   'fadeUp 0.25s ease-out',
        'spin':      'spin 1s linear infinite',
        'pulse-dot': 'pulseDot 2s ease-in-out infinite',
      },
      keyframes: {
        fadeUp:   { from: { opacity: '0', transform: 'translateY(10px)' }, to: { opacity: '1', transform: 'translateY(0)' } },
        pulseDot: { '0%,100%': { opacity: '1', transform: 'scale(1)' }, '50%': { opacity: '0.4', transform: 'scale(1.3)' } },
      },
    },
  },
  plugins: [],
}
