import Link from "next/link";
import type { Metadata } from "next";
import {
  ArrowRight,
  Brain,
  CheckCircle2,
  Database,
  FileText,
  GitBranch,
  Network,
  ShieldCheck,
  Target,
} from "lucide-react";

export const metadata: Metadata = {
  title: "Situation Demo",
  description: "A simple investor demo showing how DIALECTICA turns a complex situation into a queryable, auditable graph.",
};

const steps = [
  {
    icon: FileText,
    label: "1. Read the situation",
    text: "A Syria briefing, a book, a case file, or a policy memo goes in.",
  },
  {
    icon: Network,
    label: "2. Build the graph",
    text: "DIALECTICA extracts actors, events, interests, constraints, evidence, and causal edges.",
  },
  {
    icon: Brain,
    label: "3. Ask real questions",
    text: "The system answers with graph paths, theory rules, citations, and confidence.",
  },
];

const graphNodes = [
  { id: "Russia", x: 64, y: 68, c: "#3b82f6" },
  { id: "Assad regime", x: 208, y: 64, c: "#3b82f6" },
  { id: "Aleppo 2016", x: 352, y: 98, c: "#eab308" },
  { id: "Astana 2017", x: 488, y: 138, c: "#06b6d4" },
  { id: "HTS 2024", x: 342, y: 245, c: "#eab308" },
  { id: "Iran", x: 184, y: 238, c: "#3b82f6" },
  { id: "Turkey", x: 64, y: 200, c: "#3b82f6" },
];

const graphEdges = [
  ["Russia", "Assad regime", "HAS_POWER_OVER"],
  ["Russia", "Aleppo 2016", "CAUSED"],
  ["Aleppo 2016", "Astana 2017", "CAUSED"],
  ["Iran", "Assad regime", "SUPPORTS"],
  ["Turkey", "HTS 2024", "INFLUENCES"],
  ["HTS 2024", "Assad regime", "TARGETED"],
];

const answers = [
  {
    q: "Did Russia's 2015 intervention cause regime survival?",
    a: "Yes, for the 2016-2018 window. The trace runs through airpower, Aleppo, rebel fragmentation, and Astana.",
    proof: "Cited graph path: Russia -> intervention -> Aleppo -> Astana.",
  },
  {
    q: "Why did Geneva lose to Astana?",
    a: "Because bargaining power moved to the actors who could enforce facts on the ground.",
    proof: "Rule: BATNA shift. Evidence: Aleppo recapture and external sponsor leverage.",
  },
  {
    q: "What is the 5-year recurrence risk?",
    a: "The model flags elevated recurrence risk because structural violence and spoiler-to-successor transition remain unresolved.",
    proof: "Frameworks: Walter recurrence, Galtung violence, spoiler typology.",
  },
];

const layers = [
  ["Source", "briefing, article, book, note"],
  ["Situation", "actors, events, interests, constraints"],
  ["Time", "episodes, valid dates, change since"],
  ["Causality", "caused, enabled, constrained, contradicted"],
  ["Reasoning", "rules, traces, confidence, review"],
];

function findNode(id: string) {
  const node = graphNodes.find((item) => item.id === id);
  if (!node) throw new Error(`Missing graph node ${id}`);
  return node;
}

function MiniGraph() {
  return (
    <svg viewBox="0 0 560 320" role="img" aria-label="Example Syria situation graph" className="h-full w-full">
      <defs>
        <marker id="arrow" markerWidth="8" markerHeight="8" refX="8" refY="4" orient="auto">
          <path d="M0,0 L8,4 L0,8 Z" fill="#64748b" />
        </marker>
      </defs>
      {graphEdges.map(([from, to, label]) => {
        const a = findNode(from);
        const b = findNode(to);
        return (
          <g key={`${from}-${to}`}>
            <line
              x1={a.x}
              y1={a.y}
              x2={b.x}
              y2={b.y}
              stroke="#334155"
              strokeWidth="2"
              markerEnd="url(#arrow)"
            />
            <text x={(a.x + b.x) / 2} y={(a.y + b.y) / 2 - 6} fill="#94a3b8" fontSize="10" textAnchor="middle">
              {label}
            </text>
          </g>
        );
      })}
      {graphNodes.map((node) => (
        <g key={node.id}>
          <circle cx={node.x} cy={node.y} r="20" fill={node.c} opacity="0.95" />
          <circle cx={node.x} cy={node.y} r="28" fill="none" stroke={node.c} opacity="0.22" strokeWidth="8" />
          <text x={node.x} y={node.y + 42} fill="#e2e8f0" fontSize="12" textAnchor="middle">
            {node.id}
          </text>
        </g>
      ))}
    </svg>
  );
}

