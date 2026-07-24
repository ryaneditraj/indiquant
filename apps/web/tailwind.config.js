/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        canvas: {
          DEFAULT: "#06110d",
          elevated: "#0b1a14",
          border: "#1a3228",
        },
        ink: {
          DEFAULT: "#e7f6ee",
          muted: "#8fb29e",
          faint: "#5a7a6a",
        },
        accent: {
          DEFAULT: "#c8f54a",
          soft: "#1d3a18",
          teal: "#4fd1c5",
          warn: "#f0b429",
          good: "#5eead4",
          bad: "#fb7185",
        },
      },
      fontFamily: {
        display: ["var(--font-display)", "Georgia", "serif"],
        sans: ["var(--font-sans)", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
      },
      boxShadow: {
        panel:
          "0 0 0 1px rgba(26, 50, 40, 0.9), 0 18px 50px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(200, 245, 74, 0.04)",
      },
      backgroundImage: {
        grid: "linear-gradient(rgba(200, 245, 74, 0.035) 1px, transparent 1px), linear-gradient(90deg, rgba(200, 245, 74, 0.035) 1px, transparent 1px)",
      },
      backgroundSize: {
        grid: "56px 56px",
      },
      keyframes: {
        pulseDot: {
          "0%, 100%": { opacity: "1", transform: "scale(1)" },
          "50%": { opacity: "0.55", transform: "scale(0.85)" },
        },
        rise: {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        pulseDot: "pulseDot 2s ease-in-out infinite",
        rise: "rise 0.45s ease-out both",
      },
    },
  },
  plugins: [],
};
