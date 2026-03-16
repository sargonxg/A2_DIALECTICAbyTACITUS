'use client';

import React, { useEffect, useState } from 'react';
import { Loader2, AlertTriangle, TrendingUp } from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
  Legend,
  Area,
  AreaChart,
} from 'recharts';
import { graphApi, reasoningApi } from '@/lib/api';
import type { GraphNode, EscalationAssessment } from '@/lib/api';

const GLASL_BANDS = [
  { stage: 1, label: 'S1 Harden',    y: 0.11 },
  { stage: 2, label: 'S2 Debate',    y: 0.22 },
  { stage: 3, label: 'S3 Actions',   y: 0.33 },
  { stage: 4, label: 'S4 Images',    y: 0.44 },
  { stage: 5, label: 'S5 Face',      y: 0.56 },
  { stage: 6, label: 'S6 Threats',   y: 0.67 },
  { stage: 7, label: 'S7 Strikes',   y: 0.78 },
  { stage: 8, label: 'S8 Fragment',  y: 0.89 },
  { stage: 9, label: 'S9 Abyss',     y: 1.00 },
];

interface ChartPoint {
  date: string;
  severity: number;
  forecast?: number;
  forecastConf?: number;
  isForecast?: boolean;
}

function formatXTick(dateStr: string): string {
  try {
    return new Date(dateStr).toLocaleDateString('en-GB', {
      month: 'short',
      day: 'numeric',
    });
  } catch {
    return dateStr;
  }
}

function getSeverity(node: GraphNode): number {
  const s = node.properties?.severity ?? node.properties?.intensity;
  if (typeof s === 'number') return Math.min(1, Math.max(0, s));
  if (typeof s === 'string') return Math.min(1, Math.max(0, parseFloat(s) || 0));
  return 0;
}

