'use client';

import React, { useState } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { Zap, Crown, AlertTriangle, ChevronDown, ChevronUp } from 'lucide-react';
import type { PowerMap as PowerMapData } from '@/lib/api';

interface PowerMapProps {
  data: PowerMapData;
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: { value: number; payload: { actor_a: string; actor_b: string; advantage_holder: string; score: number } }[];
}

function CustomTooltip({ active, payload }: CustomTooltipProps) {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="rounded-lg border border-[#27272a] bg-[#18181b] px-3 py-2 shadow-xl text-xs space-y-1">
      <p className="font-semibold text-zinc-200">
        {d.actor_a} vs {d.actor_b}
      </p>
      <p className="text-zinc-400">
        Advantage: <span className="text-teal-400 font-medium">{d.advantage_holder}</span>
      </p>
      <p className="text-zinc-400">
        Asymmetry Score: <span className="text-white font-semibold">{d.score.toFixed(2)}</span>
      </p>
    </div>
  );
}

function asym_color(score: number): string {
  if (score >= 0.7) return '#ef4444';
  if (score >= 0.4) return '#eab308';
  return '#22c55e';
}

export function PowerMap({ data }: PowerMapProps) {
  const { dyads, most_powerful, average_asymmetry, asymmetries } = data;
  const [expandedIdx, setExpandedIdx] = useState<number | null>(null);

  // Build bar chart data from asymmetries (top 8)
  const chartData = asymmetries.slice(0, 8).map((a) => ({
    name: `${a.actor_a.slice(0, 6)}…/${a.actor_b.slice(0, 6)}…`,
    fullName: `${a.actor_a} / ${a.actor_b}`,
    actor_a: a.actor_a,
    actor_b: a.actor_b,
    advantage_holder: a.advantage_holder,
    score: Math.round(a.score * 100) / 100,
  }));

  // Aggregate total power per actor from dyads
  const actorPower: Record<string, number> = {};
  dyads.forEach((d) => {
    actorPower[d.actor_id] = (actorPower[d.actor_id] ?? 0) + d.total_power;
  });
  const topActors = Object.entries(actorPower)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 5);

  return (
    <div className="rounded-xl border border-[#27272a] bg-[#18181b] p-5 space-y-5">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-0.5">
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-zinc-400" />
            <span className="text-xs font-semibold uppercase tracking-widest text-zinc-400">
              Power Map
            </span>
          </div>
          <p className="text-sm text-zinc-400">French–Raven Power Bases · Actor Asymmetries</p>
        </div>

        {/* Avg asymmetry */}
        <div className="rounded-lg border border-[#27272a] bg-zinc-900/50 px-3 py-2 text-center">
          <p className="text-[10px] uppercase tracking-widest text-zinc-500 font-medium">Avg Asymmetry</p>
          <p
            className="text-xl font-bold"
            style={{ color: asym_color(average_asymmetry) }}
          >
            {Math.round(average_asymmetry * 100)}%
          </p>
        </div>
      </div>

      {/* Most powerful actor */}
      {most_powerful && (
        <div className="flex items-center gap-2 rounded-lg border border-teal-600/30 bg-teal-600/10 px-4 py-2.5">
          <Crown className="w-4 h-4 text-teal-400 shrink-0" />
          <div>
            <p className="text-[10px] uppercase tracking-widest text-teal-600 font-medium">
              Most Powerful Actor
            </p>
            <p className="text-sm font-semibold text-teal-300">{most_powerful}</p>
          </div>
        </div>
      )}

      {/* Power asymmetry bar chart */}
      {chartData.length > 0 && (
        <div className="space-y-2">
          <p className="text-[10px] font-semibold uppercase tracking-widest text-zinc-500">
            Power Asymmetry by Dyad
          </p>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={chartData}
                layout="vertical"
                margin={{ top: 0, right: 16, bottom: 0, left: 8 }}
              >
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="#27272a"
                  horizontal={false}
                />
                <XAxis
                  type="number"
                  domain={[0, 1]}
                  tick={{ fill: '#71717a', fontSize: 10 }}
                  tickLine={false}
                  axisLine={{ stroke: '#27272a' }}
                  tickFormatter={(v: number) => `${Math.round(v * 100)}%`}
                />
                <YAxis
                  dataKey="name"
                  type="category"
                  tick={{ fill: '#a1a1aa', fontSize: 10 }}
                  tickLine={false}
                  axisLine={false}
                  width={80}
                />
                <Tooltip content={<CustomTooltip />} cursor={{ fill: '#27272a55' }} />
                <Bar dataKey="score" radius={[0, 4, 4, 0]} maxBarSize={18}>
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={asym_color(entry.score)} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Top actors by total power */}
      {topActors.length > 0 && (
        <div className="space-y-2">
          <p className="text-[10px] font-semibold uppercase tracking-widest text-zinc-500">
            Total Power by Actor
          </p>
          <div className="space-y-1.5">
            {topActors.map(([actor, power], i) => {
              const maxPower = topActors[0][1];
              const pct = maxPower > 0 ? (power / maxPower) * 100 : 0;
              const isMostPowerful = actor === most_powerful;
              return (
                <div key={actor} className="flex items-center gap-3">
                  <span
                    className="text-[11px] font-medium w-5 text-right shrink-0"
                    style={{ color: i === 0 ? '#0d9488' : '#71717a' }}
                  >
                    #{i + 1}
                  </span>
                  <span
                    className={[
                      'text-xs truncate w-32 shrink-0',
                      isMostPowerful ? 'text-teal-300 font-semibold' : 'text-zinc-300',
                    ].join(' ')}
                  >
                    {actor}
                  </span>
                  <div className="flex-1 h-2 rounded-full bg-zinc-800 overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-700"
                      style={{
                        width: `${pct}%`,
                        backgroundColor: isMostPowerful ? '#0d9488' : '#3f3f46',
                      }}
                    />
                  </div>
                  <span className="text-[11px] tabular-nums text-zinc-500 w-12 text-right shrink-0">
                    {power.toFixed(1)}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Asymmetries list */}
      {asymmetries.length > 0 && (
        <>
          <div className="border-t border-[#27272a]" />
          <div className="space-y-2">
            <p className="text-[10px] font-semibold uppercase tracking-widest text-zinc-500">
              Asymmetry Details & Recommendations
            </p>
            <div className="space-y-2">
              {asymmetries.slice(0, 6).map((asym, i) => {
                const isExpanded = expandedIdx === i;
                const color = asym_color(asym.score);
                return (
                  <div
                    key={i}
                    className="rounded-lg border border-[#27272a] bg-zinc-900/30 overflow-hidden"
                  >
                    <button
                      className="w-full flex items-center gap-3 px-3 py-2.5 text-left hover:bg-zinc-800/30 transition-colors"
                      onClick={() => setExpandedIdx(isExpanded ? null : i)}
                    >
                      <AlertTriangle className="w-3.5 h-3.5 shrink-0" style={{ color }} />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="text-xs font-medium text-zinc-300">{asym.actor_a}</span>
                          <span className="text-zinc-600 text-[11px]">vs</span>
                          <span className="text-xs text-zinc-300">{asym.actor_b}</span>
                          <span
                            className="text-[10px] font-semibold rounded px-1.5 py-0.5 border ml-auto"
                            style={{
                              color,
                              borderColor: `${color}40`,
                              backgroundColor: `${color}15`,
                            }}
                          >
                            {Math.round(asym.score * 100)}%
                          </span>
                        </div>
                        <p className="text-[11px] text-zinc-500 mt-0.5">
                          Advantage: <span className="text-teal-400">{asym.advantage_holder}</span>
                        </p>
                      </div>
                      {isExpanded ? (
                        <ChevronUp className="w-3.5 h-3.5 text-zinc-500 shrink-0" />
                      ) : (
                        <ChevronDown className="w-3.5 h-3.5 text-zinc-500 shrink-0" />
                      )}
                    </button>
                    {isExpanded && asym.recommendation && (
                      <div className="border-t border-[#27272a] px-3 py-2.5 bg-zinc-900/60">
                        <p className="text-[11px] text-zinc-400 leading-relaxed">
                          <span className="text-teal-600 font-medium">Recommendation: </span>
                          {asym.recommendation}
                        </p>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default PowerMap;
