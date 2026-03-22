"use client";

import Link from "next/link";

export default function HomePage() {
  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-background">
      {/* ── NAV BAR ── */}
      <nav className="sticky top-0 z-50 border-b border-zinc-800/60 bg-background/80 backdrop-blur-md">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-2">
            <span className="text-xl font-bold tracking-tight text-white">
              DIALECTICA
            </span>
            <span className="text-xs font-mono text-zinc-500">by TACITUS</span>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/demo" className="text-sm text-zinc-400 hover:text-white transition-colors">
              Demo
            </Link>
            <Link href="/developers" className="text-sm text-zinc-400 hover:text-white transition-colors">
              Docs
            </Link>
            <Link href="/login" className="btn-primary text-sm">
              Sign In
            </Link>
          </div>
        </div>
      </nav>

      {/* ── HERO ── */}
      <section className="relative overflow-hidden">
        {/* Subtle grid background */}
        <div
          className="pointer-events-none absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage:
              "linear-gradient(rgba(255,255,255,.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.1) 1px, transparent 1px)",
            backgroundSize: "60px 60px",
          }}
        />
        {/* Glow */}
        <div className="pointer-events-none absolute left-1/2 top-0 -translate-x-1/2 h-[600px] w-[800px] rounded-full bg-teal-500/5 blur-3xl" />

        <div className="relative mx-auto max-w-4xl px-6 pb-24 pt-28 text-center">
          <p className="mb-6 inline-block rounded-full border border-zinc-700 bg-zinc-800/50 px-4 py-1.5 text-xs font-medium tracking-wide text-teal-400 uppercase">
            Conflict Intelligence Engine
          </p>
          <h1 className="text-5xl font-bold text-white sm:text-6xl lg:text-7xl leading-[1.1] tracking-tight">
            Make conflict computable.
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-zinc-400 leading-relaxed">
            From workplace disputes to geopolitical crises — DIALECTICA structures
            any conflict into a knowledge graph grounded in 30+ academic
            frameworks.
          </p>
          <div className="mt-10 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
            <Link
              href="/demo"
              className="btn-primary inline-flex items-center gap-2 px-8 py-3 text-base font-semibold rounded-lg shadow-lg shadow-teal-500/20"
            >
              Try the Demo
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
            </Link>
            <Link
              href="/developers"
              className="btn-secondary inline-flex items-center gap-2 px-8 py-3 text-base rounded-lg"
            >
              API Documentation
            </Link>
          </div>
        </div>
      </section>

      {/* ── CREDIBILITY BAR ── */}
      <section className="border-t border-zinc-800">
        <div className="mx-auto max-w-4xl px-6 py-6 text-center">
          <p className="text-sm text-zinc-500 leading-relaxed">
            Neurosymbolic conflict intelligence &middot; Grounded in 15 conflict resolution theories &middot; Built by{" "}
            <a href="https://tacitus.me" target="_blank" rel="noopener noreferrer" className="text-teal-400 hover:text-teal-300 transition-colors">TACITUS</a>
          </p>
        </div>
      </section>

      {/* ── HOW IT WORKS ── */}
      <section className="border-t border-zinc-800 bg-zinc-900/30">
        <div className="mx-auto max-w-5xl px-6 py-24">
          <h2 className="text-center text-3xl font-bold text-white">
            How It Works
          </h2>
          <p className="mx-auto mt-3 max-w-xl text-center text-zinc-400">
            Three steps from raw conflict data to theory-grounded analysis.
          </p>

          <div className="mt-16 grid gap-10 sm:grid-cols-3">
            {/* Step 1 */}
            <div className="text-center">
              <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full border border-zinc-700 bg-zinc-800 text-xl font-bold text-teal-400">
                1
              </div>
              <h3 className="mt-5 text-lg font-semibold text-white">
                Paste or upload conflict data
              </h3>
              <p className="mt-2 text-sm text-zinc-400 leading-relaxed">
                Drop in a memo, news article, negotiation transcript, or HR
                complaint. Plain text, PDF, or paste directly.
              </p>
            </div>

            {/* Step 2 */}
            <div className="text-center">
              <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full border border-zinc-700 bg-zinc-800 text-xl font-bold text-teal-400">
                2
              </div>
              <h3 className="mt-5 text-lg font-semibold text-white">
                AI extracts structured entities
              </h3>
              <p className="mt-2 text-sm text-zinc-400 leading-relaxed">
                Our neurosymbolic pipeline identifies actors, claims, interests,
                constraints, leverage, and 9 more entity types automatically.
              </p>
            </div>

            {/* Step 3 */}
            <div className="text-center">
              <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full border border-zinc-700 bg-zinc-800 text-xl font-bold text-teal-400">
                3
              </div>
              <h3 className="mt-5 text-lg font-semibold text-white">
                Get theory-grounded analysis
              </h3>
              <p className="mt-2 text-sm text-zinc-400 leading-relaxed">
                Symbolic rules fire against 30+ frameworks — Glasl escalation,
                Fisher/Ury interests, Zartman ripeness — delivering actionable
                insight.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ── DEPTH SHOWCASE ── */}
      <section className="border-t border-zinc-800">
        <div className="mx-auto max-w-5xl px-6 py-24">
          <h2 className="text-center text-3xl font-bold text-white">
            Analytical Depth
          </h2>
          <p className="mx-auto mt-3 max-w-xl text-center text-zinc-400">
            <span className="text-teal-400 font-semibold">15 Node Types</span>
            {" "}&middot;{" "}
            <span className="text-teal-400 font-semibold">20 Edge Types</span>
            {" "}&middot;{" "}
            <span className="text-teal-400 font-semibold">30+ Theoretical Frameworks</span>
          </p>

          <div className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {[
              {
                metric: "15",
                label: "Node Types",
                detail:
                  "Actor, Conflict, Event, Issue, Interest, Norm, Process, Outcome, Narrative, and more",
              },
              {
                metric: "20",
                label: "Edge Types",
                detail:
                  "ALLIES_WITH, OPPOSES, ESCALATES_TO, MEDIATES, CONSTRAINS, LEVERAGES, and more",
              },
              {
                metric: "30+",
                label: "Frameworks",
                detail:
                  "Glasl, Fisher/Ury, Zartman, Galtung, Lederach, Burton, Azar, and 23 more",
              },
              {
                metric: "9",
                label: "Symbolic Rules",
                detail:
                  "Deterministic reasoning over treaty violations, escalation thresholds, and ripeness",
              },
            ].map((card) => (
              <div
                key={card.label}
                className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-6 text-center transition-colors hover:border-zinc-700"
              >
                <p className="text-4xl font-bold text-teal-400">{card.metric}</p>
                <p className="mt-1 text-sm font-semibold text-white">
                  {card.label}
                </p>
                <p className="mt-2 text-xs text-zinc-500 leading-relaxed">
                  {card.detail}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── USE CASES ── */}
      <section className="border-t border-zinc-800 bg-zinc-900/30">
        <div className="mx-auto max-w-5xl px-6 py-24">
          <h2 className="text-center text-3xl font-bold text-white">
            Use Cases
          </h2>
          <p className="mx-auto mt-3 max-w-xl text-center text-zinc-400">
            One ontology, many domains.
          </p>

          <div className="mt-12 grid gap-6 sm:grid-cols-2">
            {[
              {
                title: "HR & Employee Relations",
                description: "Detect escalation before it becomes litigation.",
                accent: "border-blue-500/40",
              },
              {
                title: "Mediation & ADR",
                description: "Structure case complexity in seconds.",
                accent: "border-violet-500/40",
              },
              {
                title: "Political Risk",
                description:
                  "API-first conflict intelligence infrastructure.",
                accent: "border-amber-500/40",
              },
              {
                title: "Peacebuilding",
                description: "The intelligence layer the UN needs.",
                accent: "border-emerald-500/40",
              },
            ].map((uc) => (
              <div
                key={uc.title}
                className={`rounded-lg border-l-4 ${uc.accent} border border-zinc-800 bg-zinc-900/50 p-6 transition-colors hover:bg-zinc-800/40`}
              >
                <h3 className="text-lg font-semibold text-white">{uc.title}</h3>
                <p className="mt-2 text-sm text-zinc-400">{uc.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── DEVELOPER SECTION ── */}
      <section className="border-t border-zinc-800">
        <div className="mx-auto max-w-5xl px-6 py-24">
          <h2 className="text-center text-3xl font-bold text-white">
            Built for Developers
          </h2>
          <p className="mx-auto mt-3 max-w-xl text-center text-zinc-400">
            Install the ontology, hit the API, or connect via MCP.
          </p>

          <div className="mt-12 grid gap-6 sm:grid-cols-3">
            {/* Python */}
            <div className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-6">
              <p className="mb-3 text-xs font-medium uppercase tracking-wider text-zinc-500">
                Python
              </p>
              <pre className="overflow-x-auto rounded-md bg-black/40 px-4 py-3 font-mono text-sm text-teal-400">
                <code>pip install dialectica-ontology</code>
              </pre>
            </div>

            {/* Node / TypeScript */}
            <div className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-6">
              <p className="mb-3 text-xs font-medium uppercase tracking-wider text-zinc-500">
                Node / TypeScript
              </p>
              <pre className="overflow-x-auto rounded-md bg-black/40 px-4 py-3 font-mono text-sm text-teal-400">
                <code>npm install @tacitus/dialectica-sdk</code>
              </pre>
            </div>

            {/* MCP */}
            <div className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-6">
              <p className="mb-3 text-xs font-medium uppercase tracking-wider text-zinc-500">
                Claude Desktop
              </p>
              <pre className="overflow-x-auto rounded-md bg-black/40 px-4 py-3 font-mono text-sm text-teal-400">
                <code>MCP Server for Claude Desktop</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* ── FOOTER ── */}
      <footer className="border-t border-zinc-800 bg-zinc-900/50">
        <div className="mx-auto flex max-w-5xl flex-col items-center gap-4 px-6 py-10 sm:flex-row sm:justify-between">
          <div className="flex items-center gap-2">
            <a href="https://tacitus.me" target="_blank" rel="noopener noreferrer" className="text-sm font-semibold text-white hover:text-teal-400 transition-colors">TACITUS</a>
          </div>
          <div className="flex items-center gap-6">
            <Link href="/demo" className="text-sm text-zinc-500 hover:text-white transition-colors">
              Demo
            </Link>
            <Link href="/developers" className="text-sm text-zinc-500 hover:text-white transition-colors">
              API Docs
            </Link>
            <a
              href="https://tacitus.me"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-zinc-500 hover:text-white transition-colors"
            >
              tacitus.me
            </a>
            <a
              href="https://github.com/tacitus-io"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-zinc-500 hover:text-white transition-colors"
            >
              GitHub
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
