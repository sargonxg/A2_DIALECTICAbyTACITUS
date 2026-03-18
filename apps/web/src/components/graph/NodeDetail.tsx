"use client";

import type { GraphNode } from "@/types/graph";
import { NODE_COLORS, capitalize } from "@/lib/utils";
import { X, Brain, Link } from "lucide-react";

interface Props {
  node: GraphNode;
  connectedNodes?: { node: GraphNode; edgeType: string }[];
  onClose: () => void;
  onAnalyze?: (nodeId: string) => void;
}

export default function NodeDetail({ node, connectedNodes = [], onClose, onAnalyze }: Props) {
  const color = NODE_COLORS[node.node_type] || "#94a3b8";

  return (
    <div className="card w-80 space-y-4 animate-slide-in">
      <div className="flex items-start justify-between">
        <div>
          <span className="badge text-[10px] mb-1" style={{ backgroundColor: color + "20", color }}>
            {node.node_type.replace("_", " ")}
          </span>
          <h3 className="font-semibold text-text-primary text-lg">{node.name}</h3>
        </div>
        <button onClick={onClose} className="btn-ghost p-1">
          <X size={16} />
        </button>
      </div>

      {/* Properties */}
      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-text-secondary">Confidence</span>
          <span className="font-mono text-text-primary">{(node.confidence * 100).toFixed(0)}%</span>
        </div>
        {Object.entries(node.properties).map(([key, val]) => {
          if (key === "centrality" || key === "embedding") return null;
          return (
            <div key={key} className="flex justify-between">
              <span className="text-text-secondary">{capitalize(key.replace("_", " "))}</span>
              <span className="text-text-primary text-right max-w-[180px] truncate">{String(val)}</span>
            </div>
          );
        })}
      </div>

      {/* Connected nodes */}
      {connectedNodes.length > 0 && (
        <div>
          <p className="text-xs text-text-secondary font-semibold uppercase tracking-wider mb-2">
            <Link size={12} className="inline mr-1" /> Connected ({connectedNodes.length})
          </p>
          <div className="space-y-1 max-h-40 overflow-y-auto">
            {connectedNodes.map(({ node: n, edgeType }) => (
              <div key={n.id} className="flex items-center gap-2 text-sm">
                <span className="w-2 h-2 rounded-full" style={{ backgroundColor: NODE_COLORS[n.node_type] }} />
                <span className="text-text-primary truncate flex-1">{n.name}</span>
                <span className="text-text-secondary text-[10px]">{edgeType}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-2">
        {onAnalyze && (
          <button onClick={() => onAnalyze(node.id)} className="btn-primary flex-1 flex items-center justify-center gap-1">
            <Brain size={14} /> Analyze
          </button>
        )}
      </div>
    </div>
  );
}
