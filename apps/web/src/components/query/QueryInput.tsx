"use client";

import { useState } from "react";
import type { AnalysisMode } from "@/types/api";
import { Send } from "lucide-react";
import { cn } from "@/lib/utils";

const MODES: { value: AnalysisMode; label: string; color: string }[] = [
  { value: "general", label: "General", color: "#94a3b8" },
  { value: "escalation", label: "Escalation", color: "#f43f5e" },
  { value: "ripeness", label: "Ripeness", color: "#f59e0b" },
  { value: "trust", label: "Trust", color: "#8b5cf6" },
  { value: "power", label: "Power", color: "#a855f7" },
  { value: "causal", label: "Causal", color: "#06b6d4" },
  { value: "narrative", label: "Narrative", color: "#ec4899" },
];

interface Props {
  onSubmit: (query: string, mode: AnalysisMode) => void;
  loading?: boolean;
}

export default function QueryInput({ onSubmit, loading }: Props) {
  const [query, setQuery] = useState("");
  const [mode, setMode] = useState<AnalysisMode>("general");

  const handleSubmit = () => {
    if (!query.trim()) return;
    onSubmit(query.trim(), mode);
    setQuery("");
  };

  return (
    <div className="space-y-2">
      <div className="flex gap-1 flex-wrap">
        {MODES.map((m) => (
          <button
            key={m.value}
            onClick={() => setMode(m.value)}
            className={cn("badge text-[10px] transition-all", mode === m.value ? "ring-1" : "opacity-50")}
            style={{ backgroundColor: m.color + "20", color: m.color, borderColor: mode === m.value ? m.color : "transparent" }}
          >
            {m.label}
          </button>
        ))}
      </div>
      <div className="flex gap-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
          placeholder="Ask about this conflict..."
          className="input-base flex-1"
        />
        <button onClick={handleSubmit} disabled={loading || !query.trim()} className="btn-primary">
          <Send size={16} />
        </button>
      </div>
    </div>
  );
}
