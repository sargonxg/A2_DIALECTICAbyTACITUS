'use client';

import React, { useEffect, useState } from 'react';
import { Calendar, AlertTriangle, Loader2, Clock } from 'lucide-react';
import { graphApi } from '@/lib/api';
import type { GraphNode } from '@/lib/api';

const EVENT_TYPE_COLORS: Record<string, string> = {
  ceasefire:   '#22c55e',
  negotiation: '#06b6d4',
  attack:      '#ef4444',
  protest:     '#f97316',
  election:    '#3b82f6',
  displacement:'#eab308',
  accord:      '#22c55e',
  sanction:    '#a855f7',
  default:     '#6366f1',
};

function eventTypeColor(type?: string): string {
  if (!type) return EVENT_TYPE_COLORS.default;
  const t = type.toLowerCase();
  for (const key of Object.keys(EVENT_TYPE_COLORS)) {
    if (t.includes(key)) return EVENT_TYPE_COLORS[key];
  }
  return EVENT_TYPE_COLORS.default;
}

function formatDate(dateStr?: string): string {
  if (!dateStr) return 'Unknown date';
  try {
    return new Date(dateStr).toLocaleDateString('en-GB', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    });
  } catch {
    return dateStr;
  }
}

function getSeverity(node: GraphNode): number | undefined {
  const s = node.properties?.severity ?? node.properties?.intensity;
  if (typeof s === 'number') return s;
  if (typeof s === 'string') return parseFloat(s) || undefined;
  return undefined;
}

function getEventType(node: GraphNode): string | undefined {
  const t = node.properties?.event_type ?? node.properties?.type;
  if (typeof t === 'string') return t;
  return undefined;
}

function getOccurredAt(node: GraphNode): string | undefined {
  const d =
    node.properties?.occurred_at ??
    node.properties?.date ??
    node.properties?.timestamp;
  if (typeof d === 'string') return d;
  return undefined;
}

interface EventTimelineProps {
  workspaceId: string;
}

export function EventTimeline({ workspaceId }: EventTimelineProps) {
  const [events, setEvents] = useState<GraphNode[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    graphApi
      .getNodes(workspaceId, 'Event')
      .then(({ nodes }) => {
        // Sort by occurred_at, most recent first
        const sorted = [...nodes].sort((a, b) => {
          const da = getOccurredAt(a) ?? '';
          const db = getOccurredAt(b) ?? '';
          return db.localeCompare(da);
        });
        setEvents(sorted);
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
        <span className="text-sm">Loading events…</span>
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

  if (events.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center gap-3 py-16 text-center">
        <Clock className="h-8 w-8 text-zinc-700" />
        <p className="text-sm text-zinc-500">No events recorded</p>
        <p className="text-xs text-zinc-600">
          Ingest documents with event mentions to populate the timeline.
        </p>
      </div>
    );
  }

  return (
    <div className="relative space-y-0">
      {/* Timeline rail */}
      <div className="absolute left-[88px] top-0 bottom-0 w-px bg-[#27272a]" />

      {events.map((evt, i) => {
        const eventType = getEventType(evt);
        const occurredAt = getOccurredAt(evt);
        const severity = getSeverity(evt);
        const description = evt.properties?.description as string | undefined;
        const color = eventTypeColor(eventType);

        return (
          <div key={evt.id ?? i} className="relative flex gap-4 pb-5 last:pb-0">
            {/* Date column */}
            <div className="w-20 flex-shrink-0 pt-0.5 text-right">
              <div className="flex items-center justify-end gap-1">
                <Calendar className="h-3 w-3 text-zinc-600 flex-shrink-0" />
                <span className="text-[10px] text-zinc-500 leading-tight">
                  {formatDate(occurredAt)}
                </span>
              </div>
            </div>

            {/* Dot */}
            <div className="relative z-10 flex-shrink-0 -ml-[4.5px] mt-[3px]">
              <div
                className="h-2.5 w-2.5 rounded-full ring-2 ring-[#09090b]"
                style={{ backgroundColor: color }}
              />
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0 rounded-lg border border-[#27272a] bg-[#18181b] p-3">
              <div className="flex items-start justify-between gap-2">
                <p className="text-sm font-medium text-zinc-200 leading-snug">
                  {evt.name || evt.id}
                </p>
                {eventType && (
                  <span
                    className="flex-shrink-0 rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider"
                    style={{
                      backgroundColor: `${color}20`,
                      color,
                      border: `1px solid ${color}40`,
                    }}
                  >
                    {eventType}
                  </span>
                )}
              </div>

              {description && (
                <p className="mt-1.5 text-xs text-zinc-500 leading-relaxed line-clamp-2">
                  {description}
                </p>
              )}

              {/* Severity bar */}
              {severity !== undefined && (
                <div className="mt-2 flex items-center gap-2">
                  <span className="text-[10px] text-zinc-600 w-12">Severity</span>
                  <div className="flex-1 h-1 rounded-full bg-zinc-800">
                    <div
                      className="h-full rounded-full transition-all"
                      style={{
                        width: `${Math.min(100, severity * 100)}%`,
                        backgroundColor:
                          severity > 0.7
                            ? '#ef4444'
                            : severity > 0.4
                            ? '#f97316'
                            : '#eab308',
                      }}
                    />
                  </div>
                  <span className="text-[10px] text-zinc-500 tabular-nums w-7 text-right">
                    {Math.round(severity * 100)}%
                  </span>
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default EventTimeline;