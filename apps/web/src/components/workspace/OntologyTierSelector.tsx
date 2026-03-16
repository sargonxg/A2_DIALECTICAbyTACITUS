'use client';

import React from 'react';
import { CheckCircle2, Users, Layers, Database } from 'lucide-react';

interface Tier {
  id: string;
  label: string;
  tagline: string;
  description: string;
  nodeTypes: string[];
  icon: React.ElementType;
  accentColor: string;
  accentBg: string;
  borderColor: string;
  selectedBorder: string;
}

const TIERS: Tier[] = [
  {
    id: 'essential',
    label: 'Essential',
    tagline: 'Core conflict entities',
    description:
      'The minimum viable ontology. Captures the fundamental who, what, and when of any conflict.',
    nodeTypes: ['Actor', 'Conflict', 'Event'],
    icon: Users,
    accentColor: '#22c55e',
    accentBg: 'bg-emerald-950/20',
    borderColor: 'border-[#27272a]',
    selectedBorder: 'border-emerald-700/60',
  },
  {
    id: 'standard',
    label: 'Standard',
    tagline: 'Recommended for most analyses',
    description:
      'Adds issue framing, actor interests, and process tracking for richer analytical depth.',
    nodeTypes: ['Actor', 'Conflict', 'Event', 'Issue', 'Interest', 'Process'],
    icon: Layers,
    accentColor: '#eab308',
    accentBg: 'bg-yellow-950/20',
    borderColor: 'border-[#27272a]',
    selectedBorder: 'border-yellow-700/60',
  },
  {
    id: 'full',
    label: 'Full',
    tagline: 'Complete 15-type ontology',
    description:
      'All node types including narratives, trust states, and power dynamics for deep systemic analysis.',
    nodeTypes: [
      'Actor', 'Conflict', 'Event', 'Issue', 'Interest',
      'Process', 'Narrative', 'Trust State', 'Power Dynamic',
      '+ 6 more',
    ],
    icon: Database,
    accentColor: '#0d9488',
    accentBg: 'bg-teal-950/20',
    borderColor: 'border-[#27272a]',
    selectedBorder: 'border-teal-700/60',
  },
];

interface OntologyTierSelectorProps {
  currentTier: string;
  onTierChange: (tier: string) => void;
}

export function OntologyTierSelector({
  currentTier,
  onTierChange,
}: OntologyTierSelectorProps) {
  return (
    <div className="space-y-3">
      <div className="flex flex-col gap-2.5">
        {TIERS.map((tier) => {
          const isSelected = currentTier === tier.id;
          const Icon = tier.icon;

          return (
            <button
              key={tier.id}
              type="button"
              onClick={() => onTierChange(tier.id)}
              className={[
                'relative w-full rounded-xl border p-4 text-left transition-all duration-200',
                'focus:outline-none focus:ring-2 focus:ring-teal-600/30',
                isSelected
                  ? `${tier.accentBg} ${tier.selectedBorder}`
                  : `bg-[#18181b] ${tier.borderColor} hover:border-zinc-600 hover:bg-white/[0.02]`,
              ].join(' ')}
            >
              <div className="flex items-start gap-3">
                {/* Icon */}
                <div
                  className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-lg"
                  style={{ backgroundColor: `${tier.accentColor}18`, border: `1px solid ${tier.accentColor}30` }}
                >
                  <Icon className="h-4 w-4" style={{ color: tier.accentColor }} />
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span
                      className="text-sm font-semibold"
                      style={{ color: isSelected ? tier.accentColor : '#e4e4e7' }}
                    >
                      {tier.label}
                    </span>
                    <span
                      className="rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider"
                      style={{
                        backgroundColor: `${tier.accentColor}18`,
                        color: tier.accentColor,
                        border: `1px solid ${tier.accentColor}30`,
                      }}
                    >
                      {tier.nodeTypes.filter((t) => !t.startsWith('+')).length} types
                    </span>
                  </div>

                  <p className="text-[11px] text-zinc-500 mt-0.5">{tier.tagline}</p>

                  <p className="text-xs text-zinc-500 mt-1.5 leading-relaxed">
                    {tier.description}
                  </p>

                  {/* Node type chips */}
                  <div className="mt-2.5 flex flex-wrap gap-1">
                    {tier.nodeTypes.map((nt) => (
                      <span
                        key={nt}
                        className={[
                          'rounded-full px-2 py-0.5 text-[10px] font-medium',
                          nt.startsWith('+')
                            ? 'text-zinc-600 bg-zinc-800/50'
                            : '',
                        ].join(' ')}
                        style={
                          !nt.startsWith('+')
                            ? {
                                backgroundColor: `${tier.accentColor}12`,
                                color: `${tier.accentColor}cc`,
                                border: `1px solid ${tier.accentColor}25`,
                              }
                            : undefined
                        }
                      >
                        {nt}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Selected check */}
                <div className="flex-shrink-0 mt-0.5">
                  {isSelected ? (
                    <CheckCircle2
                      className="h-4.5 w-4.5"
                      style={{ color: tier.accentColor }}
                    />
                  ) : (
                    <div className="h-4.5 w-4.5 rounded-full border border-zinc-700" />
                  )}
                </div>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}

export default OntologyTierSelector;