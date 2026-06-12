/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#F8FAFC",
        surface: {
          DEFAULT: "#FFFFFF",
          raised: "#FFFFFF",
          muted: "#F1F5F9",
          subtle: "#E2E8F0",
          tint: "#EEF2FF",
          blue: "#EFF6FF",
          emerald: "#ECFDF5",
          amber: "#FFFBEB",
          rose: "#FFF1F2",
        },
        border: {
          DEFAULT: "#E2E8F0",
          strong: "#CBD5E1",
          subtle: "#F1F5F9",
        },
        text: {
          DEFAULT: "#0F172A",
          soft: "#334155",
          muted: "#64748B",
          faint: "#94A3B8",
          inverse: "#FFFFFF",
        },
        primary: {
          DEFAULT: "#2563EB",
          hover: "#1D4ED8",
          soft: "#DBEAFE",
          subtle: "#EFF6FF",
          deep: "#1E3A8A",
        },
        secondary: {
          DEFAULT: "#1E293B",
          hover: "#0F172A",
          soft: "#F1F5F9",
        },
        accent: {
          DEFAULT: "#4F46E5",
          hover: "#4338CA",
          soft: "#E0E7FF",
        },
        success: {
          DEFAULT: "#10B981",
          hover: "#059669",
          soft: "#D1FAE5",
        },
        warning: {
          DEFAULT: "#F59E0B",
          hover: "#D97706",
          soft: "#FEF3C7",
        },
        error: {
          DEFAULT: "#E11D48",
          hover: "#BE123C",
          soft: "#FFE4E6",
        },
      },
      boxShadow: {
        premium:
          "0 1px 2px rgba(15, 23, 42, 0.04), 0 20px 50px rgba(15, 23, 42, 0.07)",
        "premium-hover":
          "0 2px 6px rgba(15, 23, 42, 0.06), 0 24px 60px rgba(15, 23, 42, 0.1)",
        "inner-soft": "inset 0 1px 2px rgba(15, 23, 42, 0.04)",
        "soft-card": "0 8px 30px rgba(15, 23, 42, 0.06)",
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        display: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
