"use client";

import { BookOpen } from "lucide-react";

const NODE_TYPES = [
  { label: "Actor", color: "#3b82f6", desc: "Individual or collective participant in a conflict" },
  { label: "Issue", color: "#f59e0b", desc: "Point of contention or dispute" },
  { label: "Position", color: "#8b5cf6", desc: "Stated stance on an issue" },
  { label: "Interest", color: "#06b6d4", desc: "Underlying motivation or need" },
  { label: "Event", color: "#ef4444", desc: "Discrete occurrence with temporal location" },
  { label: "Statement", color: "#ec4899", desc: "Quoted or reported communication" },
  { label: "Agreement", color: "#10b981", desc: "Formal or informal accord" },
  { label: "Grievance", color: "#f97316", desc: "Expressed harm or injustice" },
  { label: "Document", color: "#6b7280", desc: "Source text or artefact" },
  { label: "Organization", color: "#14b8a6", desc: "Formal body or institution" },
  { label: "Mediator", color: "#84cc16", desc: "Neutral third-party facilitator" },
  { label: "Coalition", color: "#a78bfa", desc: "Temporary alliance of actors" },
  { label: "Territory", color: "#fb923c", desc: "Geographic area under dispute" },
  { label: "Timeline", color: "#38bdf8", desc: "Temporal frame of conflict phase" },
  { label: "Frame", color: "#e879f9", desc: "Interpretive lens applied to conflict" },
];

const EDGE_TYPES = [
  { type: "OPPOSES", desc: "Actor opposes actor or position" },
  { type: "SUPPORTS", desc: "Actor supports actor or position" },
  { type: "TRUSTS", desc: "Trust relationship with direction and score" },
  { type: "MISTRUSTS", desc: "Negative trust or distrust" },
  { type: "HOLDS_POSITION", desc: "Actor holds a stated position" },
  { type: "HAS_INTEREST", desc: "Actor has an underlying interest" },
  { type: "PARTICIPATED_IN", desc: "Actor participated in event" },
  { type: "CAUSED", desc: "Event or actor caused event or grievance" },
  { type: "SIGNED", desc: "Actor signed agreement" },
  { type: "MEDIATES", desc: "Mediator facilitates between parties" },
  { type: "ALLIED_WITH", desc: "Alliance relationship" },
  { type: "ESCALATED_BY", desc: "Escalation causality" },
  { type: "REFERENCES", desc: "Statement or document references entity" },
  { type: "ADDRESSES", desc: "Agreement or position addresses issue" },
  { type: "MEMBER_OF", desc: "Actor is member of organization or coalition" },
  { type: "PRECEDED_BY", desc: "Temporal sequencing" },
  { type: "CLAIMS", desc: "Actor claims territory or right" },
  { type: "NEGOTIATED", desc: "Actors engaged in negotiation" },
  { type: "CONCEDES", desc: "Actor concedes point or position" },
  { type: "THREATENS", desc: "Actor threatens actor or action" },
];

const GLASL_STAGES = [
  { stage: 1, name: "Hardening", color: "#10b981", desc: "Positions harden, still manageable" },
  { stage: 2, name: "Debates & Polemics", color: "#84cc16", desc: "Verbal escalation begins" },
  { stage: 3, name: "Actions Not Words", color: "#f59e0b", desc: "Pressure tactics, actions replace dialogue" },
  { stage: 4, name: "Images & Coalitions", color: "#f97316", desc: "Stereotyping, coalition-building" },
  { stage: 5, name: "Loss of Face", color: "#ef4444", desc: "Public humiliation, no retreat" },
  { stage: 6, name: "Threat Strategies", color: "#dc2626", desc: "Ultimatums, threats dominate" },
  { stage: 7, name: "Limited Destructive Blows", color: "#b91c1c", desc: "Targeted damage begins" },
  { stage: 8, name: "Fragmentation", color: "#991b1b", desc: "Disintegration of enemy" },
  { stage: 9, name: "Together into the Abyss", color: "#7f1d1d", desc: "Mutual destruction accepted" },
];

