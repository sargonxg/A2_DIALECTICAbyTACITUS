'use client';

import React from 'react';
import { X, ArrowRight, Hash, Weight } from 'lucide-react';
import type { GraphEdge } from '@/lib/api';

function formatValue(value: unknown): string {
  if (value === null || value === undefined) return '—';
  if (typeof value === 'boolean') return value ? 'true' : 'false';
  if (typeof value === 'object') return JSON.stringify(value);
  return String(value);
}

function getEdgeTypeColor(type: string): string {
  const t = type.toLowerCase();
  if (t.includes('causes') || t.includes('causal'))    return '#f97316';
  if (t.includes('trust'))                              return '#8b5cf6';
  if (t.includes('power') || t.includes('influence'))  return '#a855f7';
  if (t.includes('ally') || t.includes('support'))     return '#22c55e';
  if (t.includes('oppose') || t.includes('conflict'))  return '#ef4444';
  if (t.includes('part') || t.includes('member'))      return '#06b6d4';
  return '#71717a';
}

interface EdgeDetailProps {
  edge: GraphEdge | null;
  onClose: () => void;
}

export function EdgeDetail({ edge, onClose }: EdgeDetailProps) {
  if (!edge) return null;

  const typeColor = getEdgeTypeColor(edge.type);
  const properties = edge.properties ?? {};
  const propertyEntries = Object.entries(properties);

  return (
    <div className="flex flex-col h-full rounded-xl border border-[#27272a] bg-[#18181b] shadow-2xl overflow-hidden">
      {/* Header */}
      <div className="flex items-start justify-between gap-3 p-4 border-b border-[#27272a]">
        <div className="flex items-start gap-3 min-w-0">
          <div
            className="mt-0.5 h-3 w-3 flex-shrink-0 rounded-sm ring-2 ring-black/20"
            style={{ backgroundColor: typeColor }}
          />
          <div className="min-w-0">
            <h3 className="text-sm font-semibold text-white leading-tight">Edge</h3>
            <span
              className="mt-1 inline-block rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider"
              style={{
                backgroundColor: `${typeColor}20`,
                color: typeColor,
                border: `1px solid ${typeColor}40`,
              }}
            >
              {edge.type}
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
                <p className="text-xs text-zinc-300 font-mono break-all">{edge.id}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Relationship */}
        <div className="space-y-2">
          <p className="text-[10px] font-semibold uppercase tracking-widest text-zinc-500">
            Relationship
          </p>
          <div className="rounded-lg border border-[#27272a] bg-[#09090b] divide-y divide-[#27272a]">
            <div className="flex items-start gap-3 px-3 py-2">
              <ArrowRight className="w-3.5 h-3.5 text-zinc-500 mt-0.5 flex-shrink-0" />
              <div className="min-w-0flex-1">
                <p className="text-[10px] text-zinc-500 font-medium">Source</p>
                <p className="text-xs text-zinc-300 font-mono break-all">{edge.source_id}</p>
              </div>
            </div>
            <div className="flex items-start gap-3 px-3 py-2">
              <ArrowRight
                className="w-3.5 h-3.5 mt-0.5 flex-shrink-0"
                style={{ color: typeColor }}
              />
              <div className="min-w-0 flex-1">
                <p className="text-[10px] text-zinc-500 font-medium">Target</p>
                <p className="text-xs text-zinc-300 font-mono break-all">{edge.target_id}</p>
              </div>
            </div>
            {edge.weight !== undefined && (
              <div className="flex items-start gap-3 px-3 py-2">
                <Weight className="w-3.5 h-3.5 text-zinc-500 mt-0.5 flex-shrink-0" />
                <div className="min-w-0">
                  <p className="text-[10px] text-zinc-500 font-medium">Weight</p>
                  <div className="flex items-center gap-2 mt-0.5">
                    <div className="flex-1 h-1.5 rounded-full bg-zinc-800">
                      <div
                        className="h-full rounded-full transition-all"
                        style={{
                          width: `${Math.min(100, (edge.weight ?? 0) * 100)}%`,
                          backgroundColor: typeColor,
                        }}
                      />
                    </div>
                    <span className="text-xs text-zinc-300 font-mono">
                      {edge.weight.toFixed(3)}
                    </span>
                  </div>
                </div>
              </div>
            )}
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

export default EdgeDetail;
