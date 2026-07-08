"use client";
import { useEffect, useState } from "react";
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell
} from "recharts";
import { TrendingUp, CheckCircle2, Clock, AlertCircle, Pin } from "lucide-react";
import Header from "@/components/layout/Header";
import StatsCard from "@/components/ui/StatsCard";
import { listAccounts, getAnalytics, getHistory } from "@/lib/api";
import type { AnalyticsOverview, HistoryItem, PinterestAccount } from "@/types";
import { formatDate, statusColor, truncate } from "@/lib/utils";

export default function AnalyticsPage() {
  const [accounts, setAccounts] = useState<PinterestAccount[]>([]);
  const [activeAccount, setActiveAccount] = useState<number | null>(null);
  const [analytics, setAnalytics] = useState<AnalyticsOverview | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    listAccounts().then(r => {
      setAccounts(r.data);
      if (r.data.length > 0) setActiveAccount(r.data[0].id);
    });
  }, []);

  useEffect(() => {
    if (!activeAccount) return;
    setLoading(true);
    Promise.all([getAnalytics(activeAccount), getHistory(activeAccount, 30)])
      .then(([a, h]) => { setAnalytics(a.data); setHistory(h.data); })
      .finally(() => setLoading(false));
  }, [activeAccount]);

  const successRate = analytics
    ? Math.round((analytics.posted_week / Math.max(analytics.posted_week + analytics.failed_week, 1)) * 100)
    : 0;

  return (
    <div className="min-h-screen">
      <Header title="Analytics" />
      <div className="p-6 max-w-6xl mx-auto">

        {/* Account selector */}
        {accounts.length > 1 && (
          <div className="flex gap-2 mb-6 flex-wrap">
            {accounts.map(a => (
              <button key={a.id} onClick={() => setActiveAccount(a.id)}
                className={`px-4 py-1.5 rounded-lg text-sm font-body border transition-all duration-200 ${activeAccount === a.id ? "bg-primary/20 border-primary/50 text-white" : "bg-bg-elevated border-border text-text-muted hover:border-primary/30"}`}>
                @{a.username}
              </button>
            ))}
          </div>
        )}

        {analytics ? (
          <>
            {/* Stats row */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
              <StatsCard label="Posted Today"  value={analytics.posted_today}  icon={CheckCircle2}  color="green"  index={0} />
              <StatsCard label="This Month"    value={analytics.posted_month}  icon={TrendingUp}    color="cyan"   index={1} />
              <StatsCard label="Queued"        value={analytics.queued}        icon={Clock}         color="violet" index={2} />
              <StatsCard label="Success Rate"  value={`${successRate}%`}       icon={Pin}           color="gold"   subtitle="last 7 days" index={3} />
            </div>

            {/* Area chart */}
            <div className="glass-card p-6 mb-6">
              <h2 className="font-display font-semibold text-white mb-1">Daily pins — last 8 days</h2>
              <p className="text-text-muted text-sm font-body mb-6">Posting activity trend</p>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={analytics.daily_chart} margin={{ top: 4, right: 8, bottom: 0, left: -20 }}>
                    <defs>
                      <linearGradient id="grad1" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%"  stopColor="#9333ea" stopOpacity={0.5} />
                        <stop offset="95%" stopColor="#9333ea" stopOpacity={0}   />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                    <XAxis dataKey="date" tick={{ fill: "#64748b", fontSize: 11, fontFamily: "DM Sans" }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fill: "#64748b", fontSize: 11, fontFamily: "DM Sans" }} axisLine={false} tickLine={false} allowDecimals={false} />
                    <Tooltip contentStyle={{ background: "#0d0d1f", border: "1px solid rgba(147,51,234,0.3)", borderRadius: "12px", fontFamily: "DM Sans", color: "#f8fafc" }} />
                    <Area type="monotone" dataKey="pins" stroke="#9333ea" strokeWidth={2} fill="url(#grad1)" dot={{ fill: "#9333ea", r: 3 }} activeDot={{ r: 5, fill: "#e879f9" }} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Bar chart */}
            <div className="glass-card p-6 mb-6">
              <h2 className="font-display font-semibold text-white mb-1">Pins by day of week</h2>
              <p className="text-text-muted text-sm font-body mb-6">Where activity concentrates</p>
              <div className="h-52">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={analytics.daily_chart} margin={{ top: 4, right: 8, bottom: 0, left: -20 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                    <XAxis dataKey="date" tick={{ fill: "#64748b", fontSize: 11, fontFamily: "DM Sans" }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fill: "#64748b", fontSize: 11, fontFamily: "DM Sans" }} axisLine={false} tickLine={false} allowDecimals={false} />
                    <Tooltip contentStyle={{ background: "#0d0d1f", border: "1px solid rgba(147,51,234,0.3)", borderRadius: "12px", fontFamily: "DM Sans", color: "#f8fafc" }} />
                    <Bar dataKey="pins" radius={[6, 6, 0, 0]}>
                      {analytics.daily_chart.map((_, i) => (
                        <Cell key={i} fill={i === analytics.daily_chart.length - 1 ? "#e879f9" : "#7c3aed"} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Safety info */}
            <div className="glass-card p-5 mb-6 flex items-center gap-4 border-primary/30">
              <div className="w-10 h-10 rounded-xl bg-primary/15 flex items-center justify-center flex-shrink-0">
                <CheckCircle2 size={20} className="text-primary-light" />
              </div>
              <div>
                <p className="font-display font-semibold text-white text-sm">Safety enforcement active</p>
                <p className="text-text-muted text-xs font-body">Daily cap: {analytics["from config"].max_per_day} pins · Randomized 15–60 min delays · Duplicate content blocked</p>
              </div>
            </div>
          </>
        ) : !loading && (
          <div className="glass-card p-12 text-center">
            <AlertCircle size={40} className="text-text-dim mx-auto mb-3" />
            <p className="text-text-muted font-body">No analytics yet. Post some pins to see data here.</p>
          </div>
        )}

        {/* History log */}
        {history.length > 0 && (
          <div className="glass-card p-5">
            <h2 className="font-display font-semibold text-white mb-4">Recent activity log</h2>
            <div className="space-y-2">
              {history.map((h, i) => (
                <div key={h.id} className="flex items-center gap-3 py-2.5 border-b border-border/50 last:border-0">
                  <span className={statusColor(h.status)}>{h.status}</span>
                  <p className="flex-1 text-sm font-body text-text-muted truncate">{truncate(h.title || "–", 50)}</p>
                  <p className="text-xs font-mono text-text-dim flex-shrink-0">{h.board_name}</p>
                  <p className="text-xs font-mono text-text-dim flex-shrink-0">{formatDate(h.occurred_at)}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
