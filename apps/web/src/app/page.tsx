import Link from "next/link";
import type { Metadata } from "next";
import {
  ArrowRight,
  BarChart3,
  BookOpen,
  Brain,
  CheckCircle2,
  Clock,
  Cpu,
  Database,
  ExternalLink,
  FileJson,
  GitBranch,
  Globe2,
  Layers,
  Network,
  Search,
  Shield,
  Workflow,
  Zap,
} from "lucide-react";

export const metadata: Metadata = {
  title: "DIALECTICA Situation Graph Platform",
  description:
    "Dialectica turns documents, sources, and live cases into ontology-grounded graphs with provenance, temporal memory, reasoning, and benchmarks.",
};

const proofPoints = [
  { label: "Graph engines", value: "Neo4j + Graphiti + Cozo", detail: "source of truth, temporal memory, Datalog mirror" },
  { label: "Live demo", value: "Syria + Gutenberg", detail: "statecraft, sanctions, and book conflict ontologies" },
  { label: "API surface", value: "FastAPI + GraphOps", detail: "health, ingest, graph search, reasoning, timelines" },
  { label: "Cloud posture", value: "Cloud Run safe", detail: "stateless app, external graph, Cloud SQL audit" },
];

const graphNodes = [
  { label: "Sources", x: "8%", y: "24%", tone: "bg-sky-400", detail: "reports, books, articles" },
  { label: "Evidence", x: "23%", y: "64%", tone: "bg-cyan-400", detail: "spans + source_ids" },
  { label: "Ontology", x: "39%", y: "28%", tone: "bg-teal-400", detail: "Actor / Claim / Event" },
  { label: "Episodes", x: "53%", y: "70%", tone: "bg-amber-400", detail: "valid time + phases" },
  { label: "Causality", x: "68%", y: "34%", tone: "bg-rose-400", detail: "mechanisms + confidence" },
  { label: "Reasoning", x: "82%", y: "61%", tone: "bg-fuchsia-400", detail: "queries + benchmarks" },
];

const graphEdges = [
  ["Sources", "Evidence"],
  ["Evidence", "Ontology"],
  ["Ontology", "Episodes"],
  ["Episodes", "Causality"],
  ["Causality", "Reasoning"],
  ["Ontology", "Reasoning"],
];

const capabilities = [
  {
    title: "Ingest Messy Sources",
    icon: FileJson,
    detail:
      "Upload or paste reports, policy briefs, articles, transcripts, field notes, or public-domain books. The system chunks, hashes, timestamps, and attaches provenance before graph write.",
  },
  {
    title: "Compile Dynamic Ontologies",
    icon: Layers,
    detail:
      "Use a canonical backbone while adding domain-specific concepts: sanctions relief, SDF integration, trust injury, battle episode, scene evidence, or policy veto point.",
  },
  {
    title: "Create Temporal Episodes",
    icon: Clock,
    detail:
      "Every case can be read as phases: reporting windows, transition periods, scene sequences, battle episodes, changed_since windows, and valid_from/valid_to claims.",
  },
  {
    title: "Reason Over Graphs",
    icon: Brain,
    detail:
      "Ask actor profiles, leverage maps, indirect constraints, provenance traces, timelines, changed_since, and benchmark questions from structured graph data.",
  },
  {
    title: "Benchmark Against Plain LLMs",
    icon: BarChart3,
    detail:
      "Compare graph-grounded answers to ordinary LLM answers for provenance coverage, causal discipline, temporal correctness, leverage precision, and reviewability.",
  },
  {
    title: "Run As A Real Backend",
    icon: Cpu,
    detail:
      "FastAPI and GraphOps call the deployed backend. Neo4j stores the operational graph, Graphiti preserves temporal memory, Cozo mirrors reasoning, and Cloud SQL audits runs.",
  },
];

