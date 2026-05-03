import Link from "next/link";
import type { Metadata } from "next";
import { ArrowRight, Brain, CheckCircle2, FileText, Network, ShieldCheck } from "lucide-react";

export const metadata: Metadata = {
  title: "DIALECTICA by TACITUS",
  description: "DIALECTICA turns messy conflict information into an evidence-backed graph that teams can query, audit, and use.",
};

const proof = [
  {
    icon: FileText,
    title: "Reads messy material",
    text: "Reports, books, news, interviews, filings, and internal notes.",
  },
  {
    icon: Network,
    title: "Builds the situation graph",
    text: "Actors, interests, constraints, events, evidence, and causal links.",
  },
  {
    icon: Brain,
    title: "Answers with a trace",
    text: "Every answer shows the evidence, graph path, rule, and confidence.",
  },
];

const investorPoints = [
  "A graph backbone for policy, legal, intelligence, mediation, and enterprise risk workflows.",
  "Works where normal RAG fails: causality, temporality, leverage, interests, commitments, and provenance.",
  "The wedge is conflict intelligence. The platform is structured reasoning over high-stakes human systems.",
];

export default function HomePage() {
  return (
    <main className="min-h-screen bg-background text-text-primary">
      <header className="mx-auto flex max-w-7xl items-center justify-between px-5 py-5">
        <Link href="/" className="font-mono text-sm font-bold tracking-wide text-text-primary">
          DIALECTICA <span className="text-accent">TACITUS</span>
        </Link>
        <nav className="flex items-center gap-2 text-sm">
          <Link href="/situation-demo" className="btn-secondary">
            Situation demo
          </Link>
          <Link href="/demo" className="btn-primary">
            Live theatre
          </Link>
        </nav>
      </header>

      <section className="mx-auto grid max-w-7xl gap-10 px-5 pb-16 pt-12 lg:grid-cols-[1.05fr_0.95fr] lg:items-center">
        <div>
          <p className="mb-4 inline-flex rounded-md border border-accent/30 bg-accent/10 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-accent">
            Conflict intelligence infrastructure
          </p>
          <h1 className="max-w-4xl text-5xl font-semibold leading-tight tracking-normal text-text-primary md:text-6xl">
            We turn messy conflicts into evidence-backed knowledge graphs.
          </h1>
          <p className="mt-6 max-w-2xl text-lg leading-8 text-text-secondary">
            DIALECTICA gives analysts and decision-makers a structured map of who matters, what changed,
            what caused what, and what can be proven. It is the data layer that makes AI useful for high-stakes situations.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link href="/situation-demo" className="btn-primary inline-flex items-center gap-2">
              See the 90-second demo
              <ArrowRight className="h-4 w-4" aria-hidden="true" />
            </Link>
            <Link href="/demo/syria/reasoning" className="btn-secondary">
              View traced answers
            </Link>
          </div>
        </div>

        <div className="rounded-lg border border-border bg-surface p-5 shadow-2xl shadow-black/20">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-accent">What changes</p>
              <h2 className="mt-1 text-2xl font-semibold">From text to decisions</h2>
            </div>
            <ShieldCheck className="h-7 w-7 text-accent" aria-hidden="true" />
          </div>
          <div className="space-y-3">
            {proof.map((item) => (
              <article key={item.title} className="flex gap-3 rounded-md border border-border bg-background p-4">
                <item.icon className="mt-1 h-5 w-5 shrink-0 text-accent" aria-hidden="true" />
                <div>
                  <h3 className="font-semibold text-text-primary">{item.title}</h3>
                  <p className="mt-1 text-sm leading-6 text-text-secondary">{item.text}</p>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="border-y border-border bg-surface/50">
        <div className="mx-auto grid max-w-7xl gap-4 px-5 py-8 md:grid-cols-3">
          <div>
            <p className="text-3xl font-semibold text-text-primary">1 input</p>
            <p className="mt-1 text-sm text-text-secondary">A briefing, book, report, or case file.</p>
          </div>
          <div>
            <p className="text-3xl font-semibold text-text-primary">1 graph</p>
            <p className="mt-1 text-sm text-text-secondary">Typed entities, relationships, time, and evidence.</p>
          </div>
          <div>
            <p className="text-3xl font-semibold text-text-primary">Many products</p>
            <p className="mt-1 text-sm text-text-secondary">Answers, briefs, risk dashboards, simulations, and audits.</p>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-5 py-16">
        <div className="grid gap-8 lg:grid-cols-[0.8fr_1.2fr]">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-accent">Why this is investable</p>
            <h2 className="mt-2 text-3xl font-semibold">The problem is not chat. The problem is structured judgment.</h2>
          </div>
          <div className="grid gap-3">
            {investorPoints.map((point) => (
              <div key={point} className="flex gap-3 rounded-md border border-border bg-surface p-4">
                <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-accent" aria-hidden="true" />
                <p className="text-sm leading-6 text-text-secondary">{point}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-5 pb-20">
        <div className="rounded-lg border border-accent/30 bg-accent/10 p-6 md:flex md:items-center md:justify-between">
          <div>
            <h2 className="text-2xl font-semibold">Show the Syria situation demo first.</h2>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-text-secondary">
              It explains the product in plain language: read a real situation, build a graph, ask a question,
              show the trace, then explain why this becomes the backbone for TACITUS.
            </p>
          </div>
          <Link href="/situation-demo" className="btn-primary mt-5 inline-flex items-center gap-2 md:mt-0">
            Open demo
            <ArrowRight className="h-4 w-4" aria-hidden="true" />
          </Link>
        </div>
      </section>
    </main>
  );
}
