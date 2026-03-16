'use client';

import React, { useState } from 'react';

const NODE_TYPES: { label: string; color: string }[] = [
  { label: 'actor',         color: '#3b82f6' },
  { label: 'conflict',      color: '#6366f1' },
  { label: 'event',         color: '#eab308' },
  { label: 'issue',         color: '#f97316' },
  { label: 'interest',      color: '#22c55e' },
  { label: 'process',       color: '#06b6d4' },
  { label: 'narrative',     color: '#ec4899' },
  { label: 'trust_state',   color: '#8b5cf6' },
  { label: 'power_dynamic', color: '#a855f7' },
];

interface GraphLegendProps {
  visibleLabels?: string[];
  onToggle?: (label: string) => void;
}

export function GraphLegend({ visibleLabels, onToggle }: GraphLegendProps) {
  const [localVisible, setLocalVisible] = useState<Set<string>>(
    () => new Set(NODE_TYPES.map((t) => t.label))
  );

  const isVisible = (label: string): boolean => {
    if (visibleLabels) return visibleLabels.includes(label);
    return localVisible.has(label);
  };

  const handleToggle = (label: string) => {
    if (onToggle) {
      onToggle(label);
    } else {
      setLocalVisible((prev) => {
        const next = new Set(prev);
        if (next.has(label)) next.delete(label);
        else next.add(label);
        return next;
      });
    }
  };

  return (
    <div className="rounded-lg border border-[#27272a] bg-[#18181b] p-3">
      <p className="text-[10px] font-semibold uppercase tracking-widest text-zinc-500 mb-2">
        Node Types
      </p>
      <div className="grid grid-cols-2 gap-1">
        {NODE_TYPES.map(({ label, color }) => {
          const visible = isVisible(label);
          return (
            <button
              key={label}
              onClick={() => handleToggle(label)}
              className={[
                'flex items-center gap-2 rounded px-2 py-1 text-left transition-opacity',
                'hover:bg-white/5',
                visible ? 'opacity-100' : 'opacity-40',
              ].join(' ')}
              title={visible ? `Hide ${label}` : `Show ${label}`}
            >
              <span
                className="h-2.5 w-2.5 flex-shrink-0 rounded-full"
                style={{ backgroundColor: color }}
              />
              <span className="text-[11px] capitalize text-zinc-300 truncate">
                {label.replace('_', ' ')}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

export default GraphLegend;