const demoTracks = [
  {
    title: "Syria Statecraft Demo",
    icon: Globe2,
    href: "/situation-demo",
    detail:
      "A concrete policy/conflict case showing SDF integration, Israeli southern-security pressure, sanctions relief, EU re-engagement, reconstruction risk, and humanitarian legitimacy.",
    queries: ["Who has leverage?", "What changed since the last report?", "Which sanctions mechanism blocks a project?"],
  },
  {
    title: "Gutenberg Book Graphs",
    icon: BookOpen,
    href: "/situation-demo#config-builder",
    detail:
      "Public-domain books become conflict graphs. War and Peace and Romeo and Juliet demonstrate characters, scenes, commitments, causal episodes, and interpretive review.",
    queries: ["Which episodes transform Pierre?", "Which event closes a mediation window?", "What is evidence vs interpretation?"],
  },
  {
    title: "GraphOps Control Room",
    icon: Workflow,
    href: "/graphops",
    detail:
      "The operator console for ingestion, extraction, ontology controls, Databricks jobs, graph writes, benchmarking, retrieval plans, and demo-ready workflows.",
    queries: ["Run extraction", "Write graph", "Inspect trace"],
  },
];

const stack = [
  { name: "Cloud SQL", role: "audit, pipeline history, run state", icon: Database },
  { name: "Neo4j", role: "operational graph source of truth", icon: Network },
  { name: "Graphiti", role: "temporal/provenance memory layer", icon: Clock },
  { name: "Cozo", role: "Datalog-style reasoning mirror", icon: Cpu },
  { name: "Databricks", role: "large-scale extraction and benchmarks", icon: BarChart3 },
  { name: "FastAPI", role: "health, ingest, graph, reasoning APIs", icon: Zap },
];

const ontologyExamples = [
  {
    domain: "Conflict Resolution",
    structure: "Actor -> Interest -> Constraint -> Commitment -> Guarantee",
    use: "separate positions from interests, identify trust injuries, and test mediation windows",
  },
  {
    domain: "Statecraft",
    structure: "ExternalActor -> Leverage -> Constraint -> PolicyOption",
    use: "map recognition, sanctions, border pressure, security demands, and diplomatic sequencing",
  },
  {
    domain: "Economic Sanctions",
    structure: "Authority -> ReliefCondition -> CapitalFlow -> ComplianceRisk",
    use: "understand what is authorized, delayed, still blocked, or risky for reconstruction",
  },
  {
    domain: "Books and Narrative",
    structure: "Scene -> Evidence -> CausalClaim -> IdentityShift",
    use: "turn novels into queryable conflict systems without flattening interpretation into summary",
  },
];

const productFlow = [
  "Source intake",
  "Evidence spans",
  "Ontology compile",
  "Temporal episodes",
  "Causal mechanisms",
  "Graph write",
  "Reasoning query",
  "Benchmark",
];

const demoReadiness = [
  {
    step: "Open the story",
    proof: "Landing page explains the real graph backbone before jumping into controls.",
  },
  {
    step: "Show the live case",
    proof: "Situation Demo displays Syria, sanctions mechanisms, temporal episodes, Gutenberg books, and D3 graph layers.",
  },
  {
    step: "Prove the backend",
    proof: "GraphOps and demo controls expose health, ingestion, search, reasoning, pipeline runs, and public configs.",
  },
  {
    step: "Close with evaluation",
    proof: "Benchmarks show why graph-grounded answers are more traceable than ordinary LLM summaries.",
  },
];

