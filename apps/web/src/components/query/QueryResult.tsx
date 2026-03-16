'use client';

import React, { useEffect, useRef } from 'react';
import {
  BookOpen,
  TrendingUp,
  Target,
  ShieldAlert,
  Sparkles,
} from 'lucide-react';

interface Citation {
  node_id: string;
  label: string;
  relevance: number;
}

interface QueryResultData {
  answer: string;
  citations: Citation[];
  patterns_detected: string[];
  confidence: number;
  escalation_stage?: number;
  ripeness_score?: number;
}

interface QueryResultProps {
  result: QueryResultData | null;
  streaming?: string;
}

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

function labelColor(label: string): string {
  return NODE_COLORS[label.toLowerCase()] ?? '#71717a';
}

function confidenceColor(c: number): string {
  if (c >= 0.75) return '#22c55e';
  if (c >= 0.5) return '#f97316';
  return '#ef4444';
}

function glaslLabel(stage?: number): string {
  const labels: Record<number, string> = {
    1: 'Hardening',
    2: 'Debates',
    3: 'Actions not words',
    4: 'Images & coalitions',
    5: 'Loss of face',
    6: 'Threat strategies',
    7: 'Limited strikes',
    8: 'Fragmentation',
    9: 'Together into the abyss',
  };
  return stage !== undefined ? (labels[stage] ?? `Stage ${stage}`) : '—';
}

function MetricCard({
  icon: Icon,
  label,
  value,
  valueColor,
  sub,
}: {
  icon: React.ElementType;
  label: string;
  value: string;
  valueColor?: string;
  sub?: string;
}) {
  return (
    <div className="rounded-lg border border-[#27272a] bg-[#09090b] px-3 py-2.5">
      <div className="flex items-center gap-1.5 mb-1">
        <Icon className="h-3 w-3 text-zinc-500" />
        <span className="text-[10px] uppercase tracking-widest text-zinc-500 font-semibold">
          {label}
        </span>
      </div>
      <p
        className="text-lg font-bold tabular-nums leading-none"
        style={{ color: valueColor ?? '#e4e4e7' }}
      >
        {value}
      </p>
      {sub && <p className="text-[10px] text-zinc-600 mt-1">{sub}</p>}
    </div>
  );
}

export function QueryResult({ result, streaming }: QueryResultProps) {
  const streamRef = useRef<HTMLDivElement>(null);

  // Auto-scroll streaming content
  useEffect(() => {
    if (streaming && streamRef.current) {
      streamRef.current.scrollTop = streamRef.current.scrollHeight;
    }
  }, [streaming]);

  // Streaming state
  if (!result && streaming !== undefined) {
    return (
      <div className="rounded-xl border border-[#27272a] bg-[#18181b] overflow-hidden">
        <div className="flex items-center gap-2 border-b border-[#27272a] px-4 py-2.5">
          <Sparkles className="h-3.5 w-3.5 text-teal-500 animate-pulse" />
          <span className="text-xs font-semibold text-zinc-300">Analyzing…</span>
        </div>
        <div
          ref={streamRef}
          className="p-4 max-h-64 overflow-y-auto"
        >
          <p className="text-sm text-zinc-300 leading-relaxed whitespace-pre-wrap">
            {streaming}
            <span className="inline-block h-3.5 w-0.5 bg-teal-500 animate-pulse ml-0.5 align-middle" />
          </p>
        </div>
      </div>
    );
  }

  if (!result) return null;

  const conf = result.confidence ?? 0;
  const confPct = Math.round(conf * 100);

  return (
    <div className="space-y-4">
      {/* Key metrics row */}
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
        <MetricCard
          icon={Target}
          label="Confidence"
          value={`${confPct}%`}
          valueColor={confidenceColor(conf)}
        />
        {result.escalation_stage !== undefined && (
          <MetricCard
            icon={TrendingUp}
            label="Glasl Stage"
            value={String(result.escalation_stage)}
            valueColor="#ef4444"
            sub={glaslLabel(result.escalation_stage)}
          />
        )}
        {result.ripeness_score !== undefined && (
          <MetricCard
            icon={ShieldAlert}
            label="Ripeness"
            value={`${Math.round(result.ripeness_score * 100)}%`}
            valueColor={result.ripeness_score >= 0.6 ? '#22c55e' : '#f97316'}
            sub={result.ripeness_score >= 0.6 ? 'Ripe for negotiation' : 'Not yet ripe'}
          />
        )}
        {result.patterns_detected.length > 0 && (
          <MetricCard
            icon={Sparkles}
            label="Patterns"
            value={String(result.patterns_detected.length)}
            valueColor="#a855f7"
            sub="detected"
          />
        )}
      </div>

      {/* Answer */}
      <div className="rounded-xl border border-[#27272a] bg-[#18181b] overflow-hidden">
        <div className="flex items-center gap-2 border-b border-[#27272a] px-4 py-2.5">
          <BookOpen className="h-3.5 w-3.5 text-teal-500" />
          <span className="text-xs font-semibold text-zinc-300">Analysis</span>
        </div>
        <div className="p-4">
          {streaming ? (
            <p className="text-sm text-zinc-300 leading-relaxed whitespace-pre-wrap">
              {streaming}
              <span className="inline-block h-3.5 w-0.5 bg-teal-500 animate-pulse ml-0.5 align-middle" />
            </p>
          ) : (
            <p className="text-sm text-zinc-300 leading-relaxed whitespace-pre-wrap">
              {result.answer}
            </p>
          )}
        </div>
      </div>

      {/* Patterns */}
      {result.patterns_detected.length > 0 && (
        <div>
          <p className="mb-2 text-[10px] font-semibold uppercase tracking-widest text-zinc-500">
            Detected Patterns
          </p>
          <div className="flex flex-wrap gap-1.5">
            {result.patterns_detected.map((p) => (
              <span
                key={p}
                className="rounded-full border border-purple-800/40 bg-purple-950/30 px-2.5 py-1
                           text-[11px] font-medium text-purple-300"
              >
                {p}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Citations */}
      {result.citations.length > 0 && (
        <div>
          <p className="mb-2 text-[10px] font-semibold uppercase tracking-widest text-zinc-500">
            Citations
          </p>
          <div className="flex flex-wrap gap-1.5">
            {result.citations.map((c) => {
              const color = labelColor(c.label);
              const relPct = Math.round(c.relevance * 100);
              return (
                <div
                  key={c.node_id}
                  className="flex items-center gap-1.5 rounded-full border px-2.5 py-1"
                  style={{
                    borderColor: `${color}40`,
                    backgroundColor: `${color}10`,
                  }}
                  title={`Relevance: ${relPct}%`}
                >
                  <span
                    className="h-1.5 w-1.5 rounded-full flex-shrink-0"
                    style={{ backgroundColor: color }}
                  />
                  <span className="text-[11px] font-medium" style={{ color }}>
                    {c.label}
                  </span>
                  <span className="text-[10px] text-zinc-500 font-mono">
                    {c.node_id.slice(0, 8)}
                  </span>
                  <span
                    className="text-[10px] tabular-nums"
                    style={{ color: `${color}aa` }}
                  >
                    {relPct}%
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

export default QueryResult;