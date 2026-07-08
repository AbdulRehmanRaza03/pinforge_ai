"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
  LayoutDashboard, PlusSquare, Clock, BarChart3,
  Settings, LogOut, Pin, Users, ChevronRight
} from "lucide-react";
import { supabase } from "@/lib/supabase";
import { cn } from "@/lib/utils";
import toast from "react-hot-toast";

const navItems = [
  { label: "Dashboard",   href: "/dashboard",            icon: LayoutDashboard },
  { label: "Create Pins", href: "/dashboard/create",     icon: PlusSquare },
  { label: "Queue",       href: "/dashboard/queue",      icon: Clock },
  { label: "Analytics",   href: "/dashboard/analytics",  icon: BarChart3 },
  { label: "Accounts",    href: "/dashboard/accounts",   icon: Users },
  { label: "Settings",    href: "/dashboard/settings",   icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();

  async function handleLogout() {
    await supabase.auth.signOut();
    toast.success("Logged out.");
    router.push("/");
  }

  return (
    <aside className="w-60 flex-shrink-0 h-screen sticky top-0 flex flex-col border-r border-border bg-bg" style={{ background: "radial-gradient(ellipse 100% 60% at 0% 50%, rgba(147,51,234,0.07) 0%, transparent 60%), #070712" }}>
      {/* Logo */}
      <div className="h-16 flex items-center px-5 border-b border-border">
        <Link href="/" className="flex items-center gap-2 group">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center transition-transform group-hover:scale-105" style={{ background: "linear-gradient(135deg, #7c3aed, #e879f9)" }}>
            <Pin size={16} className="text-white" />
          </div>
          <span className="font-display font-bold text-white">PinForge <span className="text-primary-light">AI</span></span>
        </Link>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-5 overflow-y-auto">
        <div className="space-y-1">
          {navItems.map(({ label, href, icon: Icon }) => {
            const active = pathname === href;
            return (
              <Link key={href} href={href}>
                <motion.div
                  whileHover={{ x: 2 }}
                  className={cn(
                    "flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-body transition-all duration-200 group relative",
                    active
                      ? "bg-primary/15 border border-primary/30 text-white"
                      : "text-text-muted hover:text-white hover:bg-bg-elevated"
                  )}
                >
                  {active && (
                    <motion.div layoutId="sidebar-active" className="absolute left-0 top-0 bottom-0 w-1 rounded-r-full" style={{ background: "linear-gradient(to bottom, #7c3aed, #e879f9)" }} />
                  )}
                  <Icon size={18} className={active ? "text-primary-light" : "text-text-dim group-hover:text-text-muted"} />
                  <span className="flex-1">{label}</span>
                  {active && <ChevronRight size={14} className="text-primary-light opacity-60" />}
                </motion.div>
              </Link>
            );
          })}
        </div>
      </nav>

      {/* Footer */}
      <div className="p-3 border-t border-border">
        <button onClick={handleLogout}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-body text-text-muted hover:text-accent-red hover:bg-accent-red/10 transition-all duration-200">
          <LogOut size={18} />
          <span>Log out</span>
        </button>
      </div>
    </aside>
  );
}
