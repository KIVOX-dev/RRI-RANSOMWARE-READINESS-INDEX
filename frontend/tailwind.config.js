/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        bg: "#f4f4f4",
        "bg-raised": "#ececea",
        "bg-card": "#ffffff",
        accent: "#ecf95a",
        "accent-dim": "#d6e34f",
        "accent-ink": "#7a6900",
        ink: "#191314",
        light: "#191314",
        white: "#ffffff",
        border: "#dedad9",
        muted: "#726a6c",
      },
      fontFamily: {
        sans: ["Public Sans", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      borderRadius: {
        card: "14px",
      },
    },
  },
  plugins: [],
};
