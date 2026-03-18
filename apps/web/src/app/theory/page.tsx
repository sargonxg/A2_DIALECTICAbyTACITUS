"use client";

import Link from "next/link";
import { useTheoryFrameworks } from "@/hooks/useReasoning";
import { BookOpen } from "lucide-react";

const FRAMEWORKS = [
  { id: "glasl", name: "Glasl Escalation Model", author: "Friedrich Glasl", color: "#f43f5e" },
  { id: "fisher_ury", name: "Principled Negotiation", author: "Fisher & Ury", color: "#14b8a6" },
  { id: "zartman", name: "Ripeness Theory", author: "I. William Zartman", color: "#f59e0b" },
  { id: "galtung", name: "Structural Violence", author: "Johan Galtung", color: "#6366f1" },
  { id: "burton", name: "Basic Human Needs", author: "John Burton", color: "#22c55e" },
  { id: "kriesberg", name: "Conflict Dynamics", author: "Louis Kriesberg", color: "#06b6d4" },
  { id: "lederach", name: "Conflict Transformation", author: "John Paul Lederach", color: "#ec4899" },
  { id: "deutsch", name: "Cooperation & Competition", author: "Morton Deutsch", color: "#a855f7" },
  { id: "pearl_causal", name: "Causal Inference", author: "Judea Pearl", color: "#3b82f6" },
  { id: "french_raven", name: "Bases of Power", author: "French & Raven", color: "#d946ef" },
  { id: "mayer_trust", name: "Trust Model", author: "Mayer et al.", color: "#8b5cf6" },
  { id: "plutchik", name: "Emotion Theory", author: "Robert Plutchik", color: "#fb923c" },
  { id: "thomas_kilmann", name: "Conflict Modes", author: "Thomas & Kilmann", color: "#78716c" },
  { id: "winslade_monk", name: "Narrative Mediation", author: "Winslade & Monk", color: "#ec4899" },
  { id: "ury_brett_goldberg", name: "Dispute Systems Design", author: "Ury, Brett & Goldberg", color: "#64748b" },
];

export default function TheoryPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-text-primary flex items-center gap-2">
        <BookOpen size={24} /> Theory Frameworks
      </h1>
      <p className="text-text-secondary max-w-2xl">
        DIALECTICA integrates 15 conflict resolution theory frameworks. Each framework provides a unique analytical lens for understanding and resolving conflicts.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {FRAMEWORKS.map((fw) => (
          <Link key={fw.id} href={`/theory/${fw.id}`}>
            <div className="card-hover space-y-2">
              <div className="w-8 h-1 rounded-full" style={{ backgroundColor: fw.color }} />
              <h3 className="font-semibold text-text-primary">{fw.name}</h3>
              <p className="text-sm text-text-secondary">{fw.author}</p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
