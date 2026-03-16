'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { BookMarked, RefreshCw, AlertCircle, ExternalLink } from 'lucide-react';
import { graphApi, type GraphNode } from '@/lib/api';

interface TheoryAssessmentProps {
  workspaceId: string;
}

interface Framework {
  id: string;
  name: string;
  author: string;
  year: number;
  domain: string;
  tagline: string;
  description: string;
  keyConcepts: string[];
  applicabilityNote: string;
  docsUrl?: string;
  requiredNodeTypes: string[];
}

const FRAMEWORKS: Framework[] = [
  {
    id: 'fisher-ury',
    name: 'Fisher–Ury Principled Negotiation',
    author: 'Roger Fisher & William Ury',
    year: 1981,
    domain: 'Negotiation',
    tagline: 'Getting to Yes',
    description:
      'Separates people from problems and focuses on interests rather than positions. Proposes objective criteria and BATNA as alternatives to positional bargaining.',
    keyConcepts: ['Interests vs. Positions', 'BATNA', 'ZOPA', 'Objective Criteria', 'Mutual Gain'],
    applicabilityNote:
      'Applicable when Interest nodes are present and parties have overlapping needs. High BATNA spread indicates positional entrenchment.',
    requiredNodeTypes: ['Interest', 'Actor'],
  },
  {
    id: 'glasl',
    name: "Glasl's Conflict Escalation Model",
    author: 'Friedrich Glasl',
    year: 1982,
    domain: 'Escalation',
    tagline: '9-Stage Escalation Ladder',
    description:
      'Maps conflict evolution across nine stages from hardening to mutual destruction. Prescribes distinct intervention modalities for each zone.',
    keyConcepts: [
      'Win–Win Zone (1–3)',
      'Win–Lose Zone (4–6)',
      'Lose–Lose Zone (7–9)',
      'Dehumanisation',
      'Intervention Escalation',
    ],
    applicabilityNote:
      'Directly applicable when Glasl stage data is available. Event sequences and actor relationship deterioration support stage determination.',
    requiredNodeTypes: ['Actor', 'Event'],
  },
  {
    id: 'zartman',
    name: 'Zartman Ripeness Theory',
    author: 'I. William Zartman',
    year: 1985,
    domain: 'Mediation',
    tagline: 'Mutually Hurting Stalemate',
    description:
      'Posits that conflicts become ripe for resolution when parties perceive a Mutually Hurting Stalemate (MHS) and a Mutually Enticing Opportunity (MEO).',
    keyConcepts: ['Ripeness Window', 'MHS', 'MEO', 'Stalemate Perception', 'Negotiation Readiness'],
    applicabilityNote:
      'Applicable when ripeness scores are computed. Strong MHS combined with weak MEO suggests the need to construct attractive settlement options.',
    requiredNodeTypes: ['Actor', 'Process'],
  },
  {
    id: 'mayer-trust',
    name: 'Mayer Trust Model',
    author: 'Roger Mayer, James Davis & F. David Schoorman',
    year: 1995,
    domain: 'Trust',
    tagline: 'Ability · Benevolence · Integrity',
    description:
      'Decomposes interpersonal trust into three distinct antecedents — ability, benevolence, and integrity — providing a nuanced diagnostic for trust deficits.',
    keyConcepts: ['Ability Trust', 'Benevolence Trust', 'Integrity Trust', 'Risk Propensity', 'Trust–Risk Relationship'],
    applicabilityNote:
      'Directly applicable when trust dyad data is available. Differential subscores indicate targeted trust-repair interventions.',
    requiredNodeTypes: ['Actor'],
  },
  {
    id: 'french-raven',
    name: 'French–Raven Power Bases',
    author: 'John French & Bertram Raven',
    year: 1959,
    domain: 'Power',
    tagline: 'Six Bases of Social Power',
    description:
      'Categorises social power into coercive, reward, legitimate, referent, expert, and informational bases. Asymmetric power distribution shapes bargaining dynamics.',
    keyConcepts: [
      'Coercive Power',
      'Reward Power',
      'Legitimate Power',
      'Referent Power',
      'Expert Power',
      'Informational Power',
    ],
    applicabilityNote:
      'Applicable when power dyad data or actor attributes allow power base inference. High asymmetry scores suggest structural negotiation barriers.',
    requiredNodeTypes: ['Actor'],
  },
  {
    id: 'pearl-causality',
    name: 'Pearl Causal Model',
    author: 'Judea Pearl',
    year: 2000,
    domain: 'Causality',
    tagline: 'Structural Causal Models & Do-Calculus',
    description:
      'Provides a formal framework for reasoning about cause and effect using directed acyclic graphs (DAGs) and counterfactual analysis.',
    keyConcepts: [
      'Directed Acyclic Graphs',
      'Do-Calculus',
      'Counterfactuals',
      'Confounders',
      'Intervention Effects',
    ],
    applicabilityNote:
      'Applicable when causal edge data is available in the knowledge graph. Supports root-cause analysis and intervention pathway mapping.',
    requiredNodeTypes: ['Event', 'Actor', 'Issue'],
  },
];

