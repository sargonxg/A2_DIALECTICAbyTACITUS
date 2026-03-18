import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#020617",
        surface: {
          DEFAULT: "#0f172a",
          hover: "#1e293b",
          active: "#334155",
        },
        border: "#1e293b",
        "border-hover": "#334155",
        "text-primary": "#f1f5f9",
        "text-secondary": "#94a3b8",
        accent: {
          DEFAULT: "#14b8a6",
          hover: "#0d9488",
          muted: "#14b8a620",
        },
        danger: { DEFAULT: "#f43f5e", muted: "#f43f5e20" },
        warning: { DEFAULT: "#f59e0b", muted: "#f59e0b20" },
        success: { DEFAULT: "#10b981", muted: "#10b98120" },
        node: {
          actor: "#3b82f6",
          conflict: "#6366f1",
          event: "#eab308",
          issue: "#f97316",
          interest: "#22c55e",
          norm: "#64748b",
          process: "#06b6d4",
          outcome: "#10b981",
          narrative: "#ec4899",
          emotional_state: "#f43f5e",
          trust_state: "#8b5cf6",
          power_dynamic: "#a855f7",
          location: "#78716c",
          evidence: "#94a3b8",
          role: "#d946ef",
        },
        glasl: {
          "win-win": "#22c55e",
          "win-lose": "#eab308",
          "lose-lose": "#ef4444",
        },
      },
      fontFamily: {
        sans: ["system-ui", "-apple-system", "sans-serif"],
        mono: ["JetBrains Mono", "Menlo", "monospace"],
      },
      borderRadius: {
        lg: "0.5rem",
        md: "0.375rem",
        sm: "0.25rem",
      },
      animation: {
        "fade-in": "fadeIn 0.2s ease-in-out",
        "slide-in": "slideIn 0.3s ease-out",
        "slide-up": "slideUp 0.3s ease-out",
        pulse: "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideIn: {
          "0%": { transform: "translateX(-10px)", opacity: "0" },
          "100%": { transform: "translateX(0)", opacity: "1" },
        },
        slideUp: {
          "0%": { transform: "translateY(10px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