export default function SituationDemoPage() {
  return (
    <main className="min-h-screen bg-background text-text-primary">
      <header className="mx-auto flex max-w-7xl items-center justify-between px-5 py-5">
        <Link href="/" className="font-mono text-sm font-bold tracking-wide">
          DIALECTICA <span className="text-accent">TACITUS</span>
        </Link>
        <nav className="flex items-center gap-2 text-sm">
          <Link href="/demo/syria/reasoning" className="btn-secondary">
            Traced answers
          </Link>
          <Link href="/demo" className="btn-primary">
            Live ingestion
          </Link>
        </nav>
      </header>

      <section className="mx-auto grid max-w-7xl gap-8 px-5 pb-14 pt-8 lg:grid-cols-[0.92fr_1.08fr] lg:items-center">
        <div>
          <p className="inline-flex rounded-md border border-accent/30 bg-accent/10 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-accent">
            VC demo, plain English
          </p>
          <h1 className="mt-5 max-w-4xl text-5xl font-semibold leading-tight md:text-6xl">
            A situation becomes a graph. The graph becomes better decisions.
          </h1>
          <p className="mt-6 max-w-2xl text-lg leading-8 text-text-secondary">
            DIALECTICA reads complex material and builds a structured, evidence-backed map of the situation.
            Then teams can ask questions that normal chatbots cannot answer reliably.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <a href="#walkthrough" className="btn-primary inline-flex items-center gap-2">
              Walk through it
              <ArrowRight className="h-4 w-4" aria-hidden="true" />
            </a>
            <Link href="/demo/syria/reasoning" className="btn-secondary">
              Open the answer demo
            </Link>
          </div>
        </div>

        <div className="rounded-lg border border-border bg-surface p-4 shadow-2xl shadow-black/20">
          <div className="mb-3 flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-accent">Example graph</p>
              <h2 className="text-xl font-semibold">Syria 2011-2024, simplified</h2>
            </div>
            <Database className="h-6 w-6 text-accent" aria-hidden="true" />
          </div>
          <div className="h-[360px] rounded-md border border-border bg-background p-2">
            <MiniGraph />
          </div>
        </div>
      </section>

      <section id="walkthrough" className="border-y border-border bg-surface/50">
        <div className="mx-auto grid max-w-7xl gap-4 px-5 py-8 md:grid-cols-3">
          {steps.map((step) => (
            <article key={step.label} className="rounded-lg border border-border bg-background p-5">
              <step.icon className="h-6 w-6 text-accent" aria-hidden="true" />
              <h2 className="mt-4 text-xl font-semibold">{step.label}</h2>
              <p className="mt-2 text-sm leading-6 text-text-secondary">{step.text}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="mx-auto grid max-w-7xl gap-8 px-5 py-16 lg:grid-cols-[0.75fr_1.25fr]">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-accent">The core insight</p>
          <h2 className="mt-2 text-3xl font-semibold">We do not ask AI to guess. We give it structure.</h2>
          <p className="mt-4 text-sm leading-7 text-text-secondary">
            A language model can summarize Syria. DIALECTICA builds the situation memory beneath the answer:
            source, time, actors, constraints, causality, theory rules, and trace.
          </p>
        </div>
        <div className="grid gap-3">
          {answers.map((item) => (
            <article key={item.q} className="rounded-lg border border-border bg-surface p-5">
              <h3 className="text-lg font-semibold">{item.q}</h3>
              <p className="mt-2 text-sm leading-6 text-text-secondary">{item.a}</p>
              <div className="mt-3 flex items-start gap-2 rounded-md border border-accent/20 bg-accent/10 p-3">
                <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-accent" aria-hidden="true" />
                <p className="text-xs leading-5 text-text-secondary">{item.proof}</p>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-5 pb-16">
        <div className="grid gap-5 lg:grid-cols-[1fr_1fr]">
          <div className="rounded-lg border border-border bg-surface p-5">
            <div className="mb-4 flex items-center gap-2">
              <GitBranch className="h-5 w-5 text-accent" aria-hidden="true" />
              <h2 className="text-2xl font-semibold">The five graph layers</h2>
            </div>
            <div className="space-y-2">
              {layers.map(([name, text]) => (
                <div key={name} className="grid grid-cols-[110px_1fr] gap-3 rounded-md border border-border bg-background p-3 text-sm">
                  <span className="font-semibold text-text-primary">{name}</span>
                  <span className="text-text-secondary">{text}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="rounded-lg border border-border bg-surface p-5">
            <div className="mb-4 flex items-center gap-2">
              <Target className="h-5 w-5 text-accent" aria-hidden="true" />
              <h2 className="text-2xl font-semibold">Why buyers care</h2>
            </div>
            <div className="space-y-3">
              {[
                "Policy teams can see which claims are supported and which are weak.",
                "Mediators can identify ripeness, leverage, spoilers, and hidden interests.",
                "Executives can turn a pile of documents into a reusable decision layer.",
              ].map((text) => (
                <div key={text} className="flex gap-3 rounded-md border border-border bg-background p-3">
                  <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-accent" aria-hidden="true" />
                  <p className="text-sm leading-6 text-text-secondary">{text}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-5 pb-20">
        <div className="rounded-lg border border-accent/30 bg-accent/10 p-6 md:flex md:items-center md:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-accent">Suggested VC flow</p>
            <h2 className="mt-1 text-2xl font-semibold">Start here, then open the traced answer demo.</h2>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-text-secondary">
              This page explains what we do. The reasoning theatre proves the answer format. The ingestion theatre proves the graph can be built.
            </p>
          </div>
          <div className="mt-5 flex flex-wrap gap-3 md:mt-0">
            <Link href="/demo/syria/reasoning" className="btn-primary inline-flex items-center gap-2">
              Show traced answers
              <ArrowRight className="h-4 w-4" aria-hidden="true" />
            </Link>
            <Link href="/demo" className="btn-secondary">
              Show ingestion
            </Link>
          </div>
        </div>
      </section>
    </main>
  );
}
