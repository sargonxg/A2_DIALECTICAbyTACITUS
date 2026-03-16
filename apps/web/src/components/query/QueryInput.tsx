'use client';

import React, { useState, useRef, useCallback } from 'react';
import { Send, ChevronDown, Loader2 } from 'lucide-react';

const MODES = [
  { id: 'general',    label: 'General',    description: 'Open-ended conflict analysis' },
  { id: 'escalation', label: 'Escalation', description: 'Glasl stage & trajectory' },
  { id: 'ripeness',   label: 'Ripeness',   description: 'MHS/MEO resolution readiness' },
  { id: 'power',      label: 'Power',      description: 'Actor power dynamics' },
  { id: 'trust',      label: 'Trust',      description: 'Inter-actor trust assessment' },
];

const EXAMPLE_QUERIES: Record<string, string[]> = {
  general: [
    'What are the core drivers of this conflict?',
    'Who are the key actors and what are their positions?',
    'What narratives are shaping the conflict?',
  ],
  escalation: [
    'What Glasl stage is this conflict at?',
    'What signals indicate escalation risk?',
    'How has the conflict trajectory changed recently?',
  ],
  ripeness: [
    'Is there a mutually hurting stalemate?',
    'What conditions must be met for negotiations?',
    'How close is the conflict to ripeness?',
  ],
  power: [
    'Who holds the most structural power?',
    'What power asymmetries exist?',
    'Which actors are most dependent on others?',
  ],
  trust: [
    'What is the trust level between the main parties?',
    'What events have damaged trust recently?',
    'Which actors are trust brokers?',
  ],
};

interface QueryInputProps {
  onSubmit: (query: string, mode: string) => void;
  loading: boolean;
}

export function QueryInput({ onSubmit, loading }: QueryInputProps) {
  const [query, setQuery] = useState('');
  const [mode, setMode] = useState('general');
  const [modeOpen, setModeOpen] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const selectedMode = MODES.find((m) => m.id === mode) ?? MODES[0];

  const handleSubmit = useCallback(
    (e?: React.FormEvent) => {
      e?.preventDefault();
      const q = query.trim();
      if (!q || loading) return;
      onSubmit(q, mode);
    },
    [query, mode, loading, onSubmit],
  );

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleExampleClick = (example: string) => {
    setQuery(example);
    textareaRef.current?.focus();
  };

  const examples = EXAMPLE_QUERIES[mode] ?? EXAMPLE_QUERIES.general;

  return (
    <div className="space-y-3">
      <form onSubmit={handleSubmit}>
        <div
          className="overflow-hidden rounded-xl border border-[#27272a] bg-[#18181b] transition-all
                     focus-within:border-teal-600/60 focus-within:ring-1 focus-within:ring-teal-600/20"
        >
          {/* Textarea */}
          <textarea
            ref={textareaRef}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
            placeholder="Ask a question about this conflict…"
            rows={4}
            className="w-full resize-none bg-transparent px-4 pt-4 pb-2 text-sm text-zinc-100
                       placeholder:text-zinc-600 focus:outline-none disabled:opacity-50"
          />

          {/* Toolbar */}
          <div className="flex items-center gap-2 border-t border-[#27272a] px-3 py-2">
            {/* Mode selector */}
            <div ref={dropdownRef} className="relative">
              <button
                type="button"
                onClick={() => setModeOpen((v) => !v)}
                disabled={loading}
                className="flex items-center gap-1.5 rounded-md border border-[#27272a] bg-[#09090b]
                           px-2.5 py-1.5 text-xs font-medium text-zinc-300 transition-colors
                           hover:border-zinc-600 hover:text-white disabled:opacity-50"
              >
                <span
                  className="h-1.5 w-1.5 rounded-full bg-teal-500"
                />
                {selectedMode.label}
                <ChevronDown className="h-3 w-3 text-zinc-500" />
              </button>

              {modeOpen && (
                <div
                  className="absolute bottom-full left-0 mb-1.5 z-50 w-56 rounded-xl border
                             border-[#27272a] bg-[#18181b] shadow-2xl overflow-hidden"
                >
                  {MODES.map((m) => (
                    <button
                      key={m.id}
                      type="button"
                      onClick={() => {
                        setMode(m.id);
                        setModeOpen(false);
                      }}
                      className={[
                        'w-full text-left px-3 py-2.5 transition-colors',
                        m.id === mode
                          ? 'bg-teal-600/15 text-teal-300'
                          : 'text-zinc-300 hover:bg-white/5',
                      ].join(' ')}
                    >
                      <p className="text-xs font-semibold">{m.label}</p>
                      <p className="text-[11px] text-zinc-500 mt-0.5">{m.description}</p>
                    </button>
                  ))}
                </div>
              )}
            </div>

            <span className="text-[10px] text-zinc-600 hidden sm:block">
              Ctrl+Enter to submit
            </span>

            <div className="ml-auto">
              <button
                type="submit"
                disabled={loading || !query.trim()}
                className="flex items-center gap-1.5 rounded-lg bg-teal-600 px-3 py-1.5
                           text-xs font-semibold text-white transition-all
                           hover:bg-teal-500 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-3.5 w-3.5 animate-spin" />
                    Analyzing…
                  </>
                ) : (
                  <>
                    <Send className="h-3.5 w-3.5" />
                    Analyze
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </form>

      {/* Example queries */}
      <div className="flex flex-wrap gap-1.5">
        <span className="text-[10px] text-zinc-600 self-center mr-1 uppercase tracking-widest">
          Try:
        </span>
        {examples.map((ex) => (
          <button
            key={ex}
            type="button"
            onClick={() => handleExampleClick(ex)}
            disabled={loading}
            className="rounded-full border border-[#27272a] bg-[#18181b] px-2.5 py-1
                       text-[11px] text-zinc-400 transition-colors hover:border-zinc-600
                       hover:text-zinc-200 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {ex}
          </button>
        ))}
      </div>
    </div>
  );
}

export default QueryInput;