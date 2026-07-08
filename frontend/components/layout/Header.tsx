"use client";
import { useEffect, useState } from "react";
import { Bell, ChevronDown, Search } from "lucide-react";
import { supabase } from "@/lib/supabase";
import type { User } from "@supabase/supabase-js";

export default function Header({ title }: { title?: string }) {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    supabase.auth.getUser().then(({ data }) => setUser(data.user));
  }, []);

  const initials = user?.user_metadata?.full_name
    ? user.user_metadata.full_name.split(" ").map((n: string) => n[0]).join("").slice(0, 2).toUpperCase()
    : user?.email?.slice(0, 2).toUpperCase() ?? "??";

  return (
    <header className="h-16 border-b border-border flex items-center justify-between px-6 bg-bg/80 sticky top-0 z-30" style={{ backdropFilter: "blur(12px)" }}>
      <div>
        {title && <h1 className="font-display font-semibold text-white text-lg">{title}</h1>}
      </div>

      <div className="flex items-center gap-4">
        {/* Search (cosmetic for now) */}
        <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-bg-elevated border border-border text-text-dim text-sm font-body">
          <Search size={14} />
          <span>Quick search…</span>
          <kbd className="ml-4 px-1.5 py-0.5 rounded text-[10px] bg-bg-surface border border-border font-mono">⌘K</kbd>
        </div>

        {/* Notification bell */}
        <button className="relative w-9 h-9 rounded-lg flex items-center justify-center bg-bg-elevated border border-border text-text-muted hover:text-white hover:border-primary/40 transition-all duration-200">
          <Bell size={16} />
          <span className="absolute -top-1 -right-1 w-3.5 h-3.5 rounded-full bg-primary text-[9px] text-white flex items-center justify-center font-mono">3</span>
        </button>

        {/* User avatar */}
        <div className="flex items-center gap-2 pl-3 border-l border-border cursor-pointer group">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center font-display font-bold text-xs text-white" style={{ background: "linear-gradient(135deg, #7c3aed, #e879f9)" }}>
            {initials}
          </div>
          <span className="hidden md:block text-sm font-body text-text-muted group-hover:text-white transition-colors max-w-[120px] truncate">
            {user?.user_metadata?.full_name || user?.email?.split("@")[0] || "User"}
          </span>
          <ChevronDown size={14} className="text-text-dim" />
        </div>
      </div>
    </header>
  );
}
