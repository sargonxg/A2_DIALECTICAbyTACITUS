"use client";

import Link from "next/link";
import {
  Network,
  Brain,
  Shield,
  Layers,
  ArrowRight,
} from "lucide-react";

const FEATURES = [
  {
    icon: Network,
    title: "Knowledge Graphs",
    description: "Map conflicts as rich, interconnected graphs with 15 node types and 20+ edge types.",
  },
  {
    icon: Brain,
    title: "Neurosymbolic AI",
    description: "Combine LLM-powered extraction with theory-grounded symbolic reasoning.",
  },
  {
    icon: Shield,
    title: "15 Theory Frameworks",
    description: "Glasl escalation, Fisher/Ury interests, Zartman ripeness, and 12 more.",
  },
  {
    icon: Layers,
    title: "Three-Tier Ontology",
    description: "Essential, Standard, and Full tiers for progressive analytical depth.",
  },
];

export default function HomePage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[calc(100vh-8rem)]">
      <div className="max-w-3xl text-center space-y-8">
        {/* Hero */}
        <div className="space-y-4">
          <h1 className="text-5xl font-bold tracking-tight">
            <span className="text-accent">DIALECTICA</span>
          </h1>
          <p className="text-lg text-text-secondary font-mono">
            by TACITUS&#x25F3;
          </p>
          <p className="text-xl text-text-secondary max-w-2xl mx-auto">
            The Universal Data Layer for Human Friction. Structure, analyze, and
            reason about conflict through theory-grounded knowledge graphs.
          </p>
        </div>

        {/* CTA */}
        <div className="flex gap-4 justify-center">
          <Link href="/workspaces" className="btn-primary flex items-center gap-2">
            Open Workbench <ArrowRight size={16} />
          </Link>
          <Link href="/developers/docs" className="btn-secondary">
            API Documentation
          </Link>
        </div>

        {/* Features */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-12">
          {FEATURES.map((f) => (
            <div key={f.title} className="card-hover text-left">
              <f.icon size={24} className="text-accent mb-2" />
              <h3 className="font-semibold text-text-primary">{f.title}</h3>
              <p className="text-sm text-text-secondary mt-1">{f.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
