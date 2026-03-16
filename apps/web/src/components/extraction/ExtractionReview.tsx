'use client';

import React, { useEffect, useState, useCallback } from 'react';
import {
  CheckCircle2,
  XCircle,
  CheckCheck,
  Ban,
  Loader2,
  AlertTriangle,
  ScanLine,
} from 'lucide-react';
import { graphApi } from '@/lib/api';
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

function labelColor(label: string): string {
  return NODE_COLORS[label.toLowerCase()] ?? '#71717a';
}

function getConfidence(node: GraphNode): number | undefined {
  const c = node.properties?.confidence ?? node.properties?.extraction_confidence;
  if (typeof c === 'number') return c;
  if (typeof c === 'string') return parseFloat(c) || undefined;
  return undefined;
}

function confidenceColor(c: number): string {
  if (c >= 0.75) return '#22c55e';
  if (c >= 0.5) return '#f97316';
  return '#ef4444';
}

function getCreatedAt(node: GraphNode): string | null {
  const d = node.properties?.created_at ?? node.properties?.extracted_at;
  return typeof d === 'string' ? d : null;
}

interface ExtractionReviewProps {
  workspaceId: string;
}

export function ExtractionReview({ workspaceId }: ExtractionReviewProps) {
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [accepted, setAccepted] = useState<Set<string>>(new Set());
  const [rejected, setRejected] = useState<Set<string>>(new Set());

  const fetchNodes = useCallback(() => {
    setLoading(true);
    setError(null);
    graphApi
      .getNodes(workspaceId)
      .then(({ nodes: all }) => {
        // Take last 20 sorted by created_at desc
        const sorted = [...all]
          .sort((a, b) => {
            const da = getCreatedAt(a) ?? '';
            const db = getCreatedAt(b) ?? '';
            return db.localeCompare(da);
          })
          .slice(0, 20);
        setNodes(sorted);
        setLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message);
        setLoading(false);
      });
  }, [workspaceId]);

  useEffect(() => {
    fetchNodes();
  }, [fetchNodes]);

  const handleAccept = (id: string) => {
    setAccepted((prev) => new Set(prev).add(id));
    setRejected((prev) => {
      const next = new Set(prev);
      next.delete(id);
      return next;
    });
  };

  const handleReject = (id: string) => {
    setRejected((prev) => new Set(prev).add(id));
    setAccepted((prev) => {
      const next = new Set(prev);
      next.delete(id);
      return next;
    });
  };

  const handleBatchAccept = () => {
    const pendingIds = nodes
      .filter((n) => !accepted.has(n.id) && !rejected.has(n.id))
      .map((n) => n.id);
    setAccepted((prev) => new Set([...prev, ...pendingIds]));
  };

  const handleBatchReject = () => {
    const pendingIds = nodes
      .filter((n) => !accepted.has(n.id) && !rejected.has(n.id))
      .map((n) => n.id);
    setRejected((prev) => new Set([...prev, ...pendingIds]));
  };

  const pending = nodes.filter((n) => !accepted.has(n.id) && !rejected.has(n.id));
  const reviewedCount = accepted.size + rejected.size;

  if (loading) {
    return (
      <div className="flex items-center justify-center gap-2 py-12 text-zinc-500">
        <Loader2 className="h-4 w-4 animate-spin" />
        <span className="text-sm">Loading extracted nodes…</span>
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

  if (nodes.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center gap-3 py-16 text-center">
        <ScanLine className="h-8 w-8 text-zinc-700" />
        <p className="text-sm text-zinc-500">No extracted nodes to review</p>
        <p className="text-xs text-zinc-600">
          Upload and ingest a document to see extracted entities here.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Summary bar */}
      <div className="flex items-center justify-between gap-2 flex-wrap">
        <div className="flex items-center gap-3">
          <span className="text-xs text-zinc-500">
            {reviewedCount}/{nodes.length} reviewed
          </span>
          {pending.length > 0 && (
            <span className="rounded-full bg-zinc-800 px-2 py-0.5 text-[10px] text-zinc-400">
              {pending.length} pending
            </span>
          )}
        </div>

        {/* Batch controls */}
        {pending.length > 0 && (
          <div className="flex gap-2">
            <button
              type="button"
              onClick={handleBatchAccept}
              className="flex items-center gap-1.5 rounded-lg border border-emerald-800/40 bg-emerald-950/20
                         px-2.5 py-1.5 text-xs font-medium text-emerald-400 transition-colors
                         hover:bg-emerald-950/40"
            >
              <CheckCheck className="h-3.5 w-3.5" />
              Accept All
            </button>
            <button
              type="button"
              onClick={handleBatchReject}
              className="flex items-center gap-1.5 rounded-lg border border-red-900/40 bg-red-950/20
                         px-2.5 py-1.5 text-xs font-medium text-red-400 transition-colors
                         hover:bg-red-950/40"
            >
              <Ban className="h-3.5 w-3.5" />
              Reject All
            </button>
          </div>
        )}
      </div>

      {/* Node list */}
      <div className="space-y-1.5">
        {nodes.map((node) => {
          const color = labelColor(node.label);
          const confidence = getConfidence(node);
          const isAccepted = accepted.has(node.id);
          const isRejected = rejected.has(node.id);

          return (
            <div
              key={node.id}
              className={[
                'flex items-center gap-3 rounded-lg border px-3 py-2.5 transition-all duration-200',
                isAccepted
                  ? 'border-emerald-800/40 bg-emerald-950/15 opacity-70'
                  : isRejected
                  ? 'border-red-900/40 bg-red-950/15 opacity-50'
                  : 'border-[#27272a] bg-[#18181b]',
              ].join(' ')}
            >
              {/* Color dot */}
              <div
                className="h-2.5 w-2.5 flex-shrink-0 rounded-full"
                style={{ backgroundColor: color }}
              />

              {/* Label badge */}
              <span
                className="flex-shrink-0 rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider"
                style={{
                  backgroundColor: `${color}18`,
                  color,
                  border: `1px solid ${color}35`,
                }}
              >
                {node.label}
              </span>

              {/* Name */}
              <p className="flex-1 min-w-0 text-sm text-zinc-200 truncate">
                {node.name || node.id}
              </p>

              {/* Confidence */}
              {confidence !== undefined && (
                <div className="flex items-center gap-1.5 flex-shrink-0">
                  <div className="w-16 h-1 rounded-full bg-zinc-800">
                    <div
                      className="h-full rounded-full"
                      style={{
                        width: `${Math.round(confidence * 100)}%`,
                        backgroundColor: confidenceColor(confidence),
                      }}
                    />
                  </div>
                  <span
                    className="text-[10px] tabular-nums w-7"
                    style={{ color: confidenceColor(confidence) }}
                  >
                    {Math.round(confidence * 100)}%
                  </span>
                </div>
              )}

              {/* Status indicator or action buttons */}
              {isAccepted ? (
                <CheckCircle2 className="h-4 w-4 flex-shrink-0 text-emerald-500" />
              ) : isRejected ? (
                <XCircle className="h-4 w-4 flex-shrink-0 text-red-500" />
              ) : (
                <div className="flex gap-1 flex-shrink-0">
                  <button
                    type="button"
                    onClick={() => handleAccept(node.id)}
                    title="Accept"
                    className="rounded-md p-1 text-zinc-500 hover:text-emerald-400 hover:bg-emerald-950/30 transition-colors"
                  >
                    <CheckCircle2 className="h-4 w-4" />
                  </button>
                  <button
                    type="button"
                    onClick={() => handleReject(node.id)}
                    title="Reject"
                    className="rounded-md p-1 text-zinc-500 hover:text-red-400 hover:bg-red-950/30 transition-colors"
                  >
                    <XCircle className="h-4 w-4" />
                  </button>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default ExtractionReview;