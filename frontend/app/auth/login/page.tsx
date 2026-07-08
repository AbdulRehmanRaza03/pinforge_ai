"use client";
import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Pin, Mail, Lock, ArrowRight, Loader2 } from "lucide-react";
import { supabase } from "@/lib/supabase";
import toast from "react-hot-toast";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    const { error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) {
      toast.error(error.message);
    } else {
      toast.success("Welcome back!");
      router.push("/dashboard");
    }
    setLoading(false);
  }

  return (
    <div className="min-h-screen bg-bg flex items-center justify-center px-6 relative overflow-hidden">
      <div className="hero-blob-1" style={{ top: "-300px", right: "-200px" }} />
      <div className="hero-blob-2" style={{ bottom: "-200px", left: "-200px" }} />

      <motion.div
        initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}
        className="relative z-10 w-full max-w-md"
      >
        {/* Logo */}
        <div className="flex items-center gap-2 justify-center mb-8">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: "linear-gradient(135deg, #7c3aed, #e879f9)" }}>
            <Pin size={20} className="text-white" />
          </div>
          <span className="font-display font-bold text-2xl text-white">PinForge <span className="text-primary-light">AI</span></span>
        </div>

        <div className="glass-card p-8">
          <h1 className="font-display text-2xl font-bold text-white mb-2">Welcome back</h1>
          <p className="text-text-muted font-body text-sm mb-8">Log in to your PinForge AI account</p>

          <form onSubmit={handleLogin} className="space-y-5">
            <div>
              <label className="block text-sm font-body text-text-muted mb-2">Email</label>
              <div className="relative">
                <Mail size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-dim" />
                <input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="you@example.com"
                  className="input-field pl-10" required />
              </div>
            </div>
            <div>
              <label className="block text-sm font-body text-text-muted mb-2">Password</label>
              <div className="relative">
                <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-dim" />
                <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="••••••••"
                  className="input-field pl-10" required />
              </div>
            </div>
            <button type="submit" disabled={loading} className="btn-primary w-full flex items-center justify-center gap-2 py-3">
              {loading ? <Loader2 size={18} className="animate-spin" /> : <><span>Log in</span><ArrowRight size={16} /></>}
            </button>
          </form>

          <div className="mt-6 pt-6 border-t border-border text-center">
            <p className="text-text-muted text-sm font-body">
              Don't have an account?{" "}
              <Link href="/auth/signup" className="text-primary-light hover:text-accent-fuchsia transition-colors font-medium">Sign up free</Link>
            </p>
          </div>
        </div>

        <p className="text-center text-text-dim text-xs font-body mt-6">
          <Link href="/" className="hover:text-text-muted transition-colors">← Back to PinForge AI</Link>
        </p>
      </motion.div>
    </div>
  );
}
