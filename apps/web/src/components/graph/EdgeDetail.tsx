"use client";

import type { GraphLink, GraphNode } from "@/types/graph";
import { capitalize } from "@/lib/utils";
import { X } from "lucide-react";

interface Props {
  link: GraphLink;
  onClose: () => void;
}

export default function EdgeDetail({ link, onClose }: Props) {
  const source = link.source as GraphNode;
  const target = link.target as GraphNode;

  return (
    <div className="card w-80 space-y-3 animate-slide-in">
      <div className="flex items-start justify-between">
        <div>
          <span className="badge bg-surface-hover text-text-secondary text-[10px] mb-1">
            {link.edge_type.replace("_", " ")}
          </span>
          <h3 className="font-semibold text-text-primary text-sm">
            {source?.name ?? "?"} &rarr; {target?.name ?? "?"}
          </h3>
        </div>
        <button onClick={onClose} className="btn-ghost p-1"><X size={16} /></button>
      </div>

      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-text-secondary">Weight</span>
          <span className="font-mono">{link.weight.toFixed(2)}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-text-secondary">Confidence</span>
          <span className="font-mono">{(link.confidence * 100).toFixed(0)}%</span>
        </div>
      </div>
    </div>
  );
}
