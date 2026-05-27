/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: '#1A1A1A',
        surface: '#242424',
        surfaceHover: '#2E2E2E',
        border: '#333333',
        primary: '#E8A87C',
        accent: '#85C1E9',
        text: '#F5F0EB',
        textMuted: '#9CA3AF',
        success: '#6EE7B7',
        warning: '#FCD34D',
        danger: '#FCA5A5',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        'card': '8px',
      }
    },
  },
  plugins: [],
}
