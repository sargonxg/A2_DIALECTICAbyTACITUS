'use client';

import React from 'react';
import { GitBranch, Info } from 'lucide-react';

interface KriesbergPhaseTrackerProps {
  phase: string;
}

interface Phase {
  id: string;
  label: string;
  shortLabel: string;
  interventionOpportunity: string;
  description: string;
}

const PHASES: Phase[] = [
  {
    id: 'latent',
    label: 'Latent',
    shortLabel: 'Latent',
    description: 'Underlying tensions exist but have not yet surfaced into open conflict',
    interventionOpportunity:
      'Preventive diplomacy, early warning systems, structural reforms, and confidence-building measures are most effective at this stage.',
  },
  {
    id: 'emerging',
    label: 'Emerging',
    shortLabel: 'Emerging',
    description: 'Issues begin to crystallise; parties identify interests in opposition',
    interventionOpportunity:
      'Track II diplomacy, dialogue facilitation, and joint fact-finding can prevent escalation. Entry costs are low.',
  },
  {
    id: 'escalating',
    label: 'Escalating',
    shortLabel: 'Escalating',
    description: 'Conflict intensifies; coercive tactics employed; positions harden',
    interventionOpportunity:
      'Crisis mediation and cease-fire negotiations are critical. Ripeness assessment should inform intervention timing.',
  },
  {
    id: 'stalemate',
    label: 'Stalemate',
    shortLabel: 'Stalemate',
    description: 'Neither party can win; mutually hurting stalemate may ripen for resolution',
    interventionOpportunity:
      'Highest ripeness window. Third-party mediators, back-channel talks, and creative formula-building can unlock impasse.',
  },
  {
    id: 'de-escalating',
    label: 'De-escalating',
    shortLabel: 'De-escalating',
    description: 'Tension and hostility diminish; negotiations or ceasefires begin',
    interventionOpportunity:
      'Sustain momentum with confidence-building measures, partial agreements, and public commitment mechanisms.',
  },
  {
    id: 'terminating',
    label: 'Terminating',
    shortLabel: 'Terminating',
    description: 'Conflict ends through agreement, exhaustion, or one-sided victory',
    interventionOpportunity:
      'Ensure settlement sustainability: address root causes, design verification mechanisms, and support spoiler management.',
  },
  {
    id: 'post-conflict',
    label: 'Post-conflict',
    shortLabel: 'Post-conflict',
    description: 'Active hostilities have ceased; peacebuilding and reconciliation begin',
    interventionOpportunity:
      'Long-term peacebuilding: transitional justice, reconciliation processes, institutional reform, and economic recovery.',
  },
];

function normalise(s: string): string {
  return s.toLowerCase().trim().replace(/\s+/g, '-');
}

