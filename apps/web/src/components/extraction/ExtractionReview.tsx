"use client";

import { useState } from "react";
import { NODE_COLORS, capitalize } from "@/lib/utils";
import { cn } from "@/lib/utils";
import { Check, X, Edit2 } from "lucide-react";

interface ExtractedEntity {
  id: string;
  node_type: string;
  name: string;
  confidence: number;
  properties: Record<string, unknown>;
}

interface Props {
  entities: ExtractedEntity[];
  onCommit: (ids: string[]) => void;
  onReject: (ids: string[]) => void;
}

export default function ExtractionReview({ entities, onCommit, onReject }: Props) {
  const [selected, setSelected] = useState<Set<string>>(new Set(entities.map((e) => e.id)));

  const toggleSelect = (id: string) => {
    const next = new Set(selected);
    next.has(id) ? next.delete(id) : next.add(id);
    setSelected(next);
  };

  const grouped = entities.reduce<Record<string, ExtractedEntity[]>>((acc, e) => {
    (acc[e.node_type] = acc[e.node_type] || []).push(e);
    return acc;
  }, {});

  return (
    <div className="space-y-4">
      {Object.entries(grouped).map(([type, items]) => (
        <div key={type}>
          <h4 className="text-sm font-semibold text-text-secondary uppercase tracking-wider mb-2 flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: NODE_COLORS[type] }} />
            {capitalize(type.replace("_", " "))} ({items.length})
          </h4>
          <div className="space-y-1">
            {items.map((entity) => (
              <div
                key={entity.id}
                className={cn("card flex items-center gap-3 cursor-pointer", selected.has(entity.id) ? "border-accent/30" : "opacity-50")}
                onClick={() => toggleSelect(entity.id)}
              >
                <input type="checkbox" checked={selected.has(entity.id)} readOnly className="accent-accent" />
                <span className="text-sm text-text-primary flex-1">{entity.name}</span>
                <span className={cn(
                  "font-mono text-xs",
                  entity.confidence >= 0.8 ? "text-success" : entity.confidence >= 0.6 ? "text-warning" : "text-danger",
                )}>
                  {(entity.confidence * 100).toFixed(0)}%
                </span>
              </div>
            ))}
          </div>
        </div>
      ))}

      <div className="flex gap-2">
        <button onClick={() => onCommit(Array.from(selected))} className="btn-primary flex-1">
          <Check size={14} className="inline mr-1" /> Commit Selected ({selected.size})
        </button>
        <button onClick={() => onCommit(entities.map((e) => e.id))} className="btn-secondary">
          Commit All
        </button>
      </div>
    </div>
  );
}
