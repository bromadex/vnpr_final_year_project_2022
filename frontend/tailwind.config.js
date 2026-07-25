/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#e6f4f9',
          100: '#cce9f3',
          500: '#146184',
          600: '#115270',
          700: '#0e435c',
        },
        accent: {
          500: '#dc2626',
          600: '#b91c1c',
        }
      }
    },
  },
  plugins: [],
}
