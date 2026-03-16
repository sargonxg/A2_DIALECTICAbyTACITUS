'use client';

import React from 'react';
import { RadialBarChart, RadialBar, ResponsiveContainer, PolarAngleAxis } from 'recharts';
import { CheckCircle2, XCircle, Target, TrendingUp, Layers } from 'lucide-react';
import type { RipenessAssessment } from '@/lib/api';

interface RipenessGaugeProps {
  data: RipenessAssessment;
}

interface ArcGaugeProps {
  value: number; // 0–1
  color: string;
  size?: number;
  strokeWidth?: number;
  label: string;
  sublabel?: string;
  icon: React.ReactNode;
}

function ArcGauge({ value, color, size = 120, strokeWidth = 10, label, sublabel, icon }: ArcGaugeProps) {
  const pct = Math.min(1, Math.max(0, value));
  const chartData = [{ name: label, value: Math.round(pct * 100), fill: color }];

  return (
    <div className="flex flex-col items-center gap-1">
      <div style={{ width: size, height: size }} className="relative">
        <ResponsiveContainer width="100%" height="100%">
          <RadialBarChart
            cx="50%"
            cy="50%"
            innerRadius="65%"
            outerRadius="100%"
            barSize={strokeWidth}
            data={chartData}
            startAngle={220}
            endAngle={-40}
          >
            <PolarAngleAxis type="number" domain={[0, 100]} angleAxisId={0} tick={false} />
            <RadialBar
              background={{ fill: '#27272a' }}
              dataKey="value"
              angleAxisId={0}
              cornerRadius={strokeWidth / 2}
            />
          </RadialBarChart>
        </ResponsiveContainer>
        {/* Center content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
          <span style={{ color }} className="text-lg font-bold leading-none">
            {Math.round(pct * 100)}
          </span>
          <span className="text-[10px] text-zinc-500 leading-none mt-0.5">/100</span>
        </div>
      </div>
      <div className="flex items-center gap-1 text-zinc-300 text-xs font-medium">
        <span style={{ color }} className="opacity-80">{icon}</span>
        {label}
      </div>
      {sublabel && <p className="text-[10px] text-zinc-500 text-center max-w-[100px]">{sublabel}</p>}
    </div>
  );
}

function ScoreBar({
  label,
  value,
  color,
  description,
}: {
  label: string;
  value: number;
  color: string;
  description: string;
}) {
  const pct = Math.round(value * 100);
  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between text-xs">
        <div className="flex items-center gap-1.5">
          <span className="text-zinc-300 font-medium">{label}</span>
          <span className="text-zinc-500 hidden sm:inline">— {description}</span>
        </div>
        <span className="font-semibold tabular-nums" style={{ color }}>
          {pct}%
        </span>
      </div>
      <div className="h-2 rounded-full bg-zinc-800 overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-700 ease-out"
          style={{ width: `${pct}%`, backgroundColor: color }}
        />
      </div>
    </div>
  );
}

export function RipenessGauge({ data }: RipenessGaugeProps) {
  const { mhs_score, meo_score, overall_score, is_ripe, factors } = data;

  const overallColor = overall_score >= 0.7 ? '#22c55e' : overall_score >= 0.4 ? '#eab308' : '#ef4444';
  const mhsColor = '#0d9488'; // teal-600
  const meoColor = '#6366f1'; // indigo-500

  const factorEntries = Object.entries(factors).filter(
    ([, v]) => typeof v === 'number' || typeof v === 'boolean',
  );

  return (
    <div className="rounded-xl border border-[#27272a] bg-[#18181b] p-5 space-y-5">
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="space-y-0.5">
          <div className="flex items-center gap-2">
            <Target className="w-4 h-4 text-zinc-400" />
            <span className="text-xs font-semibold uppercase tracking-widest text-zinc-400">
              Ripeness Assessment
            </span>
          </div>
          <p className="text-sm text-zinc-400">Zartman Mutually Hurting Stalemate Model</p>
        </div>

        {/* Ripe badge */}
        <div
          className={[
            'flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-sm font-semibold',
            is_ripe
              ? 'bg-green-500/15 border-green-500/40 text-green-400'
              : 'bg-zinc-700/30 border-zinc-600/40 text-zinc-400',
          ].join(' ')}
        >
          {is_ripe ? (
            <>
              <CheckCircle2 className="w-4 h-4" />
              Ripe for Resolution
            </>
          ) : (
            <>
              <XCircle className="w-4 h-4" />
              Not Yet Ripe
            </>
          )}
        </div>
      </div>

      {/* Three gauges row */}
      <div className="grid grid-cols-3 gap-2 pt-1">
        <ArcGauge
          value={mhs_score}
          color={mhsColor}
          label="MHS"
          sublabel="Mutually Hurting Stalemate"
          icon={<TrendingUp className="w-3 h-3 inline" />}
        />
        <ArcGauge
          value={overall_score}
          color={overallColor}
          size={132}
          strokeWidth={12}
          label="Overall"
          sublabel="Composite Ripeness"
          icon={<Target className="w-3 h-3 inline" />}
        />
        <ArcGauge
          value={meo_score}
          color={meoColor}
          label="MEO"
          sublabel="Mutually Enticing Opportunity"
          icon={<Layers className="w-3 h-3 inline" />}
        />
      </div>

      {/* Divider */}
      <div className="border-t border-[#27272a]" />

      {/* Score bars */}
      <div className="space-y-3">
        <ScoreBar
          label="MHS Score"
          value={mhs_score}
          color={mhsColor}
          description="Cost of continued conflict"
        />
        <ScoreBar
          label="MEO Score"
          value={meo_score}
          color={meoColor}
          description="Attractiveness of settlement"
        />
        <ScoreBar
          label="Overall Ripeness"
          value={overall_score}
          color={overallColor}
          description="Combined assessment"
        />
      </div>

      {/* Factors (if present) */}
      {factorEntries.length > 0 && (
        <>
          <div className="border-t border-[#27272a]" />
          <div className="space-y-2">
            <p className="text-[10px] font-semibold uppercase tracking-widest text-zinc-500">
              Contributing Factors
            </p>
            <div className="grid grid-cols-2 gap-2">
              {factorEntries.map(([key, val]) => {
                const isBool = typeof val === 'boolean';
                const numVal = isBool ? (val ? 1 : 0) : (val as number);
                const display = isBool ? (val ? 'Yes' : 'No') : `${Math.round((val as number) * 100)}%`;
                const color = isBool
                  ? val
                    ? '#22c55e'
                    : '#71717a'
                  : numVal >= 0.6
                  ? '#22c55e'
                  : numVal >= 0.3
                  ? '#eab308'
                  : '#ef4444';

                return (
                  <div
                    key={key}
                    className="flex items-center justify-between rounded-lg border border-[#27272a] bg-zinc-900/50 px-3 py-2"
                  >
                    <span className="text-xs text-zinc-400 capitalize">
                      {key.replace(/_/g, ' ')}
                    </span>
                    <span className="text-xs font-semibold" style={{ color }}>
                      {display}
                    </span>
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

export default RipenessGauge;
