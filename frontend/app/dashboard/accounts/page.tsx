"use client";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Users, Plus, Trash2, CheckCircle2, ExternalLink, Loader2, AlertTriangle } from "lucide-react";
import Header from "@/components/layout/Header";
import { listAccounts, getAuthUrl, deleteAccount } from "@/lib/api";
import type { PinterestAccount } from "@/types";
import { formatDate } from "@/lib/utils";
import toast from "react-hot-toast";

export default function AccountsPage() {
  const [accounts, setAccounts] = useState<PinterestAccount[]>([]);
  const [loading, setLoading] = useState(true);
  const [connecting, setConnecting] = useState(false);
  const [disconnecting, setDisconnecting] = useState<number | null>(null);

  useEffect(() => {
    // Handle callback success/error from Pinterest OAuth redirect
    const params = new URLSearchParams(window.location.search);
    if (params.get("connected") === "1") {
      toast.success("Pinterest account connected!");
      window.history.replaceState({}, "", window.location.pathname);
    }
    if (params.get("error")) {
      toast.error(`Connection failed: ${params.get("error")}`);
      window.history.replaceState({}, "", window.location.pathname);
    }
    fetchAccounts();
  }, []);

  async function fetchAccounts() {
    setLoading(true);
    try {
      const { data } = await listAccounts();
      setAccounts(data);
    } catch { toast.error("Failed to load accounts."); }
    setLoading(false);
  }

  async function handleConnect() {
    setConnecting(true);
    try {
      const { data } = await getAuthUrl();
      window.location.href = data.url;  // redirect to Pinterest OAuth
    } catch { toast.error("Failed to start Pinterest connection."); setConnecting(false); }
  }

  async function handleDisconnect(id: number) {
    setDisconnecting(id);
    try {
      await deleteAccount(id);
      setAccounts(prev => prev.filter(a => a.id !== id));
      toast.success("Account disconnected.");
    } catch { toast.error("Failed to disconnect."); }
    setDisconnecting(null);
  }

  return (
    <div className="min-h-screen">
      <Header title="Accounts" />
      <div className="p-6 max-w-3xl mx-auto">

        {/* Header card */}
        <div className="glass-card p-6 mb-6 flex flex-col md:flex-row md:items-center gap-4">
          <div className="flex-1">
            <h2 className="font-display text-xl font-bold text-white mb-1">Pinterest Accounts</h2>
            <p className="text-text-muted text-sm font-body">Connect your Pinterest business accounts using the official OAuth2 flow. Each account is secured with its own access token.</p>
          </div>
          <button onClick={handleConnect} disabled={connecting}
            className="btn-primary flex items-center gap-2 flex-shrink-0">
            {connecting ? <Loader2 size={16} className="animate-spin" /> : <Plus size={16} />}
            Connect Pinterest
          </button>
        </div>

        {/* Safety notice */}
        <div className="flex items-start gap-3 p-4 rounded-xl mb-6 border border-accent-gold/30 bg-accent-gold/5">
          <CheckCircle2 size={18} className="text-accent-gold flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-accent-gold text-sm font-display font-semibold mb-0.5">Official OAuth2 only</p>
            <p className="text-text-muted text-xs font-body">PinForge AI uses only the official Pinterest API v5. Your credentials never touch our servers — we only store the OAuth access token Pinterest provides.</p>
          </div>
        </div>

        {/* Accounts list */}
        {loading ? (
          <div className="glass-card p-12 flex items-center justify-center gap-3">
            <Loader2 size={24} className="animate-spin text-primary" />
            <p className="text-text-muted font-body">Loading accounts…</p>
          </div>
        ) : accounts.length === 0 ? (
          <div className="glass-card p-12 text-center">
            <Users size={48} className="text-text-dim mx-auto mb-4" />
            <h3 className="font-display font-semibold text-white mb-2">No accounts connected yet</h3>
            <p className="text-text-muted text-sm font-body mb-6">Connect your Pinterest business account to start automating pins.</p>
            <button onClick={handleConnect} disabled={connecting} className="btn-primary flex items-center gap-2 mx-auto">
              {connecting ? <Loader2 size={16} className="animate-spin" /> : <Plus size={16} />}
              Connect Pinterest Account
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {accounts.map((account, i) => (
              <motion.div key={account.id} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }}
                className="glass-card p-5 flex items-center gap-4 group hover:border-primary/30 transition-all duration-200">

                {/* Avatar */}
                <div className="flex-shrink-0">
                  {account.profile_image ? (
                    <img src={account.profile_image} alt={account.username} className="w-12 h-12 rounded-full object-cover border-2 border-primary/30" />
                  ) : (
                    <div className="w-12 h-12 rounded-full flex items-center justify-center font-display font-bold text-white text-lg" style={{ background: "linear-gradient(135deg, #7c3aed, #e879f9)" }}>
                      {account.username?.[0]?.toUpperCase() ?? "P"}
                    </div>
                  )}
                </div>

                {/* Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-0.5">
                    <p className="font-display font-semibold text-white">@{account.username}</p>
                    <span className="flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-full bg-accent-green/15 text-accent-green border border-accent-green/25 font-mono">
                      <CheckCircle2 size={8} /> Connected
                    </span>
                  </div>
                  {account.display_name && account.display_name !== account.username && (
                    <p className="text-text-muted text-sm font-body truncate">{account.display_name}</p>
                  )}
                  <p className="text-text-dim text-xs font-body mt-0.5">Connected {formatDate(account.connected_at)}</p>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-all duration-200">
                  <a href={`https://pinterest.com/${account.username}`} target="_blank" rel="noopener noreferrer"
                    className="p-2 rounded-lg hover:bg-bg-elevated text-text-dim hover:text-primary-light transition-all duration-200">
                    <ExternalLink size={16} />
                  </a>
                  <button onClick={() => handleDisconnect(account.id)} disabled={disconnecting === account.id}
                    className="p-2 rounded-lg hover:bg-accent-red/10 text-text-dim hover:text-accent-red transition-all duration-200">
                    {disconnecting === account.id ? <Loader2 size={16} className="animate-spin" /> : <Trash2 size={16} />}
                  </button>
                </div>
              </motion.div>
            ))}

            {/* Add more */}
            <button onClick={handleConnect} disabled={connecting}
              className="w-full glass-card p-4 flex items-center justify-center gap-3 border-dashed hover:border-primary/40 hover:bg-primary/5 transition-all duration-200 text-text-muted hover:text-white font-body text-sm">
              {connecting ? <Loader2 size={16} className="animate-spin" /> : <Plus size={16} />}
              Connect another Pinterest account
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