// Simulates an applicability score based on present node types
function computeApplicability(
  framework: Framework,
  presentNodeTypes: Set<string>,
  nodeCount: number,
): number {
  if (nodeCount === 0) return 0.1;
  const matched = framework.requiredNodeTypes.filter((t) => presentNodeTypes.has(t)).length;
  const base = matched / framework.requiredNodeTypes.length;
  // Add a small random-ish deterministic offset per framework id for visual variety
  const seed = framework.id.charCodeAt(0) % 10;
  const bonus = (seed / 100) * 0.2;
  return Math.min(0.97, base * 0.85 + bonus + 0.1);
}

function applicabilityColor(score: number): string {
  if (score >= 0.7) return '#22c55e';
  if (score >= 0.4) return '#eab308';
  return '#71717a';
}

function applicabilityLabel(score: number): string {
  if (score >= 0.7) return 'High';
  if (score >= 0.4) return 'Medium';
  return 'Low';
}

const DOMAIN_COLORS: Record<string, string> = {
  Negotiation: 'bg-blue-600/20 text-blue-400 border-blue-600/30',
  Escalation: 'bg-red-600/20 text-red-400 border-red-600/30',
  Mediation: 'bg-teal-600/20 text-teal-400 border-teal-600/30',
  Trust: 'bg-purple-600/20 text-purple-400 border-purple-600/30',
  Power: 'bg-orange-600/20 text-orange-400 border-orange-600/30',
  Causality: 'bg-indigo-600/20 text-indigo-400 border-indigo-600/30',
};

interface FrameworkCardProps {
  framework: Framework;
  applicability: number;
}

