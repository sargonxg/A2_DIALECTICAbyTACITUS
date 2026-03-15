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
        // TACITUS Design System — Dark mode only
        background: "#09090b",    // zinc-950
        surface: "#18181b",       // zinc-900
        border: "#27272a",        // zinc-800
        "text-primary": "#fafafa",
        "text-secondary": "#a1a1aa",
        accent: "#0d9488",        // teal-600 (TACITUS brand)
        "accent-hover": "#0f766e", // teal-700

        // Node type colors (for graph visualization and badges)
        node: {
          actor: "#3b82f6",           // blue-500
          conflict: "#6366f1",        // indigo-500
          event: "#eab308",           // yellow-500
          issue: "#f97316",           // orange-500
          interest: "#22c55e",        // green-500
          norm: "#64748b",            // slate-500
          process: "#06b6d4",         // cyan-500
          outcome: "#10b981",         // emerald-500
          narrative: "#ec4899",       // pink-500
          emotional_state: "#f43f5e", // rose-500
          trust_state: "#8b5cf6",     // violet-500
          power_dynamic: "#a855f7",   // purple-500
          location: "#78716c",        // stone-500
          evidence: "#94a3b8",        // slate-400
          role: "#d946ef",            // fuchsia-500
        },

        // Glasl stage colors
        glasl: {
          "win-win": "#22c55e",    // green — stages 1-3
          "win-lose": "#eab308",   // yellow — stages 4-6
          "lose-lose": "#ef4444",  // red — stages 7-9
        },
      },
      fontFamily: {
        sans: ["var(--font-instrument-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-jetbrains-mono)", "Menlo", "monospace"],
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      animation: {
        "fade-in": "fadeIn 0.2s ease-in-out",
        "slide-in": "slideIn 0.3s ease-out",
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
      },
    },
  },
  plugins: [],
};

export default config;
