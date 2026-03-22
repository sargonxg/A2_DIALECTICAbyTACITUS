"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Brain,
  Network,
  Shield,
  BookOpen,
  Scale,
  Users,
  Globe,
  Zap,
  Layers,
  ArrowRight,
  ExternalLink,
  Code2,
  Database,
  Cpu,
  GitBranch,
  Target,
  Search,
  CheckCircle2,
  XCircle,
  ChevronRight,
  Workflow,
  HeartHandshake,
  Landmark,
  CircuitBoard,
} from "lucide-react";

/* ─────────────────────────────────────────────────────────────── */
/*  DIALECTICA by TACITUS — Landing Page                          */
/* ─────────────────────────────────────────────────────────────── */

export default function HomePage() {
  const [showTooltip, setShowTooltip] = useState(false);

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-background">
      {/* ══════════════════════════════════════════════════════════ */}
      {/*  NAV BAR                                                  */}
      {/* ══════════════════════════════════════════════════════════ */}
      <nav className="sticky top-0 z-50 border-b border-zinc-800/60 bg-background/80 backdrop-blur-md">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          {/* Logo */}
          <div className="flex items-center gap-2">
            <span className="text-xl font-bold tracking-tight text-white">
              DIALECTICA
            </span>
            <span className="text-xs font-mono text-zinc-500">by TACITUS</span>
          </div>

          {/* Center links — hidden on mobile */}
          <div className="hidden items-center gap-6 md:flex">
            <Link
              href="/demo"
              className="text-sm text-zinc-400 hover:text-white transition-colors"
            >
              Demo
            </Link>
            <Link
              href="/developers/docs"
              className="text-sm text-zinc-400 hover:text-white transition-colors"
            >
              Docs
            </Link>
            <Link
              href="/theory"
              className="text-sm text-zinc-400 hover:text-white transition-colors"
            >
              Theory
            </Link>
            <Link
              href="/admin/architecture"
              className="text-sm text-zinc-400 hover:text-white transition-colors"
            >
              About
            </Link>
          </div>

          {/* Right side */}
          <div className="flex items-center gap-4">
            <a
              href="https://tacitus.me"
              target="_blank"
              rel="noopener noreferrer"
              className="hidden text-sm text-zinc-500 hover:text-teal-400 transition-colors sm:inline-flex items-center gap-1"
            >
              tacitus.me
              <ExternalLink className="h-3 w-3" />
            </a>

            {/* CTA with Coming Soon tooltip */}
            <div className="relative">
              <Link
                href="/workspaces"
                className="inline-flex items-center gap-2 rounded-lg bg-teal-500/10 border border-teal-500/30 px-4 py-2 text-sm font-semibold text-teal-400 hover:bg-teal-500/20 transition-colors"
                onMouseEnter={() => setShowTooltip(true)}
                onMouseLeave={() => setShowTooltip(false)}
              >
                Access DIALECTICA
                <span className="rounded-full bg-teal-400/20 px-2 py-0.5 text-[10px] uppercase tracking-wider text-teal-300">
                  Coming Soon
                </span>
              </Link>
              {showTooltip && (
                <div className="absolute right-0 top-full mt-2 w-56 rounded-lg border border-zinc-700 bg-zinc-900 p-3 text-xs text-zinc-400 shadow-xl">
                  DIALECTICA is in private preview. Join the waitlist for early
                  access.
                </div>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* ══════════════════════════════════════════════════════════ */}
      {/*  HERO                                                     */}
      {/* ══════════════════════════════════════════════════════════ */}
      <section className="relative overflow-hidden">
        {/* Grid background */}
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

        <div className="relative mx-auto max-w-4xl px-6 pb-20 pt-28 text-center">
          <p className="mb-6 inline-flex items-center gap-2 rounded-full border border-zinc-700 bg-zinc-800/50 px-4 py-1.5 text-xs font-medium tracking-wide text-teal-400 uppercase">
            <CircuitBoard className="h-3.5 w-3.5" />
            The deterministic intelligence layer
          </p>

          <h1 className="text-4xl font-bold text-white sm:text-5xl lg:text-6xl leading-[1.1] tracking-tight">
            The deterministic intelligence{" "}
            <br className="hidden sm:block" />
            layer for conflict
          </h1>

          <p className="mx-auto mt-6 max-w-2xl text-lg text-zinc-400 leading-relaxed">
            DIALECTICA structures any conflict &mdash; workplace friction,
            commercial disputes, geopolitical crises &mdash; into a computable
            knowledge graph grounded in 15 peer-reviewed theoretical frameworks.{" "}
            <span className="text-zinc-300 font-medium">
              We give LLMs the context layer they&apos;re missing.
            </span>
          </p>

          <div className="mt-10 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
            <Link
              href="/demo"
              className="inline-flex items-center gap-2 rounded-lg bg-teal-600 px-8 py-3 text-base font-semibold text-white shadow-lg shadow-teal-500/20 hover:bg-teal-500 transition-colors"
            >
              See it in action
              <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              href="/developers/docs"
              className="inline-flex items-center gap-2 rounded-lg border border-zinc-700 bg-zinc-800/50 px-8 py-3 text-base text-zinc-300 hover:bg-zinc-800 hover:text-white transition-colors"
            >
              <BookOpen className="h-4 w-4" />
              Read the docs
            </Link>
          </div>
        </div>

        {/* ── Three Layers Visual ── */}
        <div className="relative mx-auto max-w-5xl px-6 pb-24">
          <div className="grid gap-4 md:grid-cols-3">
            {/* Context Layer */}
            <div className="group rounded-xl border border-zinc-800 bg-zinc-900/50 p-6 transition-all hover:border-teal-500/30 hover:bg-zinc-900/80">
              <div className="mb-4 flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-teal-500/10 text-teal-400">
                  <Search className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-[10px] font-bold uppercase tracking-widest text-teal-400">
                    Layer 1
                  </p>
                  <h3 className="text-sm font-semibold text-white">
                    Context Layer
                  </h3>
                </div>
              </div>
              <p className="text-sm text-zinc-400 leading-relaxed">
                We extract actors, interests, power dynamics, emotions, trust
                states, and causal chains from unstructured text.
              </p>
            </div>

            {/* Foundation Layer */}
            <div className="group rounded-xl border border-zinc-800 bg-zinc-900/50 p-6 transition-all hover:border-teal-500/30 hover:bg-zinc-900/80">
              <div className="mb-4 flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-teal-500/10 text-teal-400">
                  <Shield className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-[10px] font-bold uppercase tracking-widest text-teal-400">
                    Layer 2
                  </p>
                  <h3 className="text-sm font-semibold text-white">
                    Foundation Layer
                  </h3>
                </div>
              </div>
              <p className="text-sm text-zinc-400 leading-relaxed">
                25+ deterministic symbolic rules fire against the Conflict
                Grammar ontology (15 node types, 20 edge types) &mdash; treaty
                violations, escalation thresholds, ripeness conditions are{" "}
                <span className="text-zinc-300 font-medium">
                  computed, never hallucinated
                </span>
                .
              </p>
            </div>

            {/* Reasoning Layer */}
            <div className="group rounded-xl border border-zinc-800 bg-zinc-900/50 p-6 transition-all hover:border-teal-500/30 hover:bg-zinc-900/80">
              <div className="mb-4 flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-teal-500/10 text-teal-400">
                  <Brain className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-[10px] font-bold uppercase tracking-widest text-teal-400">
                    Layer 3
                  </p>
                  <h3 className="text-sm font-semibold text-white">
                    Reasoning Layer
                  </h3>
                </div>
              </div>
              <p className="text-sm text-zinc-400 leading-relaxed">
                6 AI agents reason over structured graphs, not raw text. Neural
                predictions are firewalled &mdash; deterministic conclusions are{" "}
                <span className="text-zinc-300 font-medium">
                  never overridden
                </span>{" "}
                by probabilistic ones.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════ */}
      {/*  WHY THIS MATTERS — Comparison Table                      */}
      {/* ══════════════════════════════════════════════════════════ */}
      <section className="border-t border-zinc-800 bg-zinc-900/30">
        <div className="mx-auto max-w-5xl px-6 py-24">
          <h2 className="text-center text-3xl font-bold text-white">
            Why LLMs need a deterministic foundation for conflict
          </h2>
          <p className="mx-auto mt-3 max-w-2xl text-center text-zinc-400">
            Language models guess. DIALECTICA computes. Here&apos;s the
            difference.
          </p>

          {/* Comparison table — responsive */}
          <div className="mt-12 overflow-x-auto">
            <table className="w-full min-w-[700px] border-collapse">
              <thead>
                <tr className="border-b border-zinc-800">
                  <th className="px-4 py-3 text-left text-sm font-semibold text-zinc-400 w-[30%]">
                    Question
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-zinc-500 w-[35%]">
                    <span className="inline-flex items-center gap-1.5">
                      <XCircle className="h-4 w-4 text-red-400/60" />
                      LLM Alone
                    </span>
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-teal-400 w-[35%]">
                    <span className="inline-flex items-center gap-1.5">
                      <CheckCircle2 className="h-4 w-4" />
                      LLM + DIALECTICA
                    </span>
                  </th>
                </tr>
              </thead>
              <tbody className="text-sm">
                {[
                  {
                    question: "\"What stage is this conflict at?\"",
                    llm: "Guesses based on keywords",
                    dialectica:
                      "Computes Glasl stage from event chains + escalation velocity",
                  },
                  {
                    question: "\"Are there treaty violations?\"",
                    llm: "Summarizes text about violations",
                    dialectica:
                      "Deterministic pattern matching against norm graph",
                  },
                  {
                    question: "\"Who has leverage?\"",
                    llm: "Describes who seems powerful",
                    dialectica:
                      "French & Raven power analysis with magnitude scores",
                  },
                  {
                    question: "\"Is this conflict ripe for resolution?\"",
                    llm: "General assessment",
                    dialectica:
                      "Zartman ripeness model: MHS + WO computed from graph",
                  },
                  {
                    question: "\"What are the underlying interests?\"",
                    llm: "Extracts stated positions",
                    dialectica:
                      "Maps stated vs unstated interests with BATNA analysis",
                  },
                  {
                    question: "\"How might this escalate?\"",
                    llm: "Speculative narrative",
                    dialectica:
                      "Causal chain analysis with mechanism tagging (escalation, retaliation, contagion)",
                  },
                ].map((row, i) => (
                  <tr
                    key={i}
                    className="border-b border-zinc-800/50 transition-colors hover:bg-zinc-800/20"
                  >
                    <td className="px-4 py-4 font-medium text-zinc-300">
                      {row.question}
                    </td>
                    <td className="px-4 py-4 text-zinc-500">{row.llm}</td>
                    <td className="px-4 py-4 text-teal-400/90">
                      {row.dialectica}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════ */}
      {/*  ACADEMIC FOUNDATIONS                                      */}
      {/* ══════════════════════════════════════════════════════════ */}
      <section className="border-t border-zinc-800">
        <div className="mx-auto max-w-5xl px-6 py-24">
          <div className="text-center">
            <h2 className="text-3xl font-bold text-white">
              Grounded in peer-reviewed conflict research
            </h2>
            <p className="mx-auto mt-3 max-w-2xl text-zinc-400">
              Every node type, edge type, and symbolic rule in DIALECTICA traces
              to published academic work.
            </p>
          </div>

          <div className="mt-12 grid gap-4 sm:grid-cols-2">
            {[
              {
                authors: "Glasl, F.",
                year: "1982",
                title:
                  "The Process of Conflict Escalation and Roles of Third Parties",
                contribution:
                  "9-stage model, basis for escalation detection",
                icon: Zap,
              },
              {
                authors: "Fisher, R. & Ury, W.",
                year: "1981",
                title: "Getting to Yes",
                contribution:
                  "Interest-based negotiation, BATNA framework",
                icon: Target,
              },
              {
                authors: "Zartman, I.W.",
                year: "2000",
                title: "Ripeness: The Hurting Stalemate and Beyond",
                contribution: "Ripeness theory for intervention timing",
                icon: Scale,
              },
              {
                authors: "Galtung, J.",
                year: "1969",
                title: "Violence, Peace, and Peace Research",
                contribution:
                  "Direct/structural/cultural violence triangle",
                icon: Layers,
              },
              {
                authors: "French, J. & Raven, B.",
                year: "1959",
                title: "The Bases of Social Power",
                contribution: "8 power domains",
                icon: Users,
              },
              {
                authors: "Mayer, R., Davis, J., & Schoorman, F.",
                year: "1995",
                title: "Model of Organizational Trust",
                contribution:
                  "Trust = f(ability, benevolence, integrity)",
                icon: HeartHandshake,
              },
              {
                authors: "Plutchik, R.",
                year: "1980",
                title:
                  "A General Psychoevolutionary Theory of Emotion",
                contribution: "8 primary emotions wheel",
                icon: Brain,
              },
              {
                authors: "Pearl, J.",
                year: "2009",
                title: "Causality",
                contribution:
                  "Causal inference for event chain analysis",
                icon: GitBranch,
              },
            ].map((ref, i) => {
              const IconComp = ref.icon;
              return (
                <div
                  key={i}
                  className="flex gap-4 rounded-lg border border-zinc-800 bg-zinc-900/50 p-5 transition-colors hover:border-zinc-700"
                >
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-zinc-800 text-teal-400">
                    <IconComp className="h-4 w-4" />
                  </div>
                  <div className="min-w-0">
                    <p className="text-sm text-zinc-300">
                      <span className="font-medium text-white">
                        {ref.authors}
                      </span>{" "}
                      ({ref.year}).{" "}
                      <span className="italic">&ldquo;{ref.title}.&rdquo;</span>
                    </p>
                    <p className="mt-1 text-xs text-teal-400/80">
                      {ref.contribution}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════ */}
      {/*  ONTOLOGY-AUGMENTED GENERATION                            */}
      {/* ══════════════════════════════════════════════════════════ */}
      <section className="border-t border-zinc-800 bg-zinc-900/30">
        <div className="mx-auto max-w-5xl px-6 py-24">
          <div className="text-center">
            <p className="mb-3 inline-flex items-center gap-2 rounded-full border border-zinc-700 bg-zinc-800/50 px-4 py-1.5 text-xs font-medium tracking-wide text-teal-400 uppercase">
              <Database className="h-3.5 w-3.5" />
              Beyond RAG
            </p>
            <h2 className="text-3xl font-bold text-white">
              Why ontology-augmented generation outperforms RAG
              <br className="hidden sm:block" />
              for structured domains
            </h2>
          </div>

          <div className="mt-12 grid gap-6 md:grid-cols-2">
            {/* Key Points */}
            <div className="space-y-4">
              {[
                {
                  text: "RAG retrieves chunks of text. OAG retrieves structured knowledge with typed relationships and computed properties.",
                  icon: Search,
                },
                {
                  text: "In conflict domains, relationships between entities ARE the data. A vector search can find mentions of \u2018Iran\u2019 and \u2018sanctions\u2019 \u2014 but it cannot compute that sanctions CAUSED enrichment breach which CAUSED escalation to Glasl stage 6.",
                  icon: Network,
                },
                {
                  text: "Deterministic symbolic rules provide guarantees that probabilistic models cannot: if a treaty exists and an event violates its terms, that violation is a fact, not a prediction.",
                  icon: Shield,
                },
              ].map((point, i) => (
                <div
                  key={i}
                  className="flex gap-4 rounded-lg border border-zinc-800 bg-zinc-900/60 p-5"
                >
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-teal-500/10 text-teal-400">
                    <point.icon className="h-4 w-4" />
                  </div>
                  <p className="text-sm text-zinc-400 leading-relaxed">
                    {point.text}
                  </p>
                </div>
              ))}
            </div>

            {/* Academic backing */}
            <div className="space-y-4">
              <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-6">
                <h3 className="mb-4 text-sm font-semibold uppercase tracking-wider text-zinc-500">
                  Academic backing
                </h3>
                <div className="space-y-4">
                  <div className="border-l-2 border-teal-500/40 pl-4">
                    <p className="text-sm text-zinc-300">
                      Pan et al. (2024).{" "}
                      <span className="italic text-zinc-400">
                        &ldquo;Unifying Large Language Models and Knowledge
                        Graphs: A Roadmap.&rdquo;
                      </span>
                    </p>
                    <p className="mt-1 text-xs text-zinc-500">
                      Argues for structured knowledge integration over
                      retrieval-only approaches. LLMs + KGs = complementary
                      strengths.
                    </p>
                  </div>
                  <div className="border-l-2 border-teal-500/40 pl-4">
                    <p className="text-sm text-zinc-300">
                      Ji et al. (2022).{" "}
                      <span className="italic text-zinc-400">
                        &ldquo;Survey on Knowledge Graphs: Representation,
                        Acquisition, and Applications.&rdquo;
                      </span>
                    </p>
                    <p className="mt-1 text-xs text-zinc-500">
                      Ontology-driven knowledge representation outperforms
                      unstructured retrieval for domains with rich relational
                      semantics.
                    </p>
                  </div>
                </div>
              </div>

              {/* RAG vs OAG mini comparison */}
              <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-6">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-zinc-500">
                      RAG
                    </p>
                    <ul className="space-y-1.5 text-xs text-zinc-500">
                      <li className="flex items-start gap-1.5">
                        <XCircle className="mt-0.5 h-3 w-3 shrink-0 text-red-400/50" />
                        Retrieves text chunks
                      </li>
                      <li className="flex items-start gap-1.5">
                        <XCircle className="mt-0.5 h-3 w-3 shrink-0 text-red-400/50" />
                        No relationship types
                      </li>
                      <li className="flex items-start gap-1.5">
                        <XCircle className="mt-0.5 h-3 w-3 shrink-0 text-red-400/50" />
                        Cannot compute causality
                      </li>
                    </ul>
                  </div>
                  <div>
                    <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-teal-400">
                      OAG
                    </p>
                    <ul className="space-y-1.5 text-xs text-teal-400/80">
                      <li className="flex items-start gap-1.5">
                        <CheckCircle2 className="mt-0.5 h-3 w-3 shrink-0" />
                        Typed knowledge graph
                      </li>
                      <li className="flex items-start gap-1.5">
                        <CheckCircle2 className="mt-0.5 h-3 w-3 shrink-0" />
                        20 edge types, computed
                      </li>
                      <li className="flex items-start gap-1.5">
                        <CheckCircle2 className="mt-0.5 h-3 w-3 shrink-0" />
                        Deterministic reasoning
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════ */}
      {/*  USE CASES                                                */}
      {/* ══════════════════════════════════════════════════════════ */}
      <section className="border-t border-zinc-800">
        <div className="mx-auto max-w-5xl px-6 py-24">
          <h2 className="text-center text-3xl font-bold text-white">
            One ontology, every conflict domain
          </h2>
          <p className="mx-auto mt-3 max-w-xl text-center text-zinc-400">
            The same Conflict Grammar powers analysis from HR desks to the UN
            Security Council.
          </p>

          <div className="mt-12 grid gap-6 sm:grid-cols-2">
            {[
              {
                title: "HR & Workplace",
                description:
                  "Detect escalation patterns before they become litigation. Map power dynamics, communication breakdowns, and trust erosion.",
                icon: Users,
                accent: "border-blue-500/40",
                link: "/demo",
              },
              {
                title: "Commercial Mediation",
                description:
                  "Structure complex multi-party disputes. Quantify interests, map BATNAs, identify zone of possible agreement.",
                icon: Scale,
                accent: "border-violet-500/40",
                link: "/demo",
              },
              {
                title: "Geopolitical Analysis",
                description:
                  "Track alliance networks, causal chains, and norm compliance across macro-scale conflicts.",
                icon: Globe,
                accent: "border-amber-500/40",
                link: "/demo",
              },
              {
                title: "Peacebuilding",
                description:
                  "Assess ripeness for intervention. Model trust trajectories. Design dispute resolution systems.",
                icon: Landmark,
                accent: "border-emerald-500/40",
                link: "/demo",
              },
            ].map((uc) => {
              const IconComp = uc.icon;
              return (
                <Link
                  key={uc.title}
                  href={uc.link}
                  className={`group flex gap-4 rounded-lg border-l-4 ${uc.accent} border border-zinc-800 bg-zinc-900/50 p-6 transition-colors hover:bg-zinc-800/40`}
                >
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-zinc-800 text-teal-400 group-hover:bg-zinc-700 transition-colors">
                    <IconComp className="h-5 w-5" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                      {uc.title}
                      <ChevronRight className="h-4 w-4 text-zinc-600 group-hover:text-teal-400 transition-colors" />
                    </h3>
                    <p className="mt-2 text-sm text-zinc-400">
                      {uc.description}
                    </p>
                  </div>
                </Link>
              );
            })}
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════ */}
      {/*  ARCHITECTURE PREVIEW                                     */}
      {/* ══════════════════════════════════════════════════════════ */}
      <section className="border-t border-zinc-800 bg-zinc-900/30">
        <div className="mx-auto max-w-5xl px-6 py-24">
          <div className="text-center">
            <h2 className="text-3xl font-bold text-white">
              Architecture Preview
            </h2>
            <p className="mx-auto mt-3 max-w-2xl text-zinc-400">
              A neurosymbolic pipeline from raw text to decision support in
              seconds.
            </p>
          </div>

          {/* Pipeline visual */}
          <div className="mt-12 overflow-x-auto">
            <div className="flex items-center gap-2 min-w-[800px] justify-center">
              {[
                {
                  label: "Unstructured Text",
                  icon: BookOpen,
                  sub: "Input",
                },
                {
                  label: "GLiNER NER",
                  icon: Search,
                  sub: "Pre-filter",
                },
                {
                  label: "Gemini Extraction",
                  icon: Cpu,
                  sub: "Structured",
                },
                {
                  label: "Pydantic Validation",
                  icon: Shield,
                  sub: "Type-safe",
                },
                {
                  label: "Neo4j Knowledge Graph",
                  icon: Network,
                  sub: "Graph DB",
                },
                {
                  label: "Symbolic Rules",
                  icon: Workflow,
                  sub: "Deterministic",
                },
                {
                  label: "AI Agents",
                  icon: Brain,
                  sub: "6 specialists",
                },
                {
                  label: "Decision Support",
                  icon: Target,
                  sub: "Output",
                },
              ].map((step, i, arr) => (
                <div key={i} className="flex items-center gap-2">
                  <div className="flex flex-col items-center gap-1.5 w-[90px]">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg border border-zinc-700 bg-zinc-800 text-teal-400">
                      <step.icon className="h-4 w-4" />
                    </div>
                    <p className="text-[10px] font-medium text-zinc-300 text-center leading-tight">
                      {step.label}
                    </p>
                    <p className="text-[9px] text-zinc-600 text-center">
                      {step.sub}
                    </p>
                  </div>
                  {i < arr.length - 1 && (
                    <ArrowRight className="h-3 w-3 shrink-0 text-zinc-600" />
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="mt-8 text-center">
            <Link
              href="/admin/architecture"
              className="inline-flex items-center gap-2 text-sm text-teal-400 hover:text-teal-300 transition-colors"
            >
              See full architecture
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════ */}
      {/*  DEVELOPER SECTION                                        */}
      {/* ══════════════════════════════════════════════════════════ */}
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
                Claude Desktop (MCP)
              </p>
              <pre className="overflow-x-auto rounded-md bg-black/40 px-4 py-3 font-mono text-sm text-teal-400">
                <code>MCP Server for Claude Desktop</code>
              </pre>
            </div>
          </div>

          {/* Developer links */}
          <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
            {[
              {
                label: "API Documentation",
                href: "/developers/docs",
                icon: BookOpen,
              },
              {
                label: "Playground",
                href: "/developers/playground",
                icon: Code2,
              },
              { label: "SDKs", href: "/developers/sdks", icon: Layers },
              {
                label: "Examples",
                href: "/developers/examples",
                icon: GitBranch,
              },
            ].map((link) => (
              <Link
                key={link.label}
                href={link.href}
                className="inline-flex items-center gap-2 rounded-lg border border-zinc-800 bg-zinc-900/50 px-4 py-2 text-sm text-zinc-400 hover:border-zinc-700 hover:text-white transition-colors"
              >
                <link.icon className="h-4 w-4 text-teal-400" />
                {link.label}
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════ */}
      {/*  FOOTER                                                   */}
      {/* ══════════════════════════════════════════════════════════ */}
      <footer className="border-t border-zinc-800 bg-zinc-900/50">
        <div className="mx-auto max-w-5xl px-6 py-10">
          <div className="flex flex-col items-center gap-6 sm:flex-row sm:justify-between">
            {/* Left — brand */}
            <div className="flex items-center gap-3">
              <a
                href="https://tacitus.me"
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm font-semibold text-white hover:text-teal-400 transition-colors"
              >
                TACITUS
              </a>
              <span className="text-zinc-700">|</span>
              <span className="text-xs text-zinc-600">
                Conflict intelligence infrastructure
              </span>
            </div>

            {/* Center — links */}
            <div className="flex flex-wrap items-center justify-center gap-6">
              <Link
                href="/demo"
                className="text-sm text-zinc-500 hover:text-white transition-colors"
              >
                Demo
              </Link>
              <Link
                href="/developers/docs"
                className="text-sm text-zinc-500 hover:text-white transition-colors"
              >
                Docs
              </Link>
              <Link
                href="/theory"
                className="text-sm text-zinc-500 hover:text-white transition-colors"
              >
                Theory
              </Link>
              <Link
                href="/admin/architecture"
                className="text-sm text-zinc-500 hover:text-white transition-colors"
              >
                Architecture
              </Link>
            </div>

            {/* Right — external */}
            <div className="flex items-center gap-4">
              <a
                href="https://github.com/tacitus-io"
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-zinc-500 hover:text-white transition-colors"
              >
                GitHub
              </a>
              <a
                href="https://tacitus.me"
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-zinc-500 hover:text-white transition-colors"
              >
                tacitus.me
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
