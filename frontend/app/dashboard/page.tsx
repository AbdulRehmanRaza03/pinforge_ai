"use client";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from "recharts";
import {
  Pin, Clock, TrendingUp, AlertCircle, Zap, ArrowRight, CheckCircle2
} from "lucide-react";
import Link from "next/link";
import Header from "@/components/layout/Header";
import StatsCard from "@/components/ui/StatsCard";
import { getAnalytics, listAccounts } from "@/lib/api";
import { formatDate, statusColor } from "@/lib/utils";
import type { AnalyticsOverview, PinterestAccount } from "@/types";

export default function DashboardPage() {
  const [accounts, setAccounts] = useState<PinterestAccount[]>([]);
  const [activeAccount, setActiveAccount] = useState<number | null>(null);
  const [analytics, setAnalytics] = useState<AnalyticsOverview | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listAccounts().then(r => {
      setAccounts(r.data);
      if (r.data.length > 0) setActiveAccount(r.data[0].id);
    }).catch(() => {});
  }, []);

  useEffect(() => {
    if (!activeAccount) { setLoading(false); return; }
    setLoading(true);
    getAnalytics(activeAccount).then(r => setAnalytics(r.data)).finally(() => setLoading(false));
  }, [activeAccount]);

  const noAccounts = accounts.length === 0;

  return (
    <div className="min-h-screen">
      <Header title="Dashboard" />
      <div className="p-6 max-w-7xl mx-auto">

        {/* No accounts CTA */}
        {noAccounts && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
            className="gradient-border p-6 mb-8 flex flex-col md:flex-row items-center gap-6"
            style={{ background: "linear-gradient(135deg, rgba(147,51,234,0.08), rgba(232,121,249,0.05))" }}>
            <div className="w-14 h-14 rounded-2xl flex items-center justify-center flex-shrink-0"
              style={{ background: "linear-gradient(135deg, #7c3aed, #e879f9)" }}>
              <Pin size={24} className="text-white" />
            </div>
            <div className="flex-1 text-center md:text-left">
              <h2 className="font-display text-xl font-bold text-white mb-1">Connect your first Pinterest account</h2>
              <p className="text-text-muted font-body text-sm">Link your Pinterest business account to start scheduling and automating pins with AI.</p>
            </div>
            <Link href="/dashboard/accounts" className="btn-primary flex items-center gap-2 flex-shrink-0">
              Connect Pinterest <ArrowRight size={16} />
            </Link>
          </motion.div>
        )}

        {/* Account selector */}
        {accounts.length > 1 && (
          <div className="flex items-center gap-3 mb-6">
            <span className="text-text-muted text-sm font-body">Account:</span>
            <div className="flex gap-2 flex-wrap">
              {accounts.map(a => (
                <button key={a.id} onClick={() => setActiveAccount(a.id)}
                  className={`px-4 py-1.5 rounded-lg text-sm font-body transition-all duration-200 border ${activeAccount === a.id ? "bg-primary/20 border-primary/50 text-white" : "bg-bg-elevated border-border text-text-muted hover:border-primary/30 hover:text-white"}`}>
                  @{a.username}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Stats grid */}
        {analytics && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <StatsCard label="Posted Today"   value={analytics.posted_today}  icon={CheckCircle2} color="green"  subtitle={`cap: ${analytics["from config"].max_per_day}/day`} index={0} />
            <StatsCard label="Queued"          value={analytics.queued}        icon={Clock}        color="violet" subtitle="waiting to post"  index={1} />
            <StatsCard label="This Week"       value={analytics.posted_week}   icon={TrendingUp}   color="cyan"   subtitle="pins posted"      index={2} />
            <StatsCard label="Failed (7d)"     value={analytics.failed_week}   icon={AlertCircle}  color="red"    subtitle="check history"    index={3} />
          </div>
        )}

        {!analytics && !loading && !noAccounts && (
          <div className="glass-card p-8 text-center mb-8">
            <p className="text-text-muted font-body">No analytics data yet. Start by creating some pins.</p>
            <Link href="/dashboard/create" className="btn-primary inline-flex mt-4 gap-2 items-center"><Zap size={16} /> Create first pin</Link>
          </div>
        )}

        {/* Chart */}
        {analytics && analytics.daily_chart.length > 0 && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}
            className="glass-card p-6 mb-8">
            <h2 className="font-display font-semibold text-white mb-1">Pins posted — last 8 days</h2>
            <p className="text-text-muted text-sm font-body mb-6">Daily posting activity across this account</p>
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={analytics.daily_chart} margin={{ top: 4, right: 8, bottom: 0, left: -20 }}>
                  <defs>
                    <linearGradient id="chartGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#9333ea" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#9333ea" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="date" tick={{ fill: "#64748b", fontSize: 11, fontFamily: "DM Sans" }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: "#64748b", fontSize: 11, fontFamily: "DM Sans" }} axisLine={false} tickLine={false} allowDecimals={false} />
                  <Tooltip
                    contentStyle={{ background: "#0d0d1f", border: "1px solid rgba(147,51,234,0.3)", borderRadius: "12px", fontFamily: "DM Sans", color: "#f8fafc" }}
                    cursor={{ stroke: "rgba(147,51,234,0.3)" }}
                  />
                  <Area type="monotone" dataKey="pins" stroke="#9333ea" strokeWidth={2} fill="url(#chartGrad)" dot={{ fill: "#9333ea", r: 3 }} activeDot={{ r: 5, fill: "#e879f9" }} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </motion.div>
        )}

        {/* Quick actions */}
        <div className="grid md:grid-cols-3 gap-4">
          {[
            { icon: Zap, label: "Create Pins", desc: "Upload images + AI content", href: "/dashboard/create", color: "#9333ea", grad: "linear-gradient(135deg, #7c3aed, #9333ea)" },
            { icon: Clock, label: "View Queue", desc: "Manage scheduled pins", href: "/dashboard/queue", color: "#06b6d4", grad: "linear-gradient(135deg, #0891b2, #06b6d4)" },
            { icon: TrendingUp, label: "Analytics", desc: "Track posting performance", href: "/dashboard/analytics", color: "#f59e0b", grad: "linear-gradient(135deg, #d97706, #f59e0b)" },
          ].map(({ icon: Icon, label, desc, href, color, grad }, i) => (
            <motion.div key={label} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 + i * 0.1 }}>
              <Link href={href} className="glass-card p-5 flex items-center gap-4 group hover:border-primary/40 transition-all duration-300 block">
                <div className="w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0 group-hover:scale-105 transition-transform" style={{ background: grad }}>
                  <Icon size={20} className="text-white" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-display font-semibold text-white text-sm">{label}</p>
                  <p className="text-text-dim text-xs font-body">{desc}</p>
                </div>
                <ArrowRight size={16} className="text-text-dim group-hover:text-primary-light group-hover:translate-x-1 transition-all duration-200" />
              </Link>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
