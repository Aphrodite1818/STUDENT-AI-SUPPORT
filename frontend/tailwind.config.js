/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#F4EBD0",
        surface: {
          DEFAULT: "#FFFFFF",
          raised: "#F9FAFB",
          muted: "#F1F5F9",
          subtle: "#E2E8F0",
          lavender: "#F4EEFF",
          peach: "#FFF1E6",
          cyan: "#E0F7FA",
          mint: "#F0FDF4",
          yellow: "#FFF8E1",
        },
        border: {
          DEFAULT: "#E2E8F0",
          strong: "#CBD5E1",
        },
        text: {
          DEFAULT: "#0F172A",
          soft: "#334155",
          muted: "#64748B",
          inverse: "#FFFFFF",
        },
        primary: {
          DEFAULT: "#F59E0B",
          hover: "#D97706",
          soft: "#FFF8E1",
        },
        secondary: {
          DEFAULT: "#1E293B",
          hover: "#0F172A",
          soft: "#F1F5F9",
        },
        accent: {
          DEFAULT: "#14B8A6",
          hover: "#0F766E",
          soft: "#CCFBF1",
        },
        success: {
          DEFAULT: "#15803D",
          soft: "#F0FDF4",
        },
        warning: {
          DEFAULT: "#B45309",
          soft: "#FFF8E1",
        },
        error: {
          DEFAULT: "#B91C1C",
          soft: "#F3E7E7",
        },
      },
      boxShadow: {
        premium:
          "0 1px 2px rgba(15, 23, 42, 0.04), 0 18px 45px rgba(15, 23, 42, 0.08)",
        "premium-hover":
          "0 2px 5px rgba(15, 23, 42, 0.06), 0 22px 55px rgba(15, 23, 42, 0.11)",
        "inner-soft": "inset 0 1px 2px rgba(15, 23, 42, 0.04)",
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        display: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
