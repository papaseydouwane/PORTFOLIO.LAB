/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/templates/**/*.html",
    "./app/static/**/*.js"
  ],
  theme: {
    extend: {
      colors: {
        // Permet d'utiliser des variables CSS injectées par Flask
        customPrimary: 'var(--p-color)',
        customSecondary: 'var(--s-color)',
      }
    },
  },
  plugins: [],
}