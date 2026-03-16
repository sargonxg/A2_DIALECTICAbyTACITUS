'use client';

import { useState, useRef } from 'react';
import { MessageSquare, ChevronDown, Loader2, AlertCircle, Sparkles } from 'lucide-react';
import { useWorkspaceList } from '@/hooks/useWorkspace';
import { reasoningApi } from '@/lib/api';
import { QueryInput } from '@/components/query/QueryInput';
import { QueryResult } from '@/components/query/QueryResult';
import { ReasoningTrace } from '@/components/query/ReasoningTrace';
import type { AnalysisResponse } from '@/lib/api';

const MODES = [
  { id: 'general',    label: 'General' },
  { id: 'escalation', label: 'Escalation' },
  { id: 'ripeness',   label: 'Ripeness' },
  { id: 'power',      label: 'Power' },
  { id: 'trust',      label: 'Trust' },
];

export default function AskPage() {
  const { workspaces, loading: wsLoading } = useWorkspaceList();

  const [selectedWorkspaceId, setSelectedWorkspaceId] = useState<string>('');
  const [mode, setMode] = useState('general');
  const [query, setQuery] = useState('');

  const [streaming, setStreaming] = useState(false);
  const [streamedText, setStreamedText] = useState('');
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState(false);

  const chunkBuffer = useRef('');

  function handleSubmit(q: string) {
    if (!selectedWorkspaceId || !q.trim() || streaming) return;

    setQuery(q);
    setStreaming(true);
    setStreamedText('');
    setResult(null);
    setError(null);
    setDone(false);
    chunkBuffer.current = '';

    reasoningApi.streamAnalyze(
      selectedWorkspaceId,
      q,
      mode,
      (chunk) => {
        // Chunks may be partial JSON or plain text deltas
        try {
          const parsed: AnalysisResponse = JSON.parse(chunk);
          setResult(parsed);
          setStreamedText(parsed.answer ?? '');
        } catch {
          chunkBuffer.current += chunk;
          setStreamedText(chunkBuffer.current);
        }
      },
      () => {
        setStreaming(false);
        setDone(true);
        // Attempt final parse of buffer
        if (!result) {
          try {
            const parsed: AnalysisResponse = JSON.parse(chunkBuffer.current);
            setResult(parsed);
          } catch {
            // leave as plain streamed text
          }
        }
      },
      (err) => {
        setStreaming(false);
        setError(err.message);
      },
    );
  }

  const selectedWorkspace = workspaces.find((w) => w.id === selectedWorkspaceId);

  return (
    <div className="min-h-full p-6 max-w-4xl mx-auto space-y-6">
      {/* Page header */}
      <div className="flex items-center gap-3">
        <div className="p-2 rounded-lg bg-violet-500/20 border border-violet-500/30">
          <MessageSquare className="w-5 h-5 text-violet-400" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-zinc-100">Ask the Graph</h1>
          <p className="text-sm text-zinc-500">Query your conflict knowledge graph with natural language.</p>
        </div>
      </div>

      {/* Workspace + mode selectors */}
      <div className="flex flex-col sm:flex-row gap-3">
        {/* Workspace selector */}
        <div className="flex-1 space-y-1.5">
          <label className="text-xs font-semibold uppercase tracking-widest text-zinc-500">
            Workspace
          </label>
          <div className="relative">
            {wsLoading ? (
              <div className="flex items-center gap-2 rounded-lg border border-[#27272a] bg-[#18181b] px-3 py-2.5">
                <Loader2 className="w-4 h-4 text-zinc-600 animate-spin" />
                <span className="text-sm text-zinc-600">Loading…</span>
              </div>
            ) : (
              <>
                <select
                  value={selectedWorkspaceId}
                  onChange={(e) => setSelectedWorkspaceId(e.target.value)}
                  className="w-full appearance-none rounded-lg border border-[#27272a] bg-[#18181b] px-3 py-2.5 pr-8 text-sm text-zinc-100 focus:border-violet-500/60 focus:outline-none focus:ring-1 focus:ring-violet-500/30 transition-colors"
                >
                  <option value="">Select a workspace…</option>
                  {workspaces.map((w) => (
                    <option key={w.id} value={w.id} className="bg-[#18181b]">
                      {w.name}
                    </option>
                  ))}
                </select>
                <ChevronDown className="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
              </>
            )}
          </div>
        </div>

        {/* Mode selector */}
        <div className="space-y-1.5">
          <label className="text-xs font-semibold uppercase tracking-widest text-zinc-500">
            Mode
          </label>
          <div className="flex items-center gap-1">
            {MODES.map((m) => (
              <button
                key={m.id}
                onClick={() => setMode(m.id)}
                className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
                  mode === m.id
                    ? 'bg-violet-500/20 text-violet-300 border border-violet-500/30'
                    : 'text-zinc-500 hover:text-zinc-300 hover:bg-[#27272a] border border-transparent'
                }`}
              >
                {m.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Selected workspace context */}
      {selectedWorkspace && (
        <div className="flex items-center gap-2 rounded-lg border border-[#27272a] bg-[#18181b] px-3 py-2">
          <Sparkles className="w-3.5 h-3.5 text-violet-400 shrink-0" />
          <span className="text-xs text-zinc-400">
            Querying <span className="text-zinc-200 font-medium">{selectedWorkspace.name}</span>
            {' '}· {selectedWorkspace.domain} · {selectedWorkspace.scale}
          </span>
        </div>
      )}

      {/* Query input */}
      <QueryInput
        onSubmit={handleSubmit}
        disabled={!selectedWorkspaceId || streaming}
        loading={streaming}
        placeholder="Ask anything about the conflict — actors, dynamics, escalation, opportunities…"
      />

      {/* Error */}
      {error && (
        <div className="rounded-xl border border-red-500/30 bg-red-500/5 p-4 flex items-start gap-3">
          <AlertCircle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
          <p className="text-sm text-zinc-400">{error}</p>
        </div>
      )}

      {/* Streaming / result display */}
      {(streaming || streamedText || result) && (
        <div className="space-y-4">
          {/* Live streaming text (before final parse) */}
          {streaming && !result && (
            <div className="rounded-xl border border-[#27272a] bg-[#18181b] p-5">
              <div className="flex items-center gap-2 mb-3">
                <Loader2 className="w-3.5 h-3.5 text-violet-400 animate-spin" />
                <span className="text-xs font-semibold uppercase tracking-widest text-zinc-500">
                  Analyzing…
                </span>
              </div>
              <p className="text-sm text-zinc-300 leading-relaxed whitespace-pre-wrap">
                {streamedText}
                <span className="inline-block w-0.5 h-4 bg-violet-400 animate-pulse align-middle ml-0.5" />
              </p>
            </div>
          )}

          {/* Final structured result */}
          {result && done && (
            <>
              <QueryResult result={result} query={query} />
              <ReasoningTrace result={result} />
            </>
          )}
        </div>
      )}

      {/* Empty prompt */}
      {!streaming && !streamedText && !result && !error && (
        <div className="rounded-xl border border-dashed border-[#27272a] p-12 text-center">
          <MessageSquare className="w-10 h-10 text-zinc-700 mx-auto mb-3" />
          <p className="text-sm text-zinc-600">
            Select a workspace and ask a question to begin analysis.
          </p>
        </div>
      )}
    </div>
  );
}