const researchWave = [
  {
    title: "GraphRAG for global sensemaking",
    source: "Microsoft Research / arXiv 2024",
    href: "https://arxiv.org/abs/2404.16130",
    finding:
      "GraphRAG was designed for questions over whole private corpora where vector-only retrieval struggles, using entity graphs and community summaries for more comprehensive answers.",
    dialecticaUse:
      "Policy teams ask global questions: what are the main constraints, leverage channels, factions, risks, and changed assumptions across a source pack?",
  },
  {
    title: "Knowledge graphs ground LLMs",
    source: "Neo4j GraphRAG resources",
    href: "https://neo4j.com/generativeai/",
    finding:
      "Knowledge graphs add structured relationships, graph retrieval, and explainability around LLM generation instead of relying only on semantic similarity.",
    dialecticaUse:
      "Dialectica stores actors, claims, constraints, leverage, events, evidence, and source_ids as graph objects that can be searched and traced.",
  },
  {
    title: "LLM + KG survey momentum",
    source: "IJCAI 2024 graph meets LLM survey",
    href: "https://www.ijcai.org/proceedings/2024/898",
    finding:
      "The research field is converging on bidirectional KG/LLM systems: LLMs help build and query graphs, while graphs constrain and enrich LLM reasoning.",
    dialecticaUse:
      "The LLM proposes structure; the graph validates, stores, temporalizes, and retrieves it for repeated policy workflows.",
  },
  {
    title: "Neurosymbolic reasoning over KGs",
    source: "IEEE TNNLS survey / University of Edinburgh",
    href: "https://www.pure.ed.ac.uk/ws/portalfiles/portal/466402539/DeLongEtalArXiv2024NeurosymbolicAIForReasoning.pdf",
    finding:
      "Neurosymbolic systems combine learned representations with symbolic structure and rules for reasoning over knowledge graphs.",
    dialecticaUse:
      "Policy claims need neural extraction plus symbolic checks: provenance required, no orphan claims, explicit causality, confidence, and review queues.",
  },
  {
    title: "Temporal KG reasoning",
    source: "Temporal KG + LLM research",
    href: "https://www.sciencedirect.com/science/article/pii/S0950705125011396",
    finding:
      "Temporal knowledge graph reasoning research combines rules, graph modeling, and LLMs to reason over validity, time windows, and evolving facts.",
    dialecticaUse:
      "Syria, sanctions, and negotiations change over time; Dialectica represents reporting windows, valid_from/valid_to, episodes, and changed_since.",
  },
  {
    title: "Policy compliance as graph reasoning",
    source: "Policy compliance KG research",
    href: "https://papers.cool/arxiv/2604.27713",
    finding:
      "Emerging work uses knowledge graphs built from policy documents to retrieve relevant policy structure for compliance questions.",
    dialecticaUse:
      "Sanctions, procurement, humanitarian exceptions, reconstruction finance, and internal policy rules become queryable constraints and review checks.",
  },
];

const policyDomainBenefits = [
  {
    domain: "Statecraft and diplomacy",
    problem: "Policy teams need to know who has leverage, which options are blocked, and what changed after each reporting window.",
    graphHelp: "Actor -> Leverage -> Constraint -> PolicyOption, with source_ids, temporal validity, and confidence.",
  },
  {
    domain: "Sanctions and reconstruction",
    problem: "Legal authorization, bank behavior, political conditionality, and beneficiary risk are different mechanisms that ordinary summaries blur.",
    graphHelp: "Authority -> License -> AuthorizedActivity -> ComplianceBoundary -> CapitalFlow -> BeneficiaryRisk.",
  },
  {
    domain: "Conflict mediation",
    problem: "Positions, interests, commitments, trust injuries, guarantees, and sequencing need to be separated before drafting a process plan.",
    graphHelp: "Actor -> Interest -> Commitment -> TrustState -> Guarantee -> ImplementationRisk.",
  },
  {
    domain: "Internal policy drafting",
    problem: "Drafts need traceable claims, red-team review, assumptions, source spans, and review owners.",
    graphHelp: "Document -> EvidenceSpan -> Claim -> ReviewFlag -> DraftPacket -> DecisionMemo.",
  },
];

