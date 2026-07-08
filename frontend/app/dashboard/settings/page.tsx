"use client";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Key, User, Shield, Loader2, Save, Eye, EyeOff, CheckCircle2 } from "lucide-react";
import Header from "@/components/layout/Header";
import { getSettings, updateSettings } from "@/lib/api";
import toast from "react-hot-toast";
import { cn } from "@/lib/utils";

const AI_PROVIDERS = [
  { id: "gemini",   label: "Google Gemini", desc: "Free tier available — Gemini 1.5 Flash", link: "https://aistudio.google.com/app/apikey" },
  { id: "openai",   label: "OpenAI",        desc: "GPT-4o Mini — fast and affordable",      link: "https://platform.openai.com/api-keys" },
  { id: "deepseek", label: "DeepSeek",      desc: "Cost-effective alternative to GPT",      link: "https://platform.deepseek.com" },
];

export default function SettingsPage() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({ full_name: "", ai_provider: "gemini", gemini_key: "", openai_key: "" });
  const [has, setHas] = useState({ gemini: false, openai: false });
  const [showKeys, setShowKeys] = useState({ gemini: false, openai: false });

  useEffect(() => {
    getSettings().then(r => {
      const d = r.data;
      setForm(f => ({ ...f, full_name: d.full_name || "", ai_provider: d.ai_provider || "gemini" }));
      setHas({ gemini: d.has_gemini_key, openai: d.has_openai_key });
    }).finally(() => setLoading(false));
  }, []);

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      await updateSettings({
        full_name: form.full_name,
        ai_provider: form.ai_provider,
        gemini_key: form.gemini_key || undefined,
        openai_key: form.openai_key || undefined,
      });
      toast.success("Settings saved.");
      setHas({ gemini: has.gemini || !!form.gemini_key, openai: has.openai || !!form.openai_key });
      setForm(f => ({ ...f, gemini_key: "", openai_key: "" }));
    } catch { toast.error("Failed to save settings."); }
    setSaving(false);
  }

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center">
      <Loader2 size={28} className="animate-spin text-primary" />
    </div>
  );

  return (
    <div className="min-h-screen">
      <Header title="Settings" />
      <div className="p-6 max-w-2xl mx-auto">
        <form onSubmit={handleSave} className="space-y-6">

          {/* Profile */}
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-6">
            <div className="flex items-center gap-3 mb-5">
              <div className="w-9 h-9 rounded-xl bg-primary/15 flex items-center justify-center">
                <User size={18} className="text-primary-light" />
              </div>
              <h2 className="font-display font-semibold text-white">Profile</h2>
            </div>
            <div>
              <label className="block text-sm font-body text-text-muted mb-2">Display name</label>
              <input value={form.full_name} onChange={e => setForm(f => ({ ...f, full_name: e.target.value }))}
                placeholder="Your name" className="input-field" />
            </div>
          </motion.div>

          {/* AI Provider */}
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="glass-card p-6">
            <div className="flex items-center gap-3 mb-5">
              <div className="w-9 h-9 rounded-xl bg-accent-fuchsia/10 flex items-center justify-center">
                <Key size={18} className="text-accent-fuchsia" />
              </div>
              <div>
                <h2 className="font-display font-semibold text-white">AI Provider & API Keys</h2>
                <p className="text-text-dim text-xs font-body">Your keys are used only for your account's AI generation.</p>
              </div>
            </div>

            {/* Provider select */}
            <div className="grid grid-cols-3 gap-3 mb-6">
              {AI_PROVIDERS.map(p => (
                <button key={p.id} type="button" onClick={() => setForm(f => ({ ...f, ai_provider: p.id }))}
                  className={cn("p-3 rounded-xl border text-left transition-all duration-200",
                    form.ai_provider === p.id ? "bg-primary/15 border-primary/50" : "bg-bg-elevated border-border hover:border-primary/30")}>
                  <p className={cn("font-display font-semibold text-sm mb-0.5", form.ai_provider === p.id ? "text-white" : "text-text-muted")}>{p.label}</p>
                  <p className="text-text-dim text-[10px] font-body">{p.desc}</p>
                </button>
              ))}
            </div>

            {/* API key inputs */}
            <div className="space-y-4">
              {/* Gemini */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-sm font-body text-text-muted flex items-center gap-2">
                    Gemini API Key
                    {has.gemini && <span className="badge-posted">Saved</span>}
                  </label>
                  <a href="https://aistudio.google.com/app/apikey" target="_blank" rel="noopener noreferrer"
                    className="text-xs text-accent-cyan hover:underline font-body">Get key →</a>
                </div>
                <div className="relative">
                  <input type={showKeys.gemini ? "text" : "password"}
                    value={form.gemini_key} onChange={e => setForm(f => ({ ...f, gemini_key: e.target.value }))}
                    placeholder={has.gemini ? "••••••••••••  (leave blank to keep existing)" : "AIzaSy…"}
                    className="input-field pr-10 font-mono text-sm" />
                  <button type="button" onClick={() => setShowKeys(s => ({ ...s, gemini: !s.gemini }))}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-text-dim hover:text-text-muted">
                    {showKeys.gemini ? <EyeOff size={14} /> : <Eye size={14} />}
                  </button>
                </div>
              </div>

              {/* OpenAI */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-sm font-body text-text-muted flex items-center gap-2">
                    OpenAI API Key
                    {has.openai && <span className="badge-posted">Saved</span>}
                  </label>
                  <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer"
                    className="text-xs text-accent-cyan hover:underline font-body">Get key →</a>
                </div>
                <div className="relative">
                  <input type={showKeys.openai ? "text" : "password"}
                    value={form.openai_key} onChange={e => setForm(f => ({ ...f, openai_key: e.target.value }))}
                    placeholder={has.openai ? "••••••••••••  (leave blank to keep existing)" : "sk-…"}
                    className="input-field pr-10 font-mono text-sm" />
                  <button type="button" onClick={() => setShowKeys(s => ({ ...s, openai: !s.openai }))}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-text-dim hover:text-text-muted">
                    {showKeys.openai ? <EyeOff size={14} /> : <Eye size={14} />}
                  </button>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Safety info */}
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="glass-card p-5">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-9 h-9 rounded-xl bg-accent-green/10 flex items-center justify-center">
                <Shield size={18} className="text-accent-green" />
              </div>
              <h2 className="font-display font-semibold text-white">Safety Settings (read-only)</h2>
            </div>
            <div className="space-y-3">
              {[
                { label: "Max pins per account per day", value: "15 pins (hard cap)" },
                { label: "Delay between posts", value: "15–60 minutes (randomized)" },
                { label: "Duplicate content", value: "Blocked by content hash" },
                { label: "API method", value: "Official Pinterest API v5 only" },
              ].map(({ label, value }) => (
                <div key={label} className="flex items-center justify-between py-2 border-b border-border/50 last:border-0">
                  <span className="text-text-muted text-sm font-body">{label}</span>
                  <span className="text-xs font-mono text-accent-green bg-accent-green/10 px-2 py-1 rounded-lg border border-accent-green/20">{value}</span>
                </div>
              ))}
            </div>
            <p className="text-text-dim text-xs font-body mt-3">Safety limits are enforced server-side and cannot be changed via the UI.</p>
          </motion.div>

          {/* Save */}
          <button type="submit" disabled={saving} className="btn-primary w-full flex items-center justify-center gap-2 py-3">
            {saving ? <Loader2 size={16} className="animate-spin" /> : <Save size={16} />}
            Save Settings
          </button>
        </form>
      </div>
    </div>
  );
}
