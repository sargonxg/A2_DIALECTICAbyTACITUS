"use client";

import { Code2 } from "lucide-react";

const EXAMPLES = [
  { title: "Syria Conflict Analysis", desc: "Analyze the Syrian civil war using multi-framework assessment", domain: "armed" },
  { title: "HR Mediation", desc: "Map workplace disputes using interest-based analysis", domain: "workplace" },
  { title: "Commercial Arbitration", desc: "Structure commercial disputes with Glasl staging", domain: "commercial" },
];

export default function ExamplesPage() {
  return (
    <div className="max-w-3xl space-y-6">
      <h1 className="text-2xl font-bold text-text-primary flex items-center gap-2"><Code2 size={24} /> Examples</h1>
      <p className="text-text-secondary">Real-world use cases demonstrating the DIALECTICA API.</p>

      <div className="space-y-4">
        {EXAMPLES.map((ex) => (
          <div key={ex.title} className="card-hover">
            <h3 className="font-semibold text-text-primary">{ex.title}</h3>
            <p className="text-sm text-text-secondary">{ex.desc}</p>
            <span className="badge bg-accent/10 text-accent text-[10px] mt-2">{ex.domain}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
