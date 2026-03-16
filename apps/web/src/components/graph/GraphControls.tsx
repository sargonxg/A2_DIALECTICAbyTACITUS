"use client";

import { NODE_COLORS } from "@/lib/utils";
import { cn } from "@/lib/utils";
import type { NodeType } from "@/types/ontology";
import type { LayoutType } from "@/types/graph";
import { Search, Maximize, Download } from "lucide-react";

interface Props {
  activeNodeTypes: Set<NodeType>;
  onToggleNodeType: (type: NodeType) => void;
  layout: LayoutType;
  onLayoutChange: (layout: LayoutType) => void;
  confidenceThreshold: number;
  onConfidenceChange: (val: number) => void;
  searchQuery: string;
  onSearchChange: (val: string) => void;
  onFitToScreen: () => void;
  onExport: (format: "png" | "svg" | "json") => void;
}

const NODE_TYPES: NodeType[] = [
  "actor", "conflict", "event", "issue", "interest", "norm",
  "process", "outcome", "narrative", "emotional_state", "trust_state",
  "power_dynamic", "location", "evidence", "role",
];

const LAYOUTS: { value: LayoutType; label: string }[] = [
  { value: "force", label: "Force" },
  { value: "hierarchy", label: "Hierarchy" },
  { value: "radial", label: "Radial" },
  { value: "temporal", label: "Temporal" },
];

export default function GraphControls({
  activeNodeTypes, onToggleNodeType, layout, onLayoutChange,
  confidenceThreshold, onConfidenceChange, searchQuery, onSearchChange,
  onFitToScreen, onExport,
}: Props) {
  return (
    <div className="space-y-4 p-4 card">
      {/* Search */}
      <div className="relative">
        <Search size={14} className="absolute left-3 top-2.5 text-text-secondary" />
        <input
          type="text"
          placeholder="Search nodes..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          className="input-base w-full pl-9"
        />
      </div>

      {/* Node type filters */}
      <div>
        <p className="text-xs text-text-secondary mb-2 font-semibold uppercase tracking-wider">Node Types</p>
        <div className="flex flex-wrap gap-1">
          {NODE_TYPES.map((type) => (
            <button
              key={type}
              onClick={() => onToggleNodeType(type)}
              className={cn(
                "badge transition-opacity text-[10px]",
                activeNodeTypes.has(type) ? "opacity-100" : "opacity-30",
              )}
              style={{ backgroundColor: NODE_COLORS[type] + "20", color: NODE_COLORS[type] }}
            >
              {type.replace("_", " ")}
            </button>
          ))}
        </div>
      </div>

      {/* Layout */}
      <div>
        <p className="text-xs text-text-secondary mb-2 font-semibold uppercase tracking-wider">Layout</p>
        <div className="flex gap-1">
          {LAYOUTS.map((l) => (
            <button
              key={l.value}
              onClick={() => onLayoutChange(l.value)}
              className={cn("badge", layout === l.value ? "bg-accent/20 text-accent" : "bg-surface-hover text-text-secondary")}
            >
              {l.label}
            </button>
          ))}
        </div>
      </div>

      {/* Confidence threshold */}
      <div>
        <p className="text-xs text-text-secondary mb-2 font-semibold uppercase tracking-wider">
          Confidence &ge; {confidenceThreshold.toFixed(1)}
        </p>
        <input
          type="range"
          min="0"
          max="1"
          step="0.1"
          value={confidenceThreshold}
          onChange={(e) => onConfidenceChange(parseFloat(e.target.value))}
          className="w-full accent-accent"
        />
      </div>

      {/* Actions */}
      <div className="flex gap-2">
        <button onClick={onFitToScreen} className="btn-secondary flex-1 flex items-center justify-center gap-1">
          <Maximize size={14} /> Fit
        </button>
        <button onClick={() => onExport("png")} className="btn-secondary flex-1 flex items-center justify-center gap-1">
          <Download size={14} /> Export
        </button>
      </div>
    </div>
  );
}
