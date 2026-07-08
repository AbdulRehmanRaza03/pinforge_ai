import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // PinForge AI palette
        bg: {
          DEFAULT: "#070712",
          surface: "#0d0d1f",
          elevated: "#161630",
          hover: "#1e1e3a",
        },
        primary: {
          DEFAULT: "#9333ea",
          light: "#a855f7",
          dark: "#7c3aed",
          glow: "rgba(147, 51, 234, 0.3)",
        },
        accent: {
          fuchsia: "#e879f9",
          gold: "#f59e0b",
          cyan: "#06b6d4",
          green: "#10b981",
          red: "#ef4444",
        },
        border: {
          DEFAULT: "rgba(147, 51, 234, 0.2)",
          bright: "rgba(147, 51, 234, 0.5)",
          subtle: "rgba(255, 255, 255, 0.06)",
        },
        text: {
          DEFAULT: "#f8fafc",
          muted: "#94a3b8",
          dim: "#64748b",
        },
      },
      fontFamily: {
        display: ["Sora", "sans-serif"],
        body: ["DM Sans", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      backgroundImage: {
        "gradient-primary": "linear-gradient(135deg, #7c3aed 0%, #9333ea 50%, #e879f9 100%)",
        "gradient-gold": "linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%)",
        "gradient-cyan": "linear-gradient(135deg, #06b6d4 0%, #22d3ee 100%)",
        "gradient-card": "linear-gradient(135deg, rgba(13,13,31,0.8) 0%, rgba(22,22,48,0.6) 100%)",
        "hero-glow": "radial-gradient(ellipse 80% 60% at 50% -20%, rgba(147,51,234,0.25) 0%, transparent 70%)",
        "sidebar-glow": "radial-gradient(ellipse 100% 60% at 0% 50%, rgba(147,51,234,0.1) 0%, transparent 60%)",
      },
      boxShadow: {
        "glow-sm": "0 0 15px rgba(147, 51, 234, 0.2)",
        "glow-md": "0 0 30px rgba(147, 51, 234, 0.3)",
        "glow-lg": "0 0 60px rgba(147, 51, 234, 0.2)",
        "card": "0 4px 24px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.05)",
        "gold": "0 0 20px rgba(245, 158, 11, 0.3)",
      },
      borderRadius: {
        "2xl": "1rem",
        "3xl": "1.5rem",
      },
      animation: {
        "fade-in": "fadeIn 0.4s ease-out",
        "slide-up": "slideUp 0.5s ease-out",
        "pulse-glow": "pulseGlow 2s ease-in-out infinite",
        "shimmer": "shimmer 2s linear infinite",
        "float": "float 6s ease-in-out infinite",
      },
      keyframes: {
        fadeIn: { "0%": { opacity: "0" }, "100%": { opacity: "1" } },
        slideUp: { "0%": { opacity: "0", transform: "translateY(20px)" }, "100%": { opacity: "1", transform: "translateY(0)" } },
        pulseGlow: { "0%, 100%": { boxShadow: "0 0 15px rgba(147,51,234,0.2)" }, "50%": { boxShadow: "0 0 30px rgba(147,51,234,0.5)" } },
        shimmer: { "0%": { transform: "translateX(-100%)" }, "100%": { transform: "translateX(100%)" } },
        float: { "0%, 100%": { transform: "translateY(0px)" }, "50%": { transform: "translateY(-10px)" } },
      },
    },
  },
  plugins: [],
};
export default config;
