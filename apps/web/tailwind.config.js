/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        canvas: {
          DEFAULT: "#0b0f14",
          elevated: "#121820",
          border: "#1e2a36",
        },
        ink: {
          DEFAULT: "#e8eef4",
          muted: "#8b9aab",
          faint: "#5c6b7a",
        },
        accent: {
          DEFAULT: "#3d9bfd",
          soft: "#1a3a5c",
          warn: "#e8a838",
          good: "#3ecf8e",
          bad: "#f07178",
        },
      },
      fontFamily: {
        display: ["var(--font-display)", "Georgia", "serif"],
        sans: ["var(--font-sans)", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
      },
      boxShadow: {
        panel: "0 0 0 1px rgba(30, 42, 54, 0.9), 0 12px 40px rgba(0, 0, 0, 0.35)",
      },
      backgroundImage: {
        grid: "linear-gradient(rgba(61, 155, 253, 0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(61, 155, 253, 0.04) 1px, transparent 1px)",
      },
      backgroundSize: {
        grid: "48px 48px",
      },
    },
  },
  plugins: [],
};
