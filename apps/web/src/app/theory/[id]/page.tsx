"use client";

import { useParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, BookOpen } from "lucide-react";

const FRAMEWORK_DETAILS: Record<string, { name: string; author: string; description: string; concepts: string[]; interventions: string[] }> = {
  glasl: {
    name: "Glasl Escalation Model",
    author: "Friedrich Glasl",
    description: "A 9-stage model describing how conflicts escalate from mild tension to mutual destruction. Each stage maps to appropriate intervention strategies.",
    concepts: ["Hardening", "Debate & Polemics", "Actions Not Words", "Images & Coalitions", "Loss of Face", "Strategies of Threats", "Limited Destructive Blows", "Fragmentation of the Enemy", "Together into the Abyss"],
    interventions: ["Moderation (1-3)", "Process Consultation (2-3)", "Socio-therapeutic Process (4)", "Mediation (5)", "Arbitration (6)", "Power Intervention (7-9)"],
  },
  fisher_ury: {
    name: "Principled Negotiation",
    author: "Roger Fisher & William Ury",
    description: "Interest-based negotiation framework from 'Getting to Yes'. Separates people from problems, focuses on interests not positions, generates options for mutual gain.",
    concepts: ["Interests vs. Positions", "BATNA", "ZOPA", "Objective Criteria", "Separate People from Problem", "Mutual Gain Options"],
    interventions: ["Interest mapping", "BATNA assessment", "Option generation", "Objective criteria identification"],
  },
  zartman: {
    name: "Ripeness Theory",
    author: "I. William Zartman",
    description: "Conflicts become 'ripe' for resolution when parties perceive a Mutually Hurting Stalemate (MHS) and a Mutually Enticing Opportunity (MEO).",
    concepts: ["Mutually Hurting Stalemate", "Mutually Enticing Opportunity", "Way Out", "Ripe Moment", "Precipice"],
    interventions: ["Ripeness assessment", "Creating sense of urgency", "Presenting viable alternatives", "Shuttle diplomacy"],
  },
};

export default function TheoryDetailPage() {
  const { id } = useParams();
  const framework = FRAMEWORK_DETAILS[id as string];

  if (!framework) {
    return (
      <div className="space-y-4">
        <Link href="/theory" className="btn-ghost flex items-center gap-1 w-fit"><ArrowLeft size={16} /> Back</Link>
        <div className="card text-center py-12">
          <BookOpen size={32} className="mx-auto text-text-secondary mb-2" />
          <p className="text-text-secondary">Framework details coming soon.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl space-y-6">
      <Link href="/theory" className="btn-ghost flex items-center gap-1 w-fit"><ArrowLeft size={16} /> Back to Frameworks</Link>
      <h1 className="text-2xl font-bold text-text-primary">{framework.name}</h1>
      <p className="text-text-secondary">{framework.author}</p>
      <p className="text-text-primary leading-relaxed">{framework.description}</p>

      <div className="card">
        <h3 className="font-semibold text-text-primary mb-3">Key Concepts</h3>
        <div className="flex flex-wrap gap-2">
          {framework.concepts.map((c) => (
            <span key={c} className="badge bg-accent/10 text-accent">{c}</span>
          ))}
        </div>
      </div>

      <div className="card">
        <h3 className="font-semibold text-text-primary mb-3">Intervention Strategies</h3>
        <ul className="space-y-1">
          {framework.interventions.map((s) => (
            <li key={s} className="text-sm text-text-secondary flex gap-2">
              <span className="text-accent">&bull;</span> {s}
            </li>
          ))}
        </ul>
      </div>

      <button className="btn-primary">Apply to Workspace</button>
    </div>
  );
}