export default function HomePage() {
  return (
    <div className="space-y-6">
      <section className="min-h-[calc(100vh-7rem)] rounded-lg border border-border bg-surface p-5">
        <div className="grid min-h-[calc(100vh-10rem)] gap-8 xl:grid-cols-[0.92fr_1.08fr]">
          <div className="flex flex-col justify-center">
            <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-accent">
              <Shield size={15} />
              DIALECTICA by TACITUS
            </div>
            <h1 className="mt-4 max-w-4xl text-4xl font-semibold leading-tight text-text-primary xl:text-5xl">
              Build live situation graphs from sources, not just summaries.
            </h1>
            <p className="mt-5 max-w-3xl text-base leading-7 text-text-secondary">
              Dialectica is a backend and operator surface for turning documents, reports, books, and live
              cases into structured knowledge: ontology-grounded objects, temporal episodes, causal mechanisms,
              provenance traces, graph reasoning, and benchmarkable answers.
            </p>
            <div className="mt-7 flex flex-wrap gap-3">
              <Link href="/situation-demo" className="btn-primary inline-flex items-center gap-2 px-5 py-3">
                Open Situation Demo
                <ArrowRight size={16} />
              </Link>
              <Link href="/graphops" className="btn-secondary inline-flex items-center gap-2 px-5 py-3">
                Open GraphOps
                <Workflow size={16} />
              </Link>
            </div>
            <div className="mt-7 grid gap-3 sm:grid-cols-2">
              {proofPoints.map((item) => (
                <div key={item.label} className="rounded-lg border border-border bg-background p-4">
                  <p className="text-[11px] font-semibold uppercase tracking-wide text-text-secondary">{item.label}</p>
                  <p className="mt-2 text-sm font-semibold text-text-primary">{item.value}</p>
                  <p className="mt-1 text-xs leading-5 text-text-secondary">{item.detail}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="flex min-h-[520px] flex-col justify-center">
            <div className="relative min-h-[520px] overflow-hidden rounded-lg border border-border bg-background">
              <div className="absolute inset-x-0 top-0 border-b border-border bg-surface/80 px-4 py-3">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="text-sm font-semibold text-text-primary">Situation graph runtime</p>
                  <span className="rounded-md bg-emerald-500/10 px-2 py-1 text-[11px] text-emerald-200">
                    live app + API
                  </span>
                </div>
              </div>
              <div className="absolute inset-0 pt-14">
                <div className="absolute inset-0 opacity-40">
                  <div className="h-full w-full bg-[linear-gradient(rgba(51,65,85,0.45)_1px,transparent_1px),linear-gradient(90deg,rgba(51,65,85,0.45)_1px,transparent_1px)] bg-[size:42px_42px]" />
                </div>
                <svg className="absolute inset-0 h-full w-full" aria-hidden="true">
                  {graphEdges.map(([from, to]) => {
                    const source = graphNodes.find((node) => node.label === from);
                    const target = graphNodes.find((node) => node.label === to);
                    if (!source || !target) return null;
                    return (
                      <line
                        key={`${from}-${to}`}
                        x1={source.x}
                        y1={source.y}
                        x2={target.x}
                        y2={target.y}
                        className="dialectica-graph-edge"
                      />
                    );
                  })}
                </svg>
                {graphNodes.map((node, index) => (
                  <div
                    key={node.label}
                    className="dialectica-graph-node absolute w-32 rounded-lg border border-border bg-surface p-3 md:w-40"
                    style={{ left: node.x, top: node.y, animationDelay: `${index * 0.22}s` }}
                  >
                    <div className="flex items-center gap-2">
                      <span className={`h-3 w-3 rounded-full ${node.tone}`} />
                      <p className="text-sm font-semibold text-text-primary">{node.label}</p>
                    </div>
                    <p className="mt-2 text-[11px] leading-4 text-text-secondary">{node.detail}</p>
                  </div>
                ))}
              </div>
              <div className="absolute bottom-4 left-4 right-4 grid gap-2 md:grid-cols-4">
                {["source_ids", "valid_time", "confidence", "changed_since"].map((item) => (
                  <code key={item} className="rounded-md border border-border bg-background/90 px-2 py-2 text-[11px] text-accent">
                    {item}
                  </code>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="rounded-lg border border-accent/30 bg-accent/10 p-5">
        <div className="flex flex-col justify-between gap-4 xl:flex-row xl:items-start">
          <div>
            <h2 className="flex items-center gap-2 text-xl font-semibold text-text-primary">
              <Zap size={20} className="text-accent" />
              Demo Readiness Path
            </h2>
            <p className="mt-2 max-w-4xl text-sm leading-6 text-text-secondary">
              The app is now organized for a clean recording: landing page, Situation Demo, GraphOps,
              backend health, and benchmark proof all point to the same product narrative.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <Link href="/situation-demo" className="btn-primary inline-flex items-center gap-2">
              Start Demo Path
              <ArrowRight size={15} />
            </Link>
            <Link href="/admin/graph-health" className="btn-secondary inline-flex items-center gap-2">
              Check Health
              <Shield size={15} />
            </Link>
          </div>
        </div>
        <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          {demoReadiness.map((item, index) => (
            <div key={item.step} className="rounded-lg border border-border bg-background p-4">
              <p className="text-xs font-semibold text-accent">Step {index + 1}</p>
              <p className="mt-2 text-sm font-semibold text-text-primary">{item.step}</p>
              <p className="mt-2 text-xs leading-5 text-text-secondary">{item.proof}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-lg border border-border bg-surface p-5">
        <div className="flex flex-col justify-between gap-3 lg:flex-row lg:items-center">
          <div>
            <h2 className="flex items-center gap-2 text-xl font-semibold text-text-primary">
              <Network size={20} className="text-accent" />
              What The Real App Does
            </h2>
            <p className="mt-2 max-w-4xl text-sm leading-6 text-text-secondary">
              Dialectica is not a landing-page concept. The deployed app already exposes a GraphOps console,
              a situation demo, API health, ingestion controls, graph search, actor reasoning, public configs,
              and a graph reasoning stack designed for Cloud Run.
            </p>
          </div>
          <Link href="/situation-demo" className="btn-secondary inline-flex items-center gap-2">
            See the live demo
            <ArrowRight size={15} />
          </Link>
        </div>
        <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {capabilities.map((item) => {
            const Icon = item.icon;
            return (
              <div key={item.title} className="rounded-lg border border-border bg-background p-4">
                <div className="flex items-center gap-3">
                  <div className="rounded-md bg-accent/10 p-2 text-accent">
                    <Icon size={17} />
                  </div>
                  <p className="text-sm font-semibold text-text-primary">{item.title}</p>
                </div>
                <p className="mt-3 text-xs leading-5 text-text-secondary">{item.detail}</p>
              </div>
            );
          })}
        </div>
      </section>

      <section className="rounded-lg border border-border bg-surface p-5">
        <div className="flex flex-col justify-between gap-3 lg:flex-row lg:items-start">
          <div>
            <h2 className="flex items-center gap-2 text-xl font-semibold text-text-primary">
              <Brain size={20} className="text-accent" />
              Research Wave: Neurosymbolic Graph + LLM Systems
            </h2>
            <p className="mt-2 max-w-5xl text-sm leading-6 text-text-secondary">
              The technical case for Dialectica is no longer speculative. GraphRAG, KG-augmented LLMs,
              neurosymbolic reasoning, temporal knowledge graphs, and policy-compliance retrieval are converging
              on the same architecture: neural extraction and explanation, symbolic graph structure, explicit
              provenance, temporal validity, and deterministic checks for questions that ordinary chat summaries
              cannot reliably audit.
            </p>
          </div>
          <Link href="/situation-demo#benchmarks" className="btn-secondary inline-flex items-center gap-2">
            See benchmark view
            <BarChart3 size={15} />
          </Link>
        </div>
        <div className="mt-5 grid gap-4 xl:grid-cols-3">
          {researchWave.map((item) => (
            <article key={item.title} className="rounded-lg border border-border bg-background p-4">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h3 className="text-sm font-semibold text-text-primary">{item.title}</h3>
                  <a
                    href={item.href}
                    target="_blank"
                    rel="noreferrer"
                    className="mt-1 inline-flex items-center gap-1 text-[11px] font-semibold text-accent hover:text-accent-strong"
                  >
                    {item.source}
                    <ExternalLink size={12} />
                  </a>
                </div>
                <span className="rounded-md bg-accent/10 px-2 py-1 text-[10px] font-semibold uppercase tracking-wide text-accent">
                  research
                </span>
              </div>
              <p className="mt-3 text-xs leading-5 text-text-secondary">{item.finding}</p>
              <div className="mt-4 rounded-lg border border-accent/20 bg-accent/10 p-3">
                <p className="text-[11px] font-semibold uppercase tracking-wide text-accent">Dialectica use</p>
                <p className="mt-2 text-xs leading-5 text-text-secondary">{item.dialecticaUse}</p>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[0.85fr_1.15fr]">
        <div className="rounded-lg border border-border bg-surface p-5">
          <h2 className="flex items-center gap-2 text-xl font-semibold text-text-primary">
            <Shield size={20} className="text-accent" />
            Policy Design Principle
          </h2>
          <p className="mt-2 text-sm leading-6 text-text-secondary">
            In policy work, the LLM should not become the database. It should propose entities, relations,
            causal mechanisms, review questions, and draft language. The graph stores the commitments,
            evidence, timestamps, source_ids, confidence, and constraints. Rule queries then test whether an
            answer is traceable, temporally valid, and operationally useful.
          </p>
          <div className="mt-5 grid gap-2">
            {[
              "LLM extracts candidates from sources and explains candidate graph paths.",
              "Neo4j stores the operational graph and every provenance-bearing object.",
              "Graphiti preserves temporal episodes, source episodes, and memory evolution.",
              "Cozo answers deterministic reasoning questions over a read-optimized mirror.",
              "PRAXIS can draft memos, briefs, and plans from traceable graph packets.",
            ].map((item) => (
              <div key={item} className="flex items-start gap-3 rounded-lg border border-border bg-background p-3">
                <CheckCircle2 size={15} className="mt-0.5 shrink-0 text-emerald-300" />
                <p className="text-sm leading-5 text-text-secondary">{item}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-lg border border-border bg-surface p-5">
          <h2 className="flex items-center gap-2 text-xl font-semibold text-text-primary">
            <Globe2 size={20} className="text-accent" />
            Why This Matters In Policy Domains
          </h2>
          <p className="mt-2 text-sm leading-6 text-text-secondary">
            These domains share the same failure mode: the useful answer depends on structured relationships,
            time, evidence, and mechanisms. Dialectica makes those structures explicit before the model drafts.
          </p>
          <div className="mt-5 grid gap-3 md:grid-cols-2">
            {policyDomainBenefits.map((item) => (
              <div key={item.domain} className="rounded-lg border border-border bg-background p-4">
                <p className="text-sm font-semibold text-text-primary">{item.domain}</p>
                <p className="mt-2 text-xs leading-5 text-text-secondary">{item.problem}</p>
                <code className="mt-3 block rounded-md bg-surface px-2 py-2 text-[11px] leading-5 text-accent">
                  {item.graphHelp}
                </code>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
        <div className="rounded-lg border border-border bg-surface p-5">
          <h2 className="flex items-center gap-2 text-xl font-semibold text-text-primary">
            <Workflow size={20} className="text-accent" />
            The Backbone Flow
          </h2>
          <p className="mt-2 text-sm leading-6 text-text-secondary">
            The pipeline is deterministic where it must be: stable IDs, required provenance, time fields,
            canonical relations, validation, and reproducible reasoning. AI is used to propose structure,
            extract candidates, explain graph paths, and generate benchmark questions.
          </p>
          <div className="mt-5 grid gap-2">
            {productFlow.map((step, index) => (
              <div key={step} className="flex items-center gap-3 rounded-lg border border-border bg-background p-3">
                <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-accent/10 text-xs font-semibold text-accent">
                  {index + 1}
                </span>
                <p className="text-sm text-text-primary">{step}</p>
                {index < productFlow.length - 1 && <ArrowRight size={14} className="ml-auto text-text-secondary" />}
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-lg border border-border bg-surface p-5">
          <h2 className="flex items-center gap-2 text-xl font-semibold text-text-primary">
            <Database size={20} className="text-accent" />
            Graph And Reasoning Stack
          </h2>
          <p className="mt-2 text-sm leading-6 text-text-secondary">
            The app is structured as a real backend: operational graph, temporal memory, reasoning mirror,
            audit database, analytics layer, and product APIs. Each part has a clear job.
          </p>
          <div className="mt-5 grid gap-3 md:grid-cols-2">
            {stack.map((item) => {
              const Icon = item.icon;
              return (
                <div key={item.name} className="rounded-lg border border-border bg-background p-4">
                  <div className="flex items-center gap-2">
                    <Icon size={16} className="text-accent" />
                    <p className="text-sm font-semibold text-text-primary">{item.name}</p>
                  </div>
                  <p className="mt-2 text-xs leading-5 text-text-secondary">{item.role}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      <section className="rounded-lg border border-border bg-surface p-5">
        <h2 className="flex items-center gap-2 text-xl font-semibold text-text-primary">
          <Globe2 size={20} className="text-accent" />
          Demo Tracks
        </h2>
        <p className="mt-2 max-w-4xl text-sm leading-6 text-text-secondary">
          The landing page now points to the actual demo paths. Syria proves policy/statecraft and sanctions
          reasoning. Gutenberg books prove long-text conflict structure. GraphOps proves the operating console.
        </p>
        <div className="mt-5 grid gap-4 xl:grid-cols-3">
          {demoTracks.map((track) => {
            const Icon = track.icon;
            return (
              <Link
                key={track.title}
                href={track.href}
                className="rounded-lg border border-border bg-background p-5 transition-colors hover:border-border-hover hover:bg-surface-hover"
              >
                <div className="flex items-center gap-3">
                  <div className="rounded-md bg-accent/10 p-2 text-accent">
                    <Icon size={18} />
                  </div>
                  <p className="text-sm font-semibold text-text-primary">{track.title}</p>
                </div>
                <p className="mt-3 text-xs leading-5 text-text-secondary">{track.detail}</p>
                <div className="mt-4 flex flex-wrap gap-2">
                  {track.queries.map((query) => (
                    <span key={query} className="rounded-md bg-surface px-2 py-1 text-[11px] text-text-secondary">
                      {query}
                    </span>
                  ))}
                </div>
              </Link>
            );
          })}
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
        <div className="rounded-lg border border-border bg-surface p-5">
          <h2 className="flex items-center gap-2 text-xl font-semibold text-text-primary">
            <GitBranch size={20} className="text-accent" />
            Dynamic Ontologies
          </h2>
          <p className="mt-2 text-sm leading-6 text-text-secondary">
            Users should not write boilerplate schemas for every case. Dialectica lets domain-specific
            ontologies compile back into a canonical graph contract, so search, provenance, reasoning, and
            benchmarks still work across cases.
          </p>
          <div className="mt-5 grid gap-3 md:grid-cols-2">
            {ontologyExamples.map((item) => (
              <div key={item.domain} className="rounded-lg border border-border bg-background p-4">
                <p className="text-sm font-semibold text-text-primary">{item.domain}</p>
                <code className="mt-3 block rounded-md bg-surface px-2 py-1 text-[11px] leading-5 text-accent">
                  {item.structure}
                </code>
                <p className="mt-3 text-xs leading-5 text-text-secondary">{item.use}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-lg border border-border bg-surface p-5">
          <h2 className="flex items-center gap-2 text-xl font-semibold text-text-primary">
            <Search size={20} className="text-accent" />
            Questions It Makes Answerable
          </h2>
          <div className="mt-4 space-y-3">
            {[
              "Who has leverage over a situation, and through which mechanism?",
              "What changed since the last source run or reporting window?",
              "Which causal claims are evidence-backed and which need human review?",
              "What does a source prove, and what is only interpretation?",
              "Which policy option is blocked by sanctions, legitimacy, security, or implementation risk?",
              "How does a book scene or historical episode transform a character's commitments?",
            ].map((question) => (
              <div key={question} className="flex items-start gap-3 rounded-lg border border-border bg-background p-3">
                <CheckCircle2 size={15} className="mt-0.5 shrink-0 text-emerald-300" />
                <p className="text-sm leading-5 text-text-secondary">{question}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="rounded-lg border border-accent/30 bg-accent/10 p-5">
        <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-center">
          <div>
            <h2 className="text-xl font-semibold text-text-primary">Start with the working demo.</h2>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-text-secondary">
              The strongest first click is the Situation Demo. It shows the product promise, the real graph
              stack, the Syria case, Gutenberg examples, D3 visualization, configuration handoff, and live API controls.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <Link href="/situation-demo" className="btn-primary inline-flex items-center gap-2">
              Launch Demo
              <ArrowRight size={15} />
            </Link>
            <Link href="/developers/docs" className="btn-secondary inline-flex items-center gap-2">
              API Docs
              <BookOpen size={15} />
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
