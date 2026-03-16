"use client";

import { cn } from "@/lib/utils";
import type { OntologyTier } from "@/types/ontology";
import { Check } from "lucide-react";

const TIERS: { value: OntologyTier; label: string; nodes: number; edges: number; desc: string }[] = [
  { value: "essential", label: "Essential", nodes: 7, edges: 6, desc: "Quick conflict mapping with core types" },
  { value: "standard", label: "Standard", nodes: 12, edges: 13, desc: "Structured analysis with narratives and norms" },
  { value: "full", label: "Full", nodes: 15, edges: 20, desc: "Complete neurosymbolic intelligence layer" },
];

export default function OntologyTierSelector({ value, onChange }: { value: OntologyTier; onChange: (t: OntologyTier) => void }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {TIERS.map((tier) => (
        <button key={tier.value} onClick={() => onChange(tier.value)} className={cn("card text-left transition-all", value === tier.value ? "border-accent bg-accent/5 ring-1 ring-accent" : "hover:border-border-hover")}>
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-semibold text-text-primary">{tier.label}</h3>
            {value === tier.value && <Check size={16} className="text-accent" />}
          </div>
          <p className="text-sm text-text-secondary mb-3">{tier.desc}</p>
          <div className="flex gap-3 text-xs font-mono text-text-secondary">
            <span>{tier.nodes} node types</span>
            <span>{tier.edges} edge types</span>
          </div>
        </button>
      ))}
    </div>
  );
}
