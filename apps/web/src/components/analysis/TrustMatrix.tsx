'use client';

import React, { useState } from 'react';
import { ShieldCheck, TrendingUp, TrendingDown, Minus, Users } from 'lucide-react';
import type { TrustMatrix as TrustMatrixData } from '@/lib/api';

interface TrustMatrixProps {
  data: TrustMatrixData;
}

function TrustBar({ value, color }: { value: number; color: string }) {
  const pct = Math.round(Math.min(1, Math.max(0, value)) * 100);
  return (
    <div className="flex items-center gap-2 w-full">
      <div className="flex-1 h-1.5 rounded-full bg-zinc-800 overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{ width: `${pct}%`, backgroundColor: color }}
        />
      </div>
      <span className="text-[11px] tabular-nums text-zinc-400 w-7 text-right">{pct}%</span>
    </div>
  );
}

function trustColor(value: number): string {
  if (value >= 0.7) return '#22c55e';
  if (value >= 0.4) return '#eab308';
  return '#ef4444';
}

function OverallBadge({ value }: { value: number }) {
  const pct = Math.round(value * 100);
  const color = trustColor(value);
  const label = value >= 0.7 ? 'High' : value >= 0.4 ? 'Medium' : 'Low';
  return (
    <span
      className="inline-flex items-center rounded px-1.5 py-0.5 text-[10px] font-semibold border"
      style={{ color, borderColor: `${color}40`, backgroundColor: `${color}15` }}
    >
      {label} {pct}%
    </span>
  );
}

function ChangeIcon({ delta }: { delta: number }) {
  if (delta > 0.01)
    return <TrendingUp className="w-3.5 h-3.5 text-green-500 shrink-0" />;
  if (delta < -0.01)
    return <TrendingDown className="w-3.5 h-3.5 text-red-500 shrink-0" />;
  return <Minus className="w-3.5 h-3.5 text-zinc-500 shrink-0" />;
}

type SortKey = 'overall' | 'ability' | 'benevolence' | 'integrity';

