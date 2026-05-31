import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./features/**/*.{ts,tsx}", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        border: "rgba(148, 163, 184, 0.18)",
        input: "rgba(15, 23, 42, 0.75)",
        ring: "#22d3ee",
        background: "#020617",
        foreground: "#e2e8f0",
        primary: {
          DEFAULT: "#22d3ee",
          foreground: "#082f49",
        },
        secondary: {
          DEFAULT: "#0f172a",
          foreground: "#cbd5e1",
        },
        muted: {
          DEFAULT: "#111827",
          foreground: "#94a3b8",
        },
        accent: {
          DEFAULT: "#1e293b",
          foreground: "#f8fafc",
        },
        card: {
          DEFAULT: "rgba(2, 6, 23, 0.78)",
          foreground: "#e2e8f0",
        },
      },
    },
  },
  plugins: [],
};

export default config;