export default function OntologyPage() {
  return (
    <div className="p-8 max-w-5xl">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-[#fafafa] mb-1">Ontology</h1>
        <p className="text-[#a1a1aa] text-sm">
          The DIALECTICA conflict knowledge graph ontology: node types, edge types, and the Glasl escalation model.
        </p>
      </div>

      {/* Node types */}
      <div className="mb-10">
        <div className="flex items-center gap-2 mb-4">
          <BookOpen size={16} className="text-[#71717a]" />
          <h2 className="text-[#fafafa] font-semibold text-sm uppercase tracking-wider">
            Node Types ({NODE_TYPES.length})
          </h2>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {NODE_TYPES.map((n) => (
            <div
              key={n.label}
              className="bg-[#18181b] border border-[#27272a] rounded-lg p-3 flex items-start gap-3"
            >
              <div
                className="w-3 h-3 rounded-full flex-shrink-0 mt-1"
                style={{ backgroundColor: n.color }}
              />
              <div>
                <p className="text-[#fafafa] text-sm font-medium font-mono">{n.label}</p>
                <p className="text-[#71717a] text-xs mt-0.5">{n.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Edge types */}
      <div className="mb-10">
        <h2 className="text-[#fafafa] font-semibold text-sm uppercase tracking-wider mb-4">
          Edge Types ({EDGE_TYPES.length})
        </h2>
        <div className="bg-[#18181b] border border-[#27272a] rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[#27272a] bg-[#09090b]/40">
                  <th className="text-left text-[#71717a] text-xs font-medium px-4 py-3 w-48">Type</th>
                  <th className="text-left text-[#71717a] text-xs font-medium px-4 py-3">Description</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#27272a]/60">
                {EDGE_TYPES.map((e) => (
                  <tr key={e.type} className="hover:bg-[#27272a]/20 transition-colors">
                    <td className="px-4 py-2.5">
                      <code className="text-teal-400 text-xs font-mono">{e.type}</code>
                    </td>
                    <td className="px-4 py-2.5 text-[#a1a1aa] text-xs">{e.desc}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Glasl stage model */}
      <div>
        <h2 className="text-[#fafafa] font-semibold text-sm uppercase tracking-wider mb-4">
          Glasl Escalation Model (9 Stages)
        </h2>
        <p className="text-[#71717a] text-xs mb-5">
          Friedrich Glasl&apos;s model describes nine stages of escalation grouped into three phases:
          Win-Win (1–3), Win-Lose (4–6), and Lose-Lose (7–9).
        </p>

        <div className="grid grid-cols-3 gap-2 mb-2">
          {[
            { label: "Win–Win", stages: "1–3", color: "text-green-400 border-green-500/30 bg-green-500/10" },
            { label: "Win–Lose", stages: "4–6", color: "text-orange-400 border-orange-500/30 bg-orange-500/10" },
            { label: "Lose–Lose", stages: "7–9", color: "text-red-400 border-red-500/30 bg-red-500/10" },
          ].map((phase) => (
            <div key={phase.label} className={`border rounded-lg px-3 py-2 text-center ${phase.color}`}>
              <p className="text-xs font-semibold">{phase.label}</p>
              <p className="text-xs opacity-70">Stages {phase.stages}</p>
            </div>
          ))}
        </div>

        <div className="space-y-2">
          {GLASL_STAGES.map((s) => (
            <div
              key={s.stage}
              className="bg-[#18181b] border border-[#27272a] rounded-lg p-3 flex items-center gap-4"
            >
              <div
                className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 text-sm font-bold"
                style={{ backgroundColor: s.color + "33", color: s.color, border: `1px solid ${s.color}55` }}
              >
                {s.stage}
              </div>
              <div className="flex-1">
                <p className="text-[#fafafa] text-sm font-medium">{s.name}</p>
                <p className="text-[#71717a] text-xs">{s.desc}</p>
              </div>
              <div
                className="w-2 h-2 rounded-full flex-shrink-0"
                style={{ backgroundColor: s.color }}
              />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
