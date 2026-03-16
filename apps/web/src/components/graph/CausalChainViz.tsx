'use client';

import React, { useEffect, useState } from 'react';
import { GitBranch, AlertCircle, Loader2, ArrowDown } from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

interface CausalEvent {
  id: string;
  name: string;
  label?: string;
  description?: string;
  severity?: number;
}

interface CausalChain {
  root_cause: CausalEvent;
  chain: CausalEvent[];
}

interface CausalData {
  chains: CausalChain[];
  summary?: string;
}

const EVENT_COLORS: Record<string, string> = {
  trigger:    '#f97316',
  escalation: '#ef4444',
  mediation:  '#22c55e',
  ceasefire:  '#06b6d4',
  default:    '#6366f1',
};

function eventColor(label?: string): string {
  if (!label) return EVENT_COLORS.default;
  const l = label.toLowerCase();
  for (const key of Object.keys(EVENT_COLORS)) {
    if (l.includes(key)) return EVENT_COLORS[key];
  }
  return EVENT_COLORS.default;
}

function severityBar(severity?: number) {
  if (severity === undefined) return null;
  const pct = Math.round(severity * 100);
  const color = severity > 0.7 ? '#ef4444' : severity > 0.4 ? '#f97316' : '#eab308';
  return (
    <div className="mt-1.5 flex items-center gap-2">
      <div className="flex-1 h-1 rounded-full bg-zinc-800">
        <div
          className="h-full rounded-full transition-all"
          style={{ width: `${pct}%`, backgroundColor: color }}
        />
      </div>
      <span className="text-[10px] text-zinc-500 tabular-nums w-7 text-right">{pct}%</span>
    </div>
  );
}

interface CausalChainVizProps {
  workspaceId: string;
}

export function CausalChainViz({ workspaceId }: CausalChainVizProps) {
  const [data, setData] = useState<CausalData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const apiKey =
      typeof window !== 'undefined'
        ? localStorage.getItem('dialectica_api_key') || ''
        : '';

    setLoading(true);
    setError(null);

    fetch(`${API_URL}/v1/workspaces/${workspaceId}/causation`, {
      headers: { 'X-API-Key': apiKey },
    })
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((json: CausalData) => {
        setData(json);
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
        <span className="text-sm">Loading causal chains…</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center gap-2 rounded-lg border border-red-900/40 bg-red-950/20 px-4 py-3 text-sm text-red-400">
        <AlertCircle className="h-4 w-4 flex-shrink-0" />
        <span>{error}</span>
      </div>
    );
  }

  const chains = data?.chains ?? [];

  if (chains.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center gap-3 py-12 text-center">
        <GitBranch className="h-8 w-8 text-zinc-700" />
        <p className="text-sm text-zinc-500">No causal chains detected</p>
        <p className="text-xs text-zinc-600">
          Add more event nodes with causal relationships to visualise chains.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {data?.summary && (
        <p className="text-sm text-zinc-400 leading-relaxed">{data.summary}</p>
      )}

      {chains.map((chain, ci) => {
        const allEvents = [chain.root_cause, ...chain.chain];
        return (
          <div
            key={ci}
            className="rounded-xl border border-[#27272a] bg-[#18181b] overflow-hidden"
          >
            {/* Chain header */}
            <div className="flex items-center gap-2 border-b border-[#27272a] px-4 py-2.5">
              <GitBranch className="h-3.5 w-3.5 text-teal-500" />
              <span className="text-[11px] font-semibold uppercase tracking-widest text-zinc-500">
                Causal Chain {ci + 1}
              </span>
              <span className="ml-auto rounded-full bg-zinc-800 px-2 py-0.5 text-[10px] text-zinc-400">
                {allEvents.length} events
              </span>
            </div>

            {/* Events */}
            <div className="px-4 py-4 space-y-0">
              {allEvents.map((evt, ei) => {
                const isRoot = ei === 0;
                const isLast = ei === allEvents.length - 1;
                const color = eventColor(evt.label);
                return (
                  <div key={evt.id ?? ei}>
                    {/* Event box */}
                    <div
                      className="relative rounded-lg border p-3"
                      style={{
                        borderColor: isRoot ? `${color}60` : '#27272a',
                        backgroundColor: isRoot ? `${color}10` : '#09090b',
                      }}
                    >
                      {/* Root cause badge */}
                      {isRoot && (
                        <span
                          className="mb-1.5 inline-block rounded-full px-2 py-0.5 text-[9px] font-bold uppercase tracking-widest"
                          style={{ backgroundColor: `${color}25`, color }}
                        >
                          Root Cause
                        </span>
                      )}
                      <p
                        className="text-sm font-medium leading-snug"
                        style={{ color: isRoot ? color : '#e4e4e7' }}
                      >
                        {evt.name || evt.id}
                      </p>
                      {evt.description && (
                        <p className="mt-1 text-xs text-zinc-500 leading-relaxed line-clamp-2">
                          {evt.description}
                        </p>
                      )}
                      {severityBar(evt.severity)}

                      {/* Label chip */}
                      {evt.label && (
                        <div className="mt-2">
                          <span
                            className="inline-block rounded-full px-1.5 py-0.5 text-[9px] font-medium uppercase tracking-wider"
                            style={{
                              backgroundColor: `${color}18`,
                              color: color,
                              border: `1px solid ${color}30`,
                            }}
                          >
                            {evt.label}
                          </span>
                        </div>
                      )}
                    </div>

                    {/* Arrow connector */}
                    {!isLast && (
                      <div className="flex justify-center py-1">
                        <ArrowDown className="h-4 w-4 text-zinc-600" />
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default CausalChainViz;