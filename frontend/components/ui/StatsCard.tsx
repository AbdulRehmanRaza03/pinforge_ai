"use client";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import type { LucideIcon } from "lucide-react";

interface StatsCardProps {
  label: string;
  value: string | number;
  icon: LucideIcon;
  color: "violet" | "fuchsia" | "cyan" | "gold" | "green" | "red";
  subtitle?: string;
  index?: number;
}

const colorMap = {
  violet:  { bg: "rgba(147,51,234,0.12)",  border: "rgba(147,51,234,0.3)",  text: "#a855f7" },
  fuchsia: { bg: "rgba(232,121,249,0.12)", border: "rgba(232,121,249,0.3)", text: "#e879f9" },
  cyan:    { bg: "rgba(6,182,212,0.12)",   border: "rgba(6,182,212,0.3)",   text: "#06b6d4" },
  gold:    { bg: "rgba(245,158,11,0.12)",  border: "rgba(245,158,11,0.3)",  text: "#f59e0b" },
  green:   { bg: "rgba(16,185,129,0.12)",  border: "rgba(16,185,129,0.3)",  text: "#10b981" },
  red:     { bg: "rgba(239,68,68,0.12)",   border: "rgba(239,68,68,0.3)",   text: "#ef4444" },
};

export default function StatsCard({ label, value, icon: Icon, color, subtitle, index = 0 }: StatsCardProps) {
  const c = colorMap[color];
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.08, duration: 0.5 }}
      className="glass-card p-5 group hover:border-primary/40 transition-all duration-300 relative overflow-hidden"
    >
      {/* Subtle glow behind icon */}
      <div className="absolute top-0 right-0 w-24 h-24 rounded-full opacity-20 blur-2xl"
        style={{ background: c.text, transform: "translate(30%, -30%)" }} />

      <div className="flex items-start justify-between mb-4 relative">
        <p className="text-text-muted text-sm font-body">{label}</p>
        <div className="w-9 h-9 rounded-xl flex items-center justify-center"
          style={{ background: c.bg, border: `1px solid ${c.border}` }}>
          <Icon size={17} style={{ color: c.text }} />
        </div>
      </div>
      <p className="font-display text-3xl font-bold relative" style={{ color: c.text }}>{value}</p>
      {subtitle && <p className="text-text-dim text-xs font-body mt-1">{subtitle}</p>}
    </motion.div>
  );
}
