"use client";

import { NODE_COLORS } from "@/lib/utils";
import { Layers } from "lucide-react";

const NODE_TYPES = [
  { type: "actor", tier: "essential", desc: "Entity capable of agency" },
  { type: "conflict", tier: "essential", desc: "Root conflict container" },
  { type: "event", tier: "essential", desc: "Discrete occurrence" },
  { type: "issue", tier: "essential", desc: "Point of contention" },
  { type: "process", tier: "essential", desc: "Resolution process" },
  { type: "outcome", tier: "essential", desc: "Process result" },
  { type: "location", tier: "essential", desc: "Geographic context" },
  { type: "interest", tier: "standard", desc: "Underlying need/want" },
  { type: "norm", tier: "standard", desc: "Rule or agreement" },
  { type: "narrative", tier: "standard", desc: "Interpretive frame" },
  { type: "evidence", tier: "standard", desc: "Supporting source" },
  { type: "role", tier: "standard", desc: "Actor function in process" },
  { type: "emotional_state", tier: "full", desc: "Affective state" },
  { type: "trust_state", tier: "full", desc: "Trust assessment" },
  { type: "power_dynamic", tier: "full", desc: "Power relationship" },
];

export default function OntologyPage() {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-text-primary flex items-center gap-2"><Layers size={20} /> Ontology Browser</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {NODE_TYPES.map((nt) => (
          <div key={nt.type} className="card flex items-center gap-3">
            <span className="w-3 h-3 rounded-full flex-shrink-0" style={{ backgroundColor: NODE_COLORS[nt.type] }} />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-text-primary capitalize">{nt.type.replace("_", " ")}</p>
              <p className="text-xs text-text-secondary">{nt.desc}</p>
            </div>
            <span className="badge bg-surface-hover text-text-secondary text-[10px]">{nt.tier}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