export function TrustMatrix({ data }: TrustMatrixProps) {
  const { average_trust, lowest_trust_pair, highest_trust_pair, dyads, recent_changes } = data;

  const [sortKey, setSortKey] = useState<SortKey>('overall');
  const [sortAsc, setSortAsc] = useState(false);

  const sorted = [...dyads].sort((a, b) => {
    const diff = a[sortKey] - b[sortKey];
    return sortAsc ? diff : -diff;
  });

  function handleSort(key: SortKey) {
    if (sortKey === key) {
      setSortAsc((v) => !v);
    } else {
      setSortKey(key);
      setSortAsc(false);
    }
  }

  const avgPct = Math.round(average_trust * 100);
  const avgColor = trustColor(average_trust);

  const COLUMNS: { key: SortKey; label: string; color: string }[] = [
    { key: 'ability', label: 'Ability', color: '#0d9488' },
    { key: 'benevolence', label: 'Benevolence', color: '#6366f1' },
    { key: 'integrity', label: 'Integrity', color: '#f59e0b' },
    { key: 'overall', label: 'Overall', color: '#22c55e' },
  ];

  return (
    <div className="rounded-xl border border-[#27272a] bg-[#18181b] p-5 space-y-5">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-0.5">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-zinc-400" />
            <span className="text-xs font-semibold uppercase tracking-widest text-zinc-400">
              Trust Matrix
            </span>
          </div>
          <p className="text-sm text-zinc-400">Mayer Trust Model — Ability · Benevolence · Integrity</p>
        </div>

        {/* Average trust */}
        <div
          className="rounded-lg border px-3 py-2 text-center"
          style={{ borderColor: `${avgColor}40`, backgroundColor: `${avgColor}10` }}
        >
          <p className="text-[10px] uppercase tracking-widest text-zinc-500 font-medium">Avg Trust</p>
          <p className="text-xl font-bold" style={{ color: avgColor }}>
            {avgPct}%
          </p>
        </div>
      </div>

      {/* Highlights */}
      {(lowest_trust_pair || highest_trust_pair) && (
        <div className="grid grid-cols-2 gap-3">
          {highest_trust_pair && (
            <div className="rounded-lg border border-green-500/20 bg-green-500/5 px-3 py-2 space-y-0.5">
              <p className="text-[10px] uppercase tracking-widest text-green-600 font-medium">
                Highest Trust
              </p>
              <p className="text-xs font-medium text-zinc-300">
                {highest_trust_pair[0]} → {highest_trust_pair[1]}
              </p>
            </div>
          )}
          {lowest_trust_pair && (
            <div className="rounded-lg border border-red-500/20 bg-red-500/5 px-3 py-2 space-y-0.5">
              <p className="text-[10px] uppercase tracking-widest text-red-500 font-medium">
                Lowest Trust
              </p>
              <p className="text-xs font-medium text-zinc-300">
                {lowest_trust_pair[0]} → {lowest_trust_pair[1]}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Table */}
      {dyads.length > 0 ? (
        <div className="overflow-x-auto -mx-1">
          <table className="w-full text-xs min-w-[520px]">
            <thead>
              <tr className="border-b border-[#27272a]">
                <th className="text-left py-2 px-2 text-zinc-500 font-medium w-28">Trustor</th>
                <th className="text-left py-2 px-2 text-zinc-500 font-medium w-28">Trustee</th>
                {COLUMNS.map((col) => (
                  <th
                    key={col.key}
                    className="text-left py-2 px-2 font-medium cursor-pointer select-none hover:text-zinc-200 transition-colors"
                    style={{ color: sortKey === col.key ? col.color : '#71717a' }}
                    onClick={() => handleSort(col.key)}
                  >
                    <span className="flex items-center gap-1">
                      {col.label}
                      {sortKey === col.key && (
                        <span className="text-[10px]">{sortAsc ? '↑' : '↓'}</span>
                      )}
                    </span>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {sorted.map((dyad, i) => (
                <tr
                  key={`${dyad.trustor}-${dyad.trustee}-${i}`}
                  className="border-b border-[#27272a]/50 hover:bg-zinc-800/30 transition-colors"
                >
                  <td className="py-2 px-2 text-zinc-300 font-medium truncate max-w-[112px]">
                    {dyad.trustor}
                  </td>
                  <td className="py-2 px-2 text-zinc-400 truncate max-w-[112px]">{dyad.trustee}</td>
                  {COLUMNS.map((col) => (
                    <td key={col.key} className="py-2 px-2">
                      {col.key === 'overall' ? (
                        <div className="flex items-center gap-2">
                          <TrustBar value={dyad[col.key]} color={trustColor(dyad[col.key])} />
                          <OverallBadge value={dyad[col.key]} />
                        </div>
                      ) : (
                        <TrustBar value={dyad[col.key]} color={col.color} />
                      )}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="rounded-lg border border-[#27272a] bg-zinc-900/30 px-4 py-6 text-center">
          <Users className="w-8 h-8 text-zinc-600 mx-auto mb-2" />
          <p className="text-sm text-zinc-500">No trust dyads available</p>
        </div>
      )}

      {/* Recent changes */}
      {recent_changes.length > 0 && (
        <>
          <div className="border-t border-[#27272a]" />
          <div className="space-y-2">
            <p className="text-[10px] font-semibold uppercase tracking-widest text-zinc-500">
              Recent Trust Changes
            </p>
            <div className="space-y-1.5">
              {recent_changes.slice(0, 6).map((change, i) => (
                <div
                  key={i}
                  className="flex items-start gap-2.5 rounded-lg border border-[#27272a] bg-zinc-900/30 px-3 py-2"
                >
                  <ChangeIcon delta={change.delta} />
                  <div className="flex-1 min-w-0 space-y-0.5">
                    <div className="flex items-center gap-1.5 flex-wrap">
                      <span className="text-xs font-medium text-zinc-300">{change.trustor}</span>
                      <span className="text-zinc-600">→</span>
                      <span className="text-xs text-zinc-400">{change.trustee}</span>
                      <span
                        className="ml-auto text-[11px] font-semibold tabular-nums"
                        style={{ color: change.delta >= 0 ? '#22c55e' : '#ef4444' }}
                      >
                        {change.delta >= 0 ? '+' : ''}
                        {Math.round(change.delta * 100)}%
                      </span>
                    </div>
                    <p className="text-[11px] text-zinc-500 truncate">{change.event}</p>
                    {change.type && (
                      <span className="inline-block text-[10px] bg-zinc-800 text-zinc-400 rounded px-1.5 py-0.5 border border-zinc-700/50">
                        {change.type}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default TrustMatrix;
