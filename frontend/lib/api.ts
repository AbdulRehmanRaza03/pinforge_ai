import axios from "axios";
import { getAccessToken } from "./supabase";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
});

// Auto-inject Supabase JWT on every request
api.interceptors.request.use(async (config) => {
  const token = await getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;

// ── Accounts ────────────────────────────────────────────────────────────────
export const getAuthUrl      = ()   => api.get("/api/accounts/auth-url");
export const listAccounts    = ()   => api.get("/api/accounts/");
export const deleteAccount   = (id: number) => api.delete(`/api/accounts/${id}`);
export const listBoards      = (accountId: number) => api.get(`/api/accounts/${accountId}/boards`);
export const createBoard     = (accountId: number, name: string, description = "") =>
  api.post(`/api/accounts/${accountId}/boards`, { name, description });

// ── Pins ────────────────────────────────────────────────────────────────────
export const generateContent = (formData: FormData) =>
  api.post("/api/pins/generate-content", formData, { headers: { "Content-Type": "multipart/form-data" } });

export const addToQueue = (formData: FormData) =>
  api.post("/api/pins/queue", formData, { headers: { "Content-Type": "multipart/form-data" } });

export const getQueue       = (accountId: number) => api.get(`/api/pins/queue?account_id=${accountId}`);
export const removeFromQueue = (itemId: number) => api.delete(`/api/pins/queue/${itemId}`);
export const getHistory      = (accountId: number, limit = 50) =>
  api.get(`/api/pins/history?account_id=${accountId}&limit=${limit}`);

// ── Analytics ───────────────────────────────────────────────────────────────
export const getAnalytics = (accountId: number) =>
  api.get(`/api/analytics/overview?account_id=${accountId}`);

// ── Settings ────────────────────────────────────────────────────────────────
export const getSettings    = ()      => api.get("/api/settings/");
export const updateSettings = (data: object) => api.patch("/api/settings/", data);