function getDate(node: GraphNode): string | null {
  const d =
    node.properties?.occurred_at ??
    node.properties?.date ??
    node.properties?.timestamp;
  return typeof d === 'string' ? d : null;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function CustomTooltip({ active, payload, label }: any) {
  if (!active || !payload || payload.length === 0) return null;
  return (
    <div className="rounded-lg border border-[#27272a] bg-[#18181b] px-3 py-2 shadow-xl text-xs">
      <p className="text-zinc-400 mb-1">{formatXTick(label)}</p>
      {payload.map(
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        (p: any) =>
          p.value !== undefined && (
            <p key={p.name} style={{ color: p.color }}>
              {p.name}: {(p.value * 100).toFixed(0)}%
            </p>
          ),
      )}
    </div>
  );
}

interface EscalationChartProps {
  workspaceId: string;
}

export function EscalationChart({ workspaceId }: EscalationChartProps) {
  const [chartData, setChartData] = useState<ChartPoint[]>([]);
  const [assessment, setAssessment] = useState<EscalationAssessment | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);

    Promise.all([
      graphApi.getNodes(workspaceId, 'Event'),
      reasoningApi.getEscalation(workspaceId).catch(() => null),
    ])
      .then(([{ nodes }, esc]) => {
        setAssessment(esc);

        // Build historical points from events
        const historical: ChartPoint[] = nodes
          .filter((n) => !!getDate(n))
          .map((n) => ({
            date: getDate(n)!,
            severity: getSeverity(n),
          }))
          .sort((a, b) => a.date.localeCompare(b.date));

        // Append forecast trajectory if available
        const forecastPoints: ChartPoint[] = (esc?.forecast?.trajectory ?? []).map(
          (t) => ({
            date: t.timestamp,
            severity: historical[historical.length - 1]?.severity ?? 0,
            forecast: t.predicted_stage / 9,
            forecastConf: t.confidence,
            isForecast: true,
          }),
        );

        // Merge: last historical point gets forecast value too
        const merged: ChartPoint[] = [...historical];
        if (forecastPoints.length > 0 && merged.length > 0) {
          const last = merged[merged.length - 1];
          merged[merged.length - 1] = {
            ...last,
            forecast: last.severity,
          };
          merged.push(...forecastPoints);
        }

        setChartData(merged);
        setLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message);
        setLoading(false);
      });
  }, [workspaceId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center gap-2 py-12 text-zinc-500">
        <Loader2 className="h-4 w-4 animate-spin" />
        <span className="text-sm">Loading escalation data…</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center gap-2 rounded-lg border border-red-900/40 bg-red-950/20 px-4 py-3 text-sm text-red-400">
        <AlertTriangle className="h-4 w-4 flex-shrink-0" />
        <span>{error}</span>
      </div>
    );
  }

  if (chartData.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center gap-3 py-16 text-center">
        <TrendingUp className="h-8 w-8 text-zinc-700" />
        <p className="text-sm text-zinc-500">No escalation data available</p>
        <p className="text-xs text-zinc-600">
          Events with severity values will appear here over time.
        </p>
      </div>
    );
  }

  const hasForecast = chartData.some((d) => d.forecast !== undefined);

  return (
    <div className="space-y-4">
      {/* Assessment summary */}
      {assessment && (
        <div className="grid grid-cols-3 gap-2">
          <div className="rounded-lg border border-[#27272a] bg-[#09090b] px-3 py-2">
            <p className="text-[10px] uppercase tracking-widest text-zinc-500 font-semibold mb-1">
              Current Stage
            </p>
            <p className="text-lg font-bold text-red-400 tabular-nums">
              {assessment.stage_number ?? '—'}
            </p>
            <p className="text-[10px] text-zinc-600 mt-0.5 truncate">{assessment.stage}</p>
          </div>
          <div className="rounded-lg border border-[#27272a] bg-[#09090b] px-3 py-2">
            <p className="text-[10px] uppercase tracking-widest text-zinc-500 font-semibold mb-1">
              Trajectory
            </p>
            <p className="text-sm font-semibold text-zinc-300 capitalize">
              {assessment.forecast?.direction ?? '—'}
            </p>
          </div>
          <div className="rounded-lg border border-[#27272a] bg-[#09090b] px-3 py-2">
            <p className="text-[10px] uppercase tracking-widest text-zinc-500 font-semibold mb-1">
              Confidence
            </p>
            <p className="text-lg font-bold text-teal-400 tabular-nums">
              {Math.round((assessment.confidence ?? 0) * 100)}%
            </p>
          </div>
        </div>
      )}

      {/* Chart */}
      <ResponsiveContainer width="100%" height={280}>
        <AreaChart data={chartData} margin={{ top: 10, right: 16, left: -10, bottom: 0 }}>
          <defs>
            <linearGradient id="severityGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#ef4444" stopOpacity={0.25} />
              <stop offset="95%" stopColor="#ef4444" stopOpacity={0.03} />
            </linearGradient>
            <linearGradient id="forecastGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#0d9488" stopOpacity={0.2} />
              <stop offset="95%" stopColor="#0d9488" stopOpacity={0.02} />
            </linearGradient>
          </defs>

          <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />

          <XAxis
            dataKey="date"
            tickFormatter={formatXTick}
            tick={{ fill: '#71717a', fontSize: 10 }}
            axisLine={{ stroke: '#27272a' }}
            tickLine={false}
          />
          <YAxis
            domain={[0, 1]}
            tickFormatter={(v: number) => `${Math.round(v * 9)}`}
            tick={{ fill: '#71717a', fontSize: 10 }}
            axisLine={{ stroke: '#27272a' }}
            tickLine={false}
            label={{
              value: 'Glasl Stage',
              angle: -90,
              position: 'insideLeft',
              offset: 16,
              fill: '#52525b',
              fontSize: 9,
            }}
          />

          <Tooltip content={<CustomTooltip />} />

          {/* Glasl band lines */}
          {GLASL_BANDS.slice(0, -1).map((b) => (
            <ReferenceLine
              key={b.stage}
              y={b.y}
              stroke="#27272a"
              strokeDasharray="4 4"
              label={{
                value: b.label,
                position: 'insideTopRight',
                fill: '#3f3f46',
                fontSize: 8,
              }}
            />
          ))}

          <Area
            type="monotone"
            dataKey="severity"
            stroke="#ef4444"
            strokeWidth={2}
            fill="url(#severityGrad)"
            dot={false}
            activeDot={{ r: 4, fill: '#ef4444' }}
            name="Severity"
            connectNulls
          />

          {hasForecast && (
            <Area
              type="monotone"
              dataKey="forecast"
              stroke="#0d9488"
              strokeWidth={2}
              strokeDasharray="5 4"
              fill="url(#forecastGrad)"
              dot={false}
              activeDot={{ r: 4, fill: '#0d9488' }}
              name="Forecast"
              connectNulls
            />
          )}

          {hasForecast && (
            <Legend
              wrapperStyle={{ fontSize: 11, color: '#71717a', paddingTop: 8 }}
            />
          )}
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

export default EscalationChart;