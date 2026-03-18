import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(date: string | Date): string {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(new Date(date));
}

export function formatRelative(date: string | Date): string {
  const now = Date.now();
  const then = new Date(date).getTime();
  const diff = now - then;
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days < 30) return `${days}d ago`;
  return formatDate(date);
}

export function truncate(str: string, len: number): string {
  return str.length > len ? str.slice(0, len) + "..." : str;
}

export function capitalize(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

export const NODE_COLORS: Record<string, string> = {
  actor: "#3b82f6",
  conflict: "#6366f1",
  event: "#eab308",
  issue: "#f97316",
  interest: "#22c55e",
  norm: "#64748b",
  process: "#06b6d4",
  outcome: "#10b981",
  narrative: "#ec4899",
  emotional_state: "#f43f5e",
  trust_state: "#8b5cf6",
  power_dynamic: "#a855f7",
  location: "#78716c",
  evidence: "#94a3b8",
  role: "#d946ef",
};

export const GLASL_COLORS: Record<string, string> = {
  "win-win": "#22c55e",
  "win-lose": "#eab308",
  "lose-lose": "#ef4444",
};

export function glaslLevel(stage: number): string {
  if (stage <= 3) return "win-win";
  if (stage <= 6) return "win-lose";
  return "lose-lose";
}
