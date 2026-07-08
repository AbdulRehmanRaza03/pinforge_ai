"use client";
import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Clock, Trash2, RefreshCw, Calendar, Link as LinkIcon, AlertCircle, CheckCircle2, Filter } from "lucide-react";
import Header from "@/components/layout/Header";
import { listAccounts, getQueue, removeFromQueue } from "@/lib/api";
import type { PinterestAccount, QueueItem } from "@/types";
import { statusColor, formatDate, timeFromNow, truncate } from "@/lib/utils";
import toast from "react-hot-toast";

const STATUS_FILTERS = ["all", "scheduled", "posted", "failed", "duplicate"];

export default function QueuePage() {
  const [accounts, setAccounts] = useState<PinterestAccount[]>([]);
  const [activeAccount, setActiveAccount] = useState<number | null>(null);
  const [items, setItems] = useState<QueueItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    listAccounts().then(r => {
      setAccounts(r.data);
      if (r.data.length > 0) setActiveAccount(r.data[0].id);
    });
  }, []);

  async function fetchQueue() {
    if (!activeAccount) return;
    setLoading(true);
    try {
      const { data } = await getQueue(activeAccount);
      setItems(data);
    } catch { toast.error("Failed to load queue."); }
    setLoading(false);
  }

  useEffect(() => { fetchQueue(); }, [activeAccount]);

  async function handleRemove(id: number) {
    try {
      await removeFromQueue(id);
      setItems(prev => prev.filter(i => i.id !== id));
      toast.success("Removed from queue.");
    } catch (e: any) {
      toast.error(e.response?.data?.detail || "Cannot remove — already processed.");
    }
  }

  const filtered = filter === "all" ? items : items.filter(i => i.status === filter);
  const counts = STATUS_FILTERS.slice(1).reduce((acc, s) => {
    acc[s] = items.filter(i => i.status === s).length; return acc;
  }, {} as Record<string, number>);

  return (
    <div className="min-h-screen">
      <Header title="Queue" />
      <div className="p-6 max-w-5xl mx-auto">

        {/* Account selector + refresh */}
        <div className="flex flex-wrap items-center gap-3 mb-6">
          {accounts.length > 1 && accounts.map(a => (
            <button key={a.id} onClick={() => setActiveAccount(a.id)}
              className={`px-4 py-1.5 rounded-lg text-sm font-body border transition-all duration-200 ${activeAccount === a.id ? "bg-primary/20 border-primary/50 text-white" : "bg-bg-elevated border-border text-text-muted hover:border-primary/30"}`}>
              @{a.username}
            </button>
          ))}
          <button onClick={fetchQueue} disabled={loading}
            className="ml-auto btn-ghost flex items-center gap-2 text-sm">
            <RefreshCw size={14} className={loading ? "animate-spin" : ""} /> Refresh
          </button>
        </div>

        {/* Summary stat chips */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-6">
          <div className="glass-card p-3 text-center">
            <p className="font-display font-bold text-2xl text-white">{items.length}</p>
            <p className="text-text-dim text-xs font-body">Total</p>
          </div>
          {STATUS_FILTERS.slice(1).map(s => (
            <div key={s} className="glass-card p-3 text-center">
              <p className={`font-display font-bold text-2xl ${s === "posted" ? "text-accent-green" : s === "failed" ? "text-accent-red" : s === "scheduled" ? "text-primary-light" : "text-text-muted"}`}>{counts[s] ?? 0}</p>
              <p className="text-text-dim text-xs font-body capitalize">{s}</p>
            </div>
          ))}
        </div>

        {/* Filters */}
        <div className="flex items-center gap-2 mb-4 flex-wrap">
          <Filter size={14} className="text-text-dim" />
          {STATUS_FILTERS.map(s => (
            <button key={s} onClick={() => setFilter(s)}
              className={`px-3 py-1 rounded-lg text-xs font-body border transition-all duration-200 ${filter === s ? "bg-primary/20 border-primary/50 text-white" : "bg-bg-elevated border-border text-text-muted hover:border-primary/30"}`}>
              {s === "all" ? "All" : s.charAt(0).toUpperCase() + s.slice(1)}
            </button>
          ))}
        </div>

        {/* Queue list */}
        {!activeAccount ? (
          <div className="glass-card p-12 text-center">
            <AlertCircle size={40} className="text-text-dim mx-auto mb-3" />
            <p className="text-text-muted font-body">Connect a Pinterest account to view queue.</p>
          </div>
        ) : filtered.length === 0 ? (
          <div className="glass-card p-12 text-center">
            <Clock size={40} className="text-text-dim mx-auto mb-3" />
            <p className="text-text-muted font-body">{filter === "all" ? "Queue is empty. Create some pins to get started." : `No ${filter} pins.`}</p>
          </div>
        ) : (
          <div className="space-y-3">
            <AnimatePresence>
              {filtered.map((item, i) => (
                <motion.div key={item.id}
                  initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, x: -20 }}
                  transition={{ delay: i * 0.04 }}
                  className="glass-card p-4 flex items-start gap-4 group hover:border-primary/30 transition-all duration-200">

                  {/* Status indicator */}
                  <div className={`w-2 h-2 rounded-full mt-2 flex-shrink-0 ${item.status === "posted" ? "bg-accent-green shadow-[0_0_8px_rgba(16,185,129,0.6)]" : item.status === "failed" ? "bg-accent-red" : item.status === "scheduled" ? "bg-primary animate-pulse" : "bg-text-dim"}`} />

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex flex-wrap items-center gap-2 mb-1">
                      <p className="font-display font-semibold text-white text-sm">{truncate(item.title, 60)}</p>
                      <span className={statusColor(item.status)}>{item.status}</span>
                    </div>
                    <p className="text-text-muted text-xs font-body mb-2 line-clamp-2">{item.description}</p>
                    <div className="flex flex-wrap items-center gap-3 text-xs text-text-dim font-body">
                      {item.board_name && <span className="flex items-center gap-1">📋 {item.board_name}</span>}
                      {item.destination_link && (
                        <a href={item.destination_link} target="_blank" rel="noopener noreferrer"
                          className="flex items-center gap-1 text-accent-cyan hover:underline">
                          <LinkIcon size={10} /> {truncate(item.destination_link, 35)}
                        </a>
                      )}
                      {item.scheduled_for && item.status === "scheduled" && (
                        <span className="flex items-center gap-1 text-primary-light">
                          <Calendar size={10} /> Posts {timeFromNow(item.scheduled_for)}
                        </span>
                      )}
                      {item.posted_at && (
                        <span className="flex items-center gap-1 text-accent-green">
                          <CheckCircle2 size={10} /> Posted {timeFromNow(item.posted_at)}
                        </span>
                      )}
                    </div>
                    {item.error_message && (
                      <p className="mt-2 text-xs text-accent-red font-body flex items-center gap-1">
                        <AlertCircle size={10} /> {item.error_message}
                      </p>
                    )}
                  </div>

                  {/* Actions */}
                  {(item.status === "scheduled" || item.status === "queued") && (
                    <button onClick={() => handleRemove(item.id)}
                      className="opacity-0 group-hover:opacity-100 p-2 rounded-lg hover:bg-accent-red/15 hover:text-accent-red text-text-dim transition-all duration-200">
                      <Trash2 size={16} />
                    </button>
                  )}
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}
      </div>
    </div>
  );
}