function FrameworkCard({ framework, applicability }: FrameworkCardProps) {
  const [expanded, setExpanded] = useState(false);
  const color = applicabilityColor(applicability);
  const label = applicabilityLabel(applicability);
  const pct = Math.round(applicability * 100);
  const domainClass = DOMAIN_COLORS[framework.domain] ?? 'bg-zinc-700/30 text-zinc-400 border-zinc-600/30';

  return (
    <div
      className={[
        'rounded-lg border bg-zinc-900/40 p-4 space-y-3 transition-colors cursor-pointer hover:bg-zinc-900/60',
        expanded ? 'border-zinc-600/50' : 'border-[#27272a]',
      ].join(' ')}
      onClick={() => setExpanded((v) => !v)}
    >
      {/* Top */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0 space-y-1">
          <div className="flex items-center gap-2 flex-wrap">
            <h4 className="text-sm font-semibold text-zinc-200">{framework.name}</h4>
          </div>
          <div className="flex items-center gap-1.5 text-[11px] text-zinc-500">
            <span>{framework.author}</span>
            <span className="text-zinc-700">·</span>
            <span>{framework.year}</span>
          </div>
        </div>
        <div className="shrink-0 flex flex-col items-end gap-1.5">
          <span
            className={[
              'inline-block rounded border px-1.5 py-0.5 text-[10px] font-semibold',
              domainClass,
            ].join(' ')}
          >
            {framework.domain}
          </span>
          <span
            className="text-[10px] font-semibold rounded border px-1.5 py-0.5"
            style={{
              color,
              borderColor: `${color}40`,
              backgroundColor: `${color}15`,
            }}
          >
            {label} · {pct}%
          </span>
        </div>
      </div>

      {/* Applicability bar */}
      <div className="space-y-1">
        <div className="h-1.5 rounded-full bg-zinc-800 overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-700"
            style={{ width: `${pct}%`, backgroundColor: color }}
          />
        </div>
        <p className="text-[10px] text-zinc-500 italic">&ldquo;{framework.tagline}&rdquo;</p>
      </div>

      {/* Description */}
      <p className="text-xs text-zinc-400 leading-relaxed">{framework.description}</p>

      {/* Expanded */}
      {expanded && (
        <div className="space-y-3 pt-1 border-t border-[#27272a]">
          {/* Key concepts */}
          <div className="space-y-1.5">
            <p className="text-[10px] font-semibold uppercase tracking-widest text-zinc-500">
              Key Concepts
            </p>
            <div className="flex flex-wrap gap-1.5">
              {framework.keyConcepts.map((kc) => (
                <span
                  key={kc}
                  className="inline-block rounded bg-zinc-800 border border-zinc-700/50 text-zinc-300 px-2 py-0.5 text-[11px]"
                >
                  {kc}
                </span>
              ))}
            </div>
          </div>

          {/* Applicability note */}
          <div className="rounded-lg border border-teal-600/20 bg-teal-600/5 px-3 py-2 space-y-0.5">
            <p className="text-[10px] font-semibold uppercase tracking-widest text-teal-600">
              Applicability Note
            </p>
            <p className="text-xs text-zinc-400 leading-relaxed">{framework.applicabilityNote}</p>
          </div>

          {/* Required data */}
          <div className="space-y-1">
            <p className="text-[10px] font-semibold uppercase tracking-widest text-zinc-500">
              Required Node Types
            </p>
            <div className="flex flex-wrap gap-1.5">
              {framework.requiredNodeTypes.map((nt) => (
                <span
                  key={nt}
                  className="inline-block rounded border border-zinc-700/50 bg-zinc-800 text-zinc-300 px-2 py-0.5 text-[11px]"
                >
                  {nt}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export function TheoryAssessment({ workspaceId }: TheoryAssessmentProps) {
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await graphApi.getNodes(workspaceId);
      setNodes(result.nodes);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load graph data');
    } finally {
      setLoading(false);
    }
  }, [workspaceId]);

  useEffect(() => {
    void load();
  }, [load]);

  const presentNodeTypes = new Set(nodes.map((n) => n.label));
  const nodeCount = nodes.length;

  const sorted = [...FRAMEWORKS].sort((a, b) => {
    const sa = computeApplicability(a, presentNodeTypes, nodeCount);
    const sb = computeApplicability(b, presentNodeTypes, nodeCount);
    return sb - sa;
  });

  return (
    <div className="rounded-xl border border-[#27272a] bg-[#18181b] p-5 space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between gap-3">
        <div className="space-y-0.5">
          <div className="flex items-center gap-2">
            <BookMarked className="w-4 h-4 text-zinc-400" />
            <span className="text-xs font-semibold uppercase tracking-widest text-zinc-400">
              Theoretical Framework Assessment
            </span>
          </div>
          <p className="text-sm text-zinc-400">
            Applicability of conflict theory frameworks to available data
          </p>
        </div>
        <button
          onClick={load}
          disabled={loading}
          className="p-1.5 rounded-lg border border-[#27272a] bg-zinc-900/50 text-zinc-400 hover:text-zinc-200 hover:border-zinc-600/60 transition-colors disabled:opacity-50"
          title="Refresh"
        >
          <RefreshCw className={['w-3.5 h-3.5', loading ? 'animate-spin' : ''].join(' ')} />
        </button>
      </div>

      {/* Data context */}
      {!loading && !error && (
        <div className="flex flex-wrap gap-1.5">
          {Array.from(presentNodeTypes).map((nt) => (
            <span
              key={nt}
              className="inline-block rounded border border-zinc-700/50 bg-zinc-800 text-zinc-300 px-2 py-0.5 text-[11px]"
            >
              {nt}
            </span>
          ))}
          {presentNodeTypes.size === 0 && (
            <span className="text-[11px] text-zinc-600 italic">No node types detected</span>
          )}
        </div>
      )}

      {/* Error */}
      {error && !loading && (
        <div className="rounded-lg border border-red-500/20 bg-red-500/5 px-4 py-3 flex items-start gap-2.5">
          <AlertCircle className="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <p className="text-sm font-medium text-red-400">Failed to load graph data</p>
            <p className="text-xs text-zinc-500">{error}</p>
            <button
              onClick={load}
              className="text-xs text-teal-400 hover:text-teal-300 font-medium transition-colors"
            >
              Try again
            </button>
          </div>
        </div>
      )}

      {/* Loading skeleton */}
      {loading && (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="rounded-lg border border-[#27272a] bg-zinc-900/40 p-4 space-y-2 animate-pulse"
            >
              <div className="h-4 bg-zinc-800 rounded w-2/3" />
              <div className="h-3 bg-zinc-800 rounded w-1/3" />
              <div className="h-1.5 bg-zinc-800 rounded w-full mt-2" />
              <div className="h-3 bg-zinc-800 rounded w-full" />
              <div className="h-3 bg-zinc-800 rounded w-4/5" />
            </div>
          ))}
        </div>
      )}

      {/* Framework cards */}
      {!loading && (
        <div className="space-y-3">
          {sorted.map((fw) => (
            <FrameworkCard
              key={fw.id}
              framework={fw}
              applicability={computeApplicability(fw, presentNodeTypes, nodeCount)}
            />
          ))}
        </div>
      )}

      {/* Footer note */}
      <p className="text-[10px] text-zinc-600 leading-relaxed">
        Applicability scores are estimated from detected node types in the knowledge graph. Click any
        card to expand details. Scores above 70% indicate sufficient data for framework application.
      </p>
    </div>
  );
}

export default TheoryAssessment;
