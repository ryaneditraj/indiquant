/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        canvas: {
          DEFAULT: "#030712",
          elevated: "#0a1224",
          border: "#1a2744",
        },
        ink: {
          DEFAULT: "#e8eefc",
          muted: "#8b9dc3",
          faint: "#5a6f96",
        },
        accent: {
          DEFAULT: "#3dff9a",
          soft: "#0a2f22",
          radar: "#22d3ee",
          warn: "#fbbf24",
          good: "#3dff9a",
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
          "0 0 0 1px rgba(26, 39, 68, 0.95), 0 20px 50px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(61, 255, 154, 0.05)",
      },
      backgroundImage: {
        grid: "linear-gradient(rgba(61, 255, 154, 0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(34, 211, 238, 0.035) 1px, transparent 1px)",
      },
      backgroundSize: {
        grid: "56px 56px",
      },
      keyframes: {
        pulseDot: {
          "0%, 100%": { opacity: "1", transform: "scale(1)" },
          "50%": { opacity: "0.5", transform: "scale(0.85)" },
        },
        sweep: {
          "0%": { transform: "rotate(0deg)", opacity: "0.35" },
          "100%": { transform: "rotate(360deg)", opacity: "0.35" },
        },
      },
      animation: {
        pulseDot: "pulseDot 2s ease-in-out infinite",
        sweep: "sweep 8s linear infinite",
      },
    },
  },
  plugins: [],
};
