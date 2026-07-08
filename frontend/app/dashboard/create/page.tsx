"use client";
import { useCallback, useEffect, useState } from "react";
import { useDropzone } from "react-dropzone";
import { motion, AnimatePresence } from "framer-motion";
import {
  Upload, Sparkles, X, Loader2, Plus, Link as LinkIcon,
  Image as ImageIcon, CheckCircle2, AlertCircle, Clock
} from "lucide-react";
import Header from "@/components/layout/Header";
import { listAccounts, listBoards, createBoard, generateContent, addToQueue } from "@/lib/api";
import type { PinterestAccount, Board, AIContent } from "@/types";
import toast from "react-hot-toast";
import { cn } from "@/lib/utils";

const AI_PROVIDERS = [
  { id: "gemini", label: "Gemini Flash", free: true },
  { id: "openai", label: "GPT-4o Mini", free: false },
  { id: "deepseek", label: "DeepSeek", free: false },
];

interface UploadedFile { file: File; preview: string; id: string; }
interface PinForm { title: string; description: string; hashtags: string; alt_text: string; }

export default function CreatePage() {
  const [accounts, setAccounts] = useState<PinterestAccount[]>([]);
  const [boards, setBoards] = useState<Board[]>([]);
  const [selectedAccount, setSelectedAccount] = useState<number | null>(null);
  const [selectedBoard, setSelectedBoard] = useState<string>("");
  const [selectedBoardName, setSelectedBoardName] = useState<string>("");
  const [newBoardName, setNewBoardName] = useState("");
  const [showNewBoard, setShowNewBoard] = useState(false);
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [activeFile, setActiveFile] = useState<UploadedFile | null>(null);
  const [productDesc, setProductDesc] = useState("");
  const [keywords, setKeywords] = useState("");
  const [destLink, setDestLink] = useState("");
  const [aiProvider, setAiProvider] = useState("gemini");
  const [content, setContent] = useState<PinForm>({ title: "", description: "", hashtags: "", alt_text: "" });
  const [generatingAI, setGeneratingAI] = useState(false);
  const [queueing, setQueueing] = useState(false);
  const [queued, setQueued] = useState<string[]>([]);

  useEffect(() => {
    listAccounts().then(r => {
      setAccounts(r.data);
      if (r.data.length > 0) setSelectedAccount(r.data[0].id);
    });
  }, []);

  useEffect(() => {
    if (!selectedAccount) return;
    listBoards(selectedAccount).then(r => {
      setBoards(r.data || []);
    }).catch(() => setBoards([]));
  }, [selectedAccount]);

  // Dropzone
  const onDrop = useCallback((accepted: File[]) => {
    const newFiles = accepted.map(f => ({ file: f, preview: URL.createObjectURL(f), id: Math.random().toString(36).slice(2) }));
    setFiles(prev => [...prev, ...newFiles]);
    if (!activeFile && newFiles.length > 0) setActiveFile(newFiles[0]);
  }, [activeFile]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop, accept: { "image/*": [".jpg", ".jpeg", ".png", ".webp"] },
    maxSize: 20 * 1024 * 1024, multiple: true,
  });

  function removeFile(id: string) {
    setFiles(prev => {
      const next = prev.filter(f => f.id !== id);
      if (activeFile?.id === id) setActiveFile(next[0] || null);
      return next;
    });
  }

  async function handleGenerateAI() {
    if (!activeFile && !productDesc) { toast.error("Upload an image or add a product description."); return; }
    setGeneratingAI(true);
    try {
      const fd = new FormData();
      fd.append("product_description", productDesc || activeFile!.file.name);
      fd.append("keywords", keywords);
      fd.append("ai_provider", aiProvider);
      if (activeFile) fd.append("image", activeFile.file);
      const { data } = await generateContent(fd);
      setContent({ title: data.title, description: data.description, hashtags: data.hashtags, alt_text: data.alt_text });
      toast.success("AI content generated!");
    } catch (e: any) {
      toast.error(e.response?.data?.detail || "AI generation failed.");
    }
    setGeneratingAI(false);
  }

  async function handleCreateBoard() {
    if (!newBoardName.trim() || !selectedAccount) return;
    try {
      const { data } = await createBoard(selectedAccount, newBoardName.trim());
      setBoards(prev => [...prev, data]);
      setSelectedBoard(data.id);
      setSelectedBoardName(data.name);
      setNewBoardName("");
      setShowNewBoard(false);
      toast.success(`Board "${data.name}" created!`);
    } catch {
      toast.error("Could not create board.");
    }
  }

  async function handleAddToQueue(targetFile: UploadedFile) {
    if (!selectedAccount) { toast.error("Select a Pinterest account."); return; }
    if (!selectedBoard) { toast.error("Select or create a board."); return; }
    if (!content.title) { toast.error("Generate AI content first."); return; }

    setQueueing(true);
    try {
      const fd = new FormData();
      fd.append("account_id", String(selectedAccount));
      fd.append("board_id", selectedBoard);
      fd.append("board_name", selectedBoardName);
      fd.append("title", content.title);
      fd.append("description", content.description);
      fd.append("alt_text", content.alt_text);
      fd.append("hashtags", content.hashtags);
      fd.append("destination_link", destLink);
      fd.append("image", targetFile.file);
      const { data } = await addToQueue(fd);
      setQueued(prev => [...prev, targetFile.id]);
      toast.success(`Pin scheduled for ${new Date(data.scheduled_for).toLocaleString()}`, { duration: 4000 });
    } catch (e: any) {
      toast.error(e.response?.data?.detail || "Failed to queue pin.");
    }
    setQueueing(false);
  }

  const noAccounts = accounts.length === 0;

  return (
    <div className="min-h-screen">
      <Header title="Create Pins" />
      <div className="p-6 max-w-7xl mx-auto">

        {noAccounts && (
          <div className="glass-card p-8 text-center mb-6">
            <AlertCircle size={40} className="text-accent-gold mx-auto mb-3" />
            <h3 className="font-display font-semibold text-white mb-2">No Pinterest account connected</h3>
            <p className="text-text-muted text-sm font-body mb-4">Connect a Pinterest account before creating pins.</p>
            <a href="/dashboard/accounts" className="btn-primary inline-block">Connect Pinterest</a>
          </div>
        )}

        <div className="grid lg:grid-cols-2 gap-6">
          {/* ── LEFT: Upload + Config ── */}
          <div className="space-y-5">
            {/* Account + Board selectors */}
            <div className="glass-card p-5">
              <h2 className="font-display font-semibold text-white mb-4">Settings</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-body text-text-muted mb-2">Pinterest Account</label>
                  <select value={selectedAccount ?? ""} onChange={e => setSelectedAccount(Number(e.target.value))}
                    className="input-field">
                    {accounts.map(a => <option key={a.id} value={a.id}>@{a.username}</option>)}
                  </select>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-2">
                    <label className="text-sm font-body text-text-muted">Board</label>
                    <button onClick={() => setShowNewBoard(!showNewBoard)} className="text-xs text-primary-light hover:text-accent-fuchsia transition-colors flex items-center gap-1 font-body">
                      <Plus size={12} /> New board
                    </button>
                  </div>
                  {showNewBoard ? (
                    <div className="flex gap-2">
                      <input value={newBoardName} onChange={e => setNewBoardName(e.target.value)} placeholder="Board name…" className="input-field flex-1" />
                      <button onClick={handleCreateBoard} className="btn-primary px-4 py-2 text-sm">Create</button>
                    </div>
                  ) : (
                    <select value={selectedBoard} onChange={e => {
                      setSelectedBoard(e.target.value);
                      setSelectedBoardName(boards.find(b => b.id === e.target.value)?.name ?? "");
                    }} className="input-field">
                      <option value="">Select a board…</option>
                      {boards.map(b => <option key={b.id} value={b.id}>{b.name}</option>)}
                    </select>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-body text-text-muted mb-2">
                    <LinkIcon size={12} className="inline mr-1" /> Destination link (affiliate / product URL)
                  </label>
                  <input type="url" value={destLink} onChange={e => setDestLink(e.target.value)}
                    placeholder="https://yourstore.com/product" className="input-field" />
                </div>
              </div>
            </div>

            {/* Image dropzone */}
            <div className="glass-card p-5">
              <h2 className="font-display font-semibold text-white mb-4">Upload Images</h2>
              <div {...getRootProps()} className={cn(
                "border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all duration-300",
                isDragActive ? "border-primary bg-primary/10" : "border-border hover:border-primary/50 hover:bg-primary/5"
              )}>
                <input {...getInputProps()} />
                <Upload size={32} className="text-text-dim mx-auto mb-3" />
                <p className="font-body text-sm text-text-muted">
                  {isDragActive ? "Drop it here…" : "Drag images here or click to browse"}
                </p>
                <p className="text-text-dim text-xs font-body mt-1">JPG, PNG, WEBP · max 20MB · multiple files OK</p>
              </div>

              {/* File thumbnails */}
              {files.length > 0 && (
                <div className="flex flex-wrap gap-3 mt-4">
                  {files.map(f => (
                    <div key={f.id} onClick={() => setActiveFile(f)}
                      className={cn("relative w-20 h-24 rounded-xl overflow-hidden cursor-pointer border-2 transition-all duration-200",
                        activeFile?.id === f.id ? "border-primary shadow-glow-sm" : "border-border hover:border-primary/40")}>
                      <img src={f.preview} alt={f.file.name} className="w-full h-full object-cover" />
                      {queued.includes(f.id) && (
                        <div className="absolute inset-0 bg-accent-green/30 flex items-center justify-center">
                          <CheckCircle2 size={20} className="text-accent-green" />
                        </div>
                      )}
                      <button onClick={e => { e.stopPropagation(); removeFile(f.id); }}
                        className="absolute top-1 right-1 w-5 h-5 rounded-full bg-bg flex items-center justify-center hover:bg-accent-red/20">
                        <X size={10} className="text-text-muted" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* AI options */}
            <div className="glass-card p-5">
              <h2 className="font-display font-semibold text-white mb-4">AI Content Engine</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-body text-text-muted mb-2">AI Provider</label>
                  <div className="flex gap-2 flex-wrap">
                    {AI_PROVIDERS.map(p => (
                      <button key={p.id} onClick={() => setAiProvider(p.id)}
                        className={cn("flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-body border transition-all duration-200",
                          aiProvider === p.id ? "bg-primary/20 border-primary/50 text-white" : "bg-bg-elevated border-border text-text-muted hover:border-primary/30")}>
                        {p.label}
                        {p.free && <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-accent-green/20 text-accent-green font-mono">FREE</span>}
                      </button>
                    ))}
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-body text-text-muted mb-2">Product description</label>
                  <textarea value={productDesc} onChange={e => setProductDesc(e.target.value)}
                    placeholder="Describe your product, audience, and key benefits…" rows={3}
                    className="input-field resize-none" />
                </div>
                <div>
                  <label className="block text-sm font-body text-text-muted mb-2">Target keywords</label>
                  <input value={keywords} onChange={e => setKeywords(e.target.value)}
                    placeholder="e.g. boho home decor, aesthetic kitchen, cozy room" className="input-field" />
                </div>
                <button onClick={handleGenerateAI} disabled={generatingAI}
                  className="btn-primary w-full flex items-center justify-center gap-2 py-3">
                  {generatingAI ? <><Loader2 size={16} className="animate-spin" /> Generating…</> : <><Sparkles size={16} /> Generate AI Content</>}
                </button>
              </div>
            </div>
          </div>

          {/* ── RIGHT: Preview + Content Editor ── */}
          <div className="space-y-5">
            {/* Pin preview */}
            <div className="glass-card p-5">
              <h2 className="font-display font-semibold text-white mb-4">Pin Preview</h2>
              <div className="flex gap-5">
                {/* Image preview */}
                <div className="w-36 flex-shrink-0">
                  {activeFile ? (
                    <div className="rounded-2xl overflow-hidden" style={{ aspectRatio: "2/3" }}>
                      <img src={activeFile.preview} alt="Preview" className="w-full h-full object-cover" />
                    </div>
                  ) : (
                    <div className="rounded-2xl bg-bg-elevated border border-border flex items-center justify-center" style={{ aspectRatio: "2/3" }}>
                      <ImageIcon size={28} className="text-text-dim" />
                    </div>
                  )}
                </div>
                {/* Content preview */}
                <div className="flex-1 min-w-0">
                  <p className="font-display font-semibold text-white text-sm mb-1 line-clamp-2">{content.title || "Your pin title will appear here…"}</p>
                  <p className="text-text-muted text-xs font-body mb-2 line-clamp-3">{content.description || "AI-generated description will show here."}</p>
                  {content.hashtags && (
                    <div className="flex flex-wrap gap-1 mb-2">
                      {content.hashtags.split(" ").slice(0, 5).map(h => (
                        <span key={h} className="text-[10px] px-2 py-0.5 rounded-full bg-primary/15 text-primary-light border border-primary/20 font-mono">{h}</span>
                      ))}
                    </div>
                  )}
                  {destLink && (
                    <p className="text-xs text-accent-cyan font-mono truncate">{destLink}</p>
                  )}
                </div>
              </div>
            </div>

            {/* Editable content fields */}
            <div className="glass-card p-5">
              <h2 className="font-display font-semibold text-white mb-4">Edit Content</h2>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between mb-2">
                    <label className="text-sm font-body text-text-muted">Title</label>
                    <span className="text-xs font-mono text-text-dim">{content.title.length}/100</span>
                  </div>
                  <input value={content.title} onChange={e => setContent(p => ({ ...p, title: e.target.value.slice(0, 100) }))}
                    placeholder="Pin title…" className="input-field" />
                </div>
                <div>
                  <div className="flex justify-between mb-2">
                    <label className="text-sm font-body text-text-muted">Description</label>
                    <span className="text-xs font-mono text-text-dim">{content.description.length}/500</span>
                  </div>
                  <textarea value={content.description} onChange={e => setContent(p => ({ ...p, description: e.target.value.slice(0, 500) }))}
                    placeholder="Pin description…" rows={4} className="input-field resize-none" />
                </div>
                <div>
                  <label className="block text-sm font-body text-text-muted mb-2">Hashtags</label>
                  <input value={content.hashtags} onChange={e => setContent(p => ({ ...p, hashtags: e.target.value }))}
                    placeholder="#hashtag1 #hashtag2 …" className="input-field font-mono text-sm" />
                </div>
                <div>
                  <label className="block text-sm font-body text-text-muted mb-2">Alt text (accessibility)</label>
                  <textarea value={content.alt_text} onChange={e => setContent(p => ({ ...p, alt_text: e.target.value.slice(0, 500) }))}
                    placeholder="Describe the image for screen readers…" rows={2} className="input-field resize-none" />
                </div>
              </div>
            </div>

            {/* Queue buttons */}
            <div className="glass-card p-5">
              <h2 className="font-display font-semibold text-white mb-3">Add to Queue</h2>
              {files.length === 0 ? (
                <p className="text-text-dim text-sm font-body">Upload at least one image first.</p>
              ) : (
                <div className="space-y-2">
                  {files.map(f => (
                    <div key={f.id} className={cn(
                      "flex items-center gap-3 p-3 rounded-xl border transition-all duration-200",
                      queued.includes(f.id) ? "bg-accent-green/10 border-accent-green/30" : "bg-bg-elevated border-border"
                    )}>
                      <img src={f.preview} alt={f.file.name} className="w-10 h-12 object-cover rounded-lg flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-body text-white truncate">{f.file.name}</p>
                        {queued.includes(f.id) && (
                          <p className="text-xs text-accent-green font-body flex items-center gap-1"><CheckCircle2 size={10} /> Queued successfully</p>
                        )}
                      </div>
                      {queued.includes(f.id) ? (
                        <span className="badge-posted">Queued</span>
                      ) : (
                        <button onClick={() => handleAddToQueue(f)} disabled={queueing}
                          className="btn-primary px-4 py-2 text-sm flex items-center gap-1.5">
                          {queueing ? <Loader2 size={13} className="animate-spin" /> : <Clock size={13} />}
                          Schedule
                        </button>
                      )}
                    </div>
                  ))}

                  {files.length > 1 && (
                    <button
                      onClick={async () => { for (const f of files.filter(f => !queued.includes(f.id))) { await handleAddToQueue(f); } }}
                      disabled={queueing}
                      className="btn-gold w-full flex items-center justify-center gap-2 py-2.5 text-sm mt-2">
                      <Clock size={14} /> Queue All ({files.filter(f => !queued.includes(f.id)).length} remaining)
                    </button>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
