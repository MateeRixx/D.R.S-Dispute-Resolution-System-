/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      colors: {
        drs: {
          bg: "#F8F6F3",
          surface: "#FFFFFF",
          card: "#F0EEEA",
          "card-hover": "#E8E5E0",
          border: "#E3DFD8",
          text: "#1C1917",
          "text-secondary": "#6B6560",
          "text-light": "#9C958E",
          accent: "#1A3C5E",
          "accent-soft": "#2E5C8A",
          "accent-subtle": "#EBF0F5",
        },
        semantic: {
          emerald: "#059669",
          amber: "#B45309",
          red: "#DC2626",
        },
      },
      boxShadow: {
        card: "0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04)",
        "card-hover": "0 4px 12px rgba(0,0,0,0.08)",
        modal: "0 20px 60px rgba(0,0,0,0.12)",
        nav: "0 1px 2px rgba(0,0,0,0.04)",
      },
    },
  },
  plugins: [],
};
