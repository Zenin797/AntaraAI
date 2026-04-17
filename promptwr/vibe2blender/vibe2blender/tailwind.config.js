/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'bg': '#000',
        'text': '#FFF',
        'accent': '#333',
        'secondary': '#111',
        'border': '#222',
      },
    },
  },
  plugins: [],
}