export function KriesbergPhaseTracker({ phase }: KriesbergPhaseTrackerProps) {
  const normPhase = normalise(phase);
  const activeIdx = PHASES.findIndex((p) => normalise(p.id) === normPhase || normalise(p.label) === normPhase);
  const currentPhase = activeIdx >= 0 ? PHASES[activeIdx] : null;

  return (
    <div className="rounded-xl border border-[#27272a] bg-[#18181b] p-5 space-y-5">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-0.5">
          <div className="flex items-center gap-2">
            <GitBranch className="w-4 h-4 text-zinc-400" />
            <span className="text-xs font-semibold uppercase tracking-widest text-zinc-400">
              Kriesberg Conflict Phase
            </span>
          </div>
          <h3 className="text-lg font-semibold text-white">
            {currentPhase ? currentPhase.label : phase}
          </h3>
          {currentPhase && (
            <p className="text-sm text-zinc-400 max-w-sm">{currentPhase.description}</p>
          )}
        </div>
        {/* Phase badge */}
        {currentPhase && (
          <div className="shrink-0 rounded-lg border border-teal-600/40 bg-teal-600/15 px-3 py-1.5">
            <p className="text-[10px] uppercase tracking-widest text-teal-600 font-medium">Active Phase</p>
            <p className="text-sm font-bold text-teal-400">{currentPhase.label}</p>
          </div>
        )}
      </div>

      {/* Phase track — desktop: horizontal, mobile: vertical */}
      <div className="hidden sm:block">
        <div className="relative">
          {/* Connector line */}
          <div className="absolute top-5 left-0 right-0 h-px bg-[#27272a]" />
          {/* Progress line */}
          {activeIdx >= 0 && (
            <div
              className="absolute top-5 left-0 h-px bg-teal-600 transition-all duration-700"
              style={{
                width: `${((activeIdx + 0.5) / PHASES.length) * 100}%`,
              }}
            />
          )}
          <div className="relative flex justify-between">
            {PHASES.map((p, i) => {
              const isActive = i === activeIdx;
              const isPast = activeIdx >= 0 && i < activeIdx;
              const isFuture = activeIdx >= 0 && i > activeIdx;

              return (
                <div
                  key={p.id}
                  className="flex flex-col items-center"
                  style={{ width: `${100 / PHASES.length}%` }}
                >
                  {/* Dot */}
                  <div
                    className={[
                      'w-10 h-10 rounded-full flex items-center justify-center border-2 transition-all duration-300 z-10 relative',
                      isActive
                        ? 'border-teal-500 bg-teal-600 shadow-lg shadow-teal-900/40'
                        : isPast
                        ? 'border-teal-700 bg-teal-900/40'
                        : 'border-[#27272a] bg-[#18181b]',
                    ].join(' ')}
                  >
                    <span
                      className={[
                        'text-[11px] font-bold',
                        isActive ? 'text-white' : isPast ? 'text-teal-500' : 'text-zinc-600',
                      ].join(' ')}
                    >
                      {i + 1}
                    </span>
                  </div>
                  {/* Label */}
                  <span
                    className={[
                      'mt-2 text-[10px] font-medium text-center leading-tight px-0.5',
                      isActive
                        ? 'text-teal-400'
                        : isPast
                        ? 'text-zinc-500'
                        : isFuture
                        ? 'text-zinc-700'
                        : 'text-zinc-500',
                    ].join(' ')}
                  >
                    {p.shortLabel}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Mobile: vertical phases list */}
      <div className="sm:hidden space-y-1">
        {PHASES.map((p, i) => {
          const isActive = i === activeIdx;
          const isPast = activeIdx >= 0 && i < activeIdx;
          return (
            <div
              key={p.id}
              className={[
                'flex items-center gap-3 rounded-lg px-3 py-2',
                isActive ? 'bg-teal-600/15 border border-teal-600/40' : 'border border-transparent',
              ].join(' ')}
            >
              <div
                className={[
                  'w-6 h-6 rounded-full flex items-center justify-center border text-[10px] font-bold shrink-0',
                  isActive
                    ? 'border-teal-500 bg-teal-600 text-white'
                    : isPast
                    ? 'border-teal-700 bg-teal-900/30 text-teal-500'
                    : 'border-[#27272a] bg-transparent text-zinc-600',
                ].join(' ')}
              >
                {i + 1}
              </div>
              <span
                className={[
                  'text-xs font-medium',
                  isActive ? 'text-teal-400' : isPast ? 'text-zinc-500' : 'text-zinc-700',
                ].join(' ')}
              >
                {p.label}
              </span>
            </div>
          );
        })}
      </div>

      {/* Intervention opportunity */}
      {currentPhase && (
        <div className="rounded-lg border border-teal-600/20 bg-teal-600/5 px-4 py-3 space-y-1">
          <div className="flex items-center gap-1.5">
            <Info className="w-3.5 h-3.5 text-teal-500 shrink-0" />
            <p className="text-[10px] font-semibold uppercase tracking-widest text-teal-600">
              Intervention Opportunity
            </p>
          </div>
          <p className="text-sm text-zinc-300 leading-relaxed">
            {currentPhase.interventionOpportunity}
          </p>
        </div>
      )}

      {/* Unknown phase fallback */}
      {!currentPhase && (
        <div className="rounded-lg border border-zinc-700/50 bg-zinc-900/30 px-4 py-3">
          <p className="text-sm text-zinc-500">
            Phase <span className="text-zinc-300 font-medium">&ldquo;{phase}&rdquo;</span> does not
            map to a recognised Kriesberg phase. Verify the phase identifier.
          </p>
        </div>
      )}

      {/* Phase list reference (collapsed) */}
      <details className="group">
        <summary className="cursor-pointer list-none flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-widest text-zinc-600 hover:text-zinc-400 transition-colors select-none">
          <span className="group-open:rotate-90 transition-transform inline-block">▶</span>
          All Phases Reference
        </summary>
        <div className="mt-3 space-y-2">
          {PHASES.map((p, i) => {
            const isActive = i === activeIdx;
            return (
              <div
                key={p.id}
                className={[
                  'rounded-lg border px-3 py-2.5 space-y-1',
                  isActive
                    ? 'border-teal-600/40 bg-teal-600/10'
                    : 'border-[#27272a] bg-zinc-900/20',
                ].join(' ')}
              >
                <div className="flex items-center gap-2">
                  <span
                    className={[
                      'text-xs font-semibold',
                      isActive ? 'text-teal-400' : 'text-zinc-300',
                    ].join(' ')}
                  >
                    {i + 1}. {p.label}
                  </span>
                  {isActive && (
                    <span className="text-[10px] bg-teal-600/20 text-teal-400 border border-teal-600/30 rounded px-1.5 py-0.5 font-medium">
                      Current
                    </span>
                  )}
                </div>
                <p className="text-[11px] text-zinc-500">{p.description}</p>
              </div>
            );
          })}
        </div>
      </details>
    </div>
  );
}

export default KriesbergPhaseTracker;
