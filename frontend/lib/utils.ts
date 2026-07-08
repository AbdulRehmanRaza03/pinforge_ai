import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import { format, formatDistanceToNow } from "date-fns";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(iso: string) {
  return format(new Date(iso), "MMM d, yyyy · h:mm a");
}

export function timeFromNow(iso: string) {
  return formatDistanceToNow(new Date(iso), { addSuffix: true });
}

export function statusColor(status: string): string {
  const map: Record<string, string> = {
    posted: "badge-posted",
    scheduled: "badge-scheduled",
    failed: "badge-failed",
    queued: "badge-queued",
    duplicate: "badge-duplicate",
    rate_limit: "badge-queued",
  };
  return map[status] ?? "badge-queued";
}

export function truncate(str: string, n: number) {
  return str.length > n ? str.slice(0, n - 1) + "…" : str;
}
