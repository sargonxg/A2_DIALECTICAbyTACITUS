'use client';

import React from 'react';
import {
  FileText,
  Braces,
  ScanLine,
  GitMerge,
  CheckCircle2,
  Loader2,
  AlertCircle,
} from 'lucide-react';

type ExtractionStatus = 'idle' | 'extracting' | 'complete' | 'error';

interface EntityCounts {
  actors: number;
  events: number;
  issues: number;
}

interface ExtractionProgressProps {
  jobId?: string;
  status: ExtractionStatus;
  progress?: number;
  entityCounts?: EntityCounts;
}

const PIPELINE_STEPS = [
  {
    id: 'document',
    label: 'Document Parsing',
    description: 'Reading and segmenting text',
    icon: FileText,
    activeAt: ['extracting', 'complete'],
    doneAt: ['complete'],
  },
  {
    id: 'nlp',
    label: 'NLP Processing',
    description: 'Tokenisation and dependency parsing',
    icon: Braces,
    activeAt: ['extracting', 'complete'],
    doneAt: ['complete'],
  },
  {
    id: 'entities',
    label: 'Entity Recognition',
    description: 'Detecting actors, events, issues',
    icon: ScanLine,
    activeAt: ['extracting', 'complete'],
    doneAt: ['complete'],
  },
  {
    id: 'graph',
    label: 'Graph Writing',
    description: 'Persisting nodes and edges',
    icon: GitMerge,
    activeAt: ['complete'],
    doneAt: ['complete'],
  },
  {
    id: 'complete',
    label: 'Complete',
    description: 'Extraction pipeline finished',
    icon: CheckCircle2,
    activeAt: ['complete'],
    doneAt: ['complete'],
  },
];

function stepState(
  step: (typeof PIPELINE_STEPS)[0],
  status: ExtractionStatus,
  progress: number,
  stepIdx: number,
  totalSteps: number,
): 'idle' | 'active' | 'done' | 'error' {
  if (status === 'error') return stepIdx === 0 ? 'error' : 'idle';
  if (status === 'idle') return 'idle';
  if (status === 'complete') return 'done';

  // Extracting: use progress to determine active step
  const stepThreshold = ((stepIdx + 1) / totalSteps) * 100;
  const prevThreshold = (stepIdx / totalSteps) * 100;
  if (progress >= stepThreshold) return 'done';
  if (progress >= prevThreshold) return 'active';
  return 'idle';
}

export function ExtractionProgress({
  jobId,
  status,
  progress = 0,
  entityCounts,
}: ExtractionProgressProps) {
  return (
    <div className="rounded-xl border border-[#27272a] bg-[#18181b] overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-[#27272a] px-4 py-2.5">
        <div className="flex items-center gap-2">
          {status === 'extracting' && (
            <Loader2 className="h-3.5 w-3.5 text-teal-500 animate-spin" />
          )}
          {status === 'complete' && (
            <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
          )}
          {status === 'error' && (
            <AlertCircle className="h-3.5 w-3.5 text-red-500" />
          )}
          {status === 'idle' && (
            <div className="h-3.5 w-3.5 rounded-full border border-zinc-700" />
          )}
          <span className="text-xs font-semibold text-zinc-300">
            {status === 'idle' && 'Extraction Pipeline'}
            {status === 'extracting' && 'Extracting…'}
            {status === 'complete' && 'Extraction Complete'}
            {status === 'error' && 'Extraction Failed'}
          </span>
        </div>
        {jobId && (
          <span className="font-mono text-[10px] text-zinc-600">
            job:{jobId.slice(0, 8)}
          </span>
        )}
      </div>

      <div className="p-4 space-y-4">
        {/* Progress bar (visible while extracting) */}
        {status === 'extracting' && (
          <div className="space-y-1.5">
            <div className="h-1.5 w-full rounded-full bg-zinc-800 overflow-hidden">
              <div
                className="h-full rounded-full bg-teal-500 transition-all duration-500"
                style={{ width: `${progress}%` }}
              />
            </div>
            <div className="flex justify-between">
              <span className="text-[10px] text-zinc-600">Processing…</span>
              <span className="text-[10px] text-zinc-500 tabular-nums">{progress}%</span>
            </div>
          </div>
        )}

        {/* Pipeline steps */}
        <div className="space-y-1">
          {PIPELINE_STEPS.map((step, i) => {
            const state = stepState(step, status, progress, i, PIPELINE_STEPS.length);
            const Icon = step.icon;
            const isActive = state === 'active';
            const isDone = state === 'done';
            const isError = state === 'error';

            let iconColor = '#52525b';
            let textColor = 'text-zinc-600';
            let bg = 'bg-transparent';
            let borderColor = 'border-transparent';

            if (isActive) {
              iconColor = '#0d9488';
              textColor = 'text-zinc-200';
              bg = 'bg-teal-950/30';
              borderColor = 'border-teal-800/40';
            } else if (isDone) {
              iconColor = '#22c55e';
              textColor = 'text-zinc-300';
            } else if (isError) {
              iconColor = '#ef4444';
              textColor = 'text-red-400';
            }

            return (
              <div
                key={step.id}
                className={[
                  'flex items-center gap-3 rounded-lg border px-3 py-2 transition-all duration-300',
                  bg,
                  borderColor,
                ].join(' ')}
              >
                <div
                  className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-md"
                  style={{ backgroundColor: `${iconColor}18` }}
                >
                  {isActive ? (
                    <Loader2 className="h-3.5 w-3.5 animate-spin" style={{ color: iconColor }} />
                  ) : (
                    <Icon className="h-3.5 w-3.5" style={{ color: iconColor }} />
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <p className={`text-xs font-medium ${textColor} leading-tight`}>
                    {step.label}
                  </p>
                  <p className="text-[10px] text-zinc-600 mt-0.5">{step.description}</p>
                </div>
                {isDone && !isActive && (
                  <CheckCircle2 className="h-3.5 w-3.5 flex-shrink-0 text-emerald-500" />
                )}
              </div>
            );
          })}
        </div>

        {/* Entity count summary */}
        {status === 'complete' && entityCounts && (
          <div className="rounded-lg border border-emerald-900/30 bg-emerald-950/20 p-3">
            <p className="text-[10px] font-semibold uppercase tracking-widest text-emerald-600 mb-2">
              Extracted Entities
            </p>
            <div className="grid grid-cols-3 gap-2">
              <div className="text-center">
                <p className="text-xl font-bold text-emerald-400 tabular-nums">
                  {entityCounts.actors}
                </p>
                <p className="text-[10px] text-zinc-500">Actors</p>
              </div>
              <div className="text-center">
                <p className="text-xl font-bold text-emerald-400 tabular-nums">
                  {entityCounts.events}
                </p>
                <p className="text-[10px] text-zinc-500">Events</p>
              </div>
              <div className="text-center">
                <p className="text-xl font-bold text-emerald-400 tabular-nums">
                  {entityCounts.issues}
                </p>
                <p className="text-[10px] text-zinc-500">Issues</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default ExtractionProgress;