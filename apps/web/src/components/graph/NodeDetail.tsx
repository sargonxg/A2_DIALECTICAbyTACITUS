'use client';

import React from 'react';
import { X, Hash, Tag } from 'lucide-react';
import type { GraphNode } from '@/lib/api';

const NODE_COLORS: Record<string, string> = {
  actor:         '#3b82f6',
  conflict:      '#6366f1',
  event:         '#eab308',
  issue:         '#f97316',
  interest:      '#22c55e',
  process:       '#06b6d4',
  narrative:     '#ec4899',
  trust_state:   '#8b5cf6',
  power_dynamic: '#a855f7',
};

function getNodeColor(label: string): string {
  return NODE_COLORS[label.toLowerCase()] ?? '#71717a';
}

function formatValue(value: unknown): string {
  if (value === null || value === undefined) return '—';
  if (typeof value === 'boolean') return value ? 'true' : 'false';
  if (typeof value === 'object') return JSON.stringify(value);
  return String(value);
}

interface NodeDetailProps {
  node: GraphNode | null;
  onClose: () => void;
}

export function NodeDetail({ node, onClose }: NodeDetailProps) {
  if (!node) return null;

  const color = getNodeColor(node.label);
  const properties = node.properties ?? {};
  const propertyEntries = Object.entries(properties).filter(
    ([key]) => key !== 'name' && key !== 'id'
  );

  return (
    <div className="flex flex-col h-full rounded-xl border border-[#27272a] bg-[#18181b] shadow-2xl overflow-hidden">
      {/* Header */}
      <div className="flex items-start justify-between gap-3 p-4 border-b border-[#27272a]">
        <div className="flex items-start gap-3 min-w-0">
          <div
            className="mt-0.5 h-3 w-3 flex-shrink-0 rounded-full ring-2 ring-black/20"
            style={{ backgroundColor: color }}
          />
          <div className="min-w-0">
            <h3 className="text-sm font-semibold text-white leading-tight truncate">
              {node.name || 'Unnamed Node'}
            </h3>
            <span
              className="mt-1 inline-block rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider"
              style={{
                backgroundColor: `${color}20`,
                color: color,
                border: `1px solid ${color}40`,
              }}
            >
              {node.label}
            </span>
          </div>
        </div>
        <button
          onClick={onClose}
          className="flex-shrink-0 rounded-md p-1 text-zinc-500 hover:text-white hover:bg-white/10 transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Body */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Core fields */}
        <div className="space-y-2">
          <p className="text-[10px] font-semibold uppercase tracking-widest text-zinc-500">
            Identity
          </p>
          <div className="rounded-lg border border-[#27272a] bg-[#09090b] divide-y divide-[#27272a]">
            <div className="flex items-start gap-3 px-3 py-2">
              <Hash className="w-3.5 h-3.5 text-zinc-500 mt-0.5 flex-shrink-0" />
              <div className="min-w-0">
                <p className="text-[10px] text-zinc-500 font-medium">ID</p>
                <p className="text-xs text-zinc-300 font-mono break-all">{node.id}</p>
              </div>
            </div>
            <div className="flex items-start gap-3 px-3 py-2">
              <Tag className="w-3.5 h-3.5 text-zinc-500 mt-0.5 flex-shrink-0" />
              <div className="min-w-0">
                <p className="text-[10px] text-zinc-500 font-medium">Label</p>
                <p className="text-xs capitalize" style={{ color }}>
                  {node.label}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Properties */}
        {propertyEntries.length > 0 && (
          <div className="space-y-2">
            <p className="text-[10px] font-semibold uppercase tracking-widest text-zinc-500">
              Properties
            </p>
            <div className="rounded-lg border border-[#27272a] bg-[#09090b] divide-y divide-[#27272a]">
              {propertyEntries.map(([key, value]) => (
                <div key={key} className="px-3 py-2">
                  <p className="text-[10px] text-zinc-500 font-medium capitalize">
                    {key.replace(/_/g, ' ')}
                  </p>
                  <p className="text-xs text-zinc-300 mt-0.5 break-words">
                    {formatValue(value)}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {propertyEntries.length === 0 && (
          <p className="text-xs text-zinc-600 italic">No additional properties.</p>
        )}
      </div>
    </div>
  );
}

export default NodeDetail;
