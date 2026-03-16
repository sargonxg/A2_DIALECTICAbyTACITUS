'use client';

import React, { useState } from 'react';
import {
  ChevronDown,
  ChevronUp,
  Play,
  Search,
  Brain,
  Layers,
  CheckCircle2,
  Clock,
} from 'lucide-react';

interface TraceStep {
  step: string;
  detail?: string;
  data?: unknown;
}

interface ReasoningTraceProps {
  steps: TraceStep[];
}

const STEP_META: Record<
  string,
  { label: string; icon: React.ElementType; color: string }
> = {
  started:   { label: 'Query Received',       icon: Play,         color: '#06b6d4' },
  retrieval: { label: 'Graph Retrieval',       icon: Search,       color: '#3b82f6' },
  symbolic:  { label: 'Symbolic Reasoning',    icon: Brain,        color: '#a855f7' },
  synthesis: { label: 'Answer Synthesis',      icon: Layers,       color: '#f97316' },
  complete:  { label: 'Analysis Complete',     icon: CheckCircle2, color: '#22c55e' },
};

function getStepMeta(step: string) {
  const key = Object.keys(STEP_META).find((k) =>
    step.toLowerCase().includes(k),
  );
  return key
    ? STEP_META[key]
    : { label: step, icon: Clock, color: '#71717a' };
}

function formatData(data: unknown): string | null {
  if (data === undefined || data === null) return null;
  if (typeof data === 'string') return data;
  try {
    return JSON.stringify(data, null, 2);
  } catch {
    return String(data);
  }
}

export function ReasoningTrace({ steps }: ReasoningTraceProps) {
  const [collapsed, setCollapsed] = useState(false);
  const [expandedIdx, setExpandedIdx] = useState<number | null>(null);

  if (steps.length === 0) return null;

  return (
    <div className="rounded-xl border border-[#27272a] bg-[#18181b] overflow-hidden">
      {/* Header */}
      <button
        type="button"
        onClick={() => setCollapsed((v) => !v)}
        className="w-full flex items-center justify-between px-4 py-2.5 hover:bg-white/5 transition-colors"
      >
        <div className="flex items-center gap-2">
          <Brain className="h-3.5 w-3.5 text-teal-500" />
          <span className="text-xs font-semibold text-zinc-300">Reasoning Trace</span>
          <span className="rounded-full bg-zinc-800 px-1.5 py-0.5 text-[10px] text-zinc-400">
            {steps.length} steps
          </span>
        </div>
        {collapsed ? (
          <ChevronDown className="h-4 w-4 text-zinc-500" />
        ) : (
          <ChevronUp className="h-4 w-4 text-zinc-500" />
        )}
      </button>

      {!collapsed && (
        <div className="px-4 pb-4 pt-1">
          <div className="relative">
            {/* Vertical line */}
            <div className="absolute left-[11px] top-0 bottom-0 w-px bg-[#27272a]" />

            <div className="space-y-1">
              {steps.map((s, i) => {
                const meta = getStepMeta(s.step);
                const Icon = meta.icon;
                const isExpanded = expandedIdx === i;
                const hasDetail = !!(s.detail || s.data);

                return (
                  <div
                    key={i}
                    className="relative animate-in fade-in slide-in-from-left-2 duration-300"
                    style={{ animationDelay: `${i * 60}ms` }}
                  >
                    <div
                      className={[
                        'ml-6 rounded-lg p-2.5 transition-colors',
                        hasDetail ? 'cursor-pointer hover:bg-white/5' : '',
                      ].join(' ')}
                      onClick={() =>
                        hasDetail && setExpandedIdx(isExpanded ? null : i)
                      }
                    >
                      {/* Step row */}
                      <div className="flex items-start gap-2">
                        {/* Icon dot on the line */}
                        <div
                          className="absolute left-0 flex h-5.5 w-5.5 items-center justify-center rounded-full"
                          style={{ top: '10px' }}
                        >
                          <div
                            className="flex h-5 w-5 items-center justify-center rounded-full ring-2 ring-[#18181b]"
                            style={{ backgroundColor: `${meta.color}20`, border: `1px solid ${meta.color}50` }}
                          >
                            <Icon className="h-2.5 w-2.5" style={{ color: meta.color }} />
                          </div>
                        </div>

                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between gap-2">
                            <span className="text-xs font-medium text-zinc-300">
                              {meta.label}
                            </span>
                            {hasDetail && (
                              <span className="text-[10px] text-zinc-600">
                                {isExpanded ? 'hide' : 'show'}
                              </span>
                            )}
                          </div>
                          {s.detail && (
                            <p className="text-[11px] text-zinc-500 mt-0.5 leading-relaxed">
                              {s.detail}
                            </p>
                          )}
                        </div>
                      </div>

                      {/* Expanded data */}
                      {isExpanded && s.data !== undefined && (
                        <div className="mt-2 rounded-lg bg-[#09090b] border border-[#27272a] p-2.5">
                          <pre className="text-[10px] text-zinc-400 font-mono whitespace-pre-wrap break-all overflow-auto max-h-48">
                            {formatData(s.data)}
                          </pre>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ReasoningTrace;