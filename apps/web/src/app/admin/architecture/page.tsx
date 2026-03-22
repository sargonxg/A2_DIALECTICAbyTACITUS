"use client";

import { useState } from "react";
import {
  Layers,
  Brain,
  Database,
  Zap,
  Users,
  ArrowRight,
  ArrowDown,
  Package,
  BookOpen,
  Shield,
  ExternalLink,
  ChevronDown,
  ChevronRight,
  CheckCircle2,
  XCircle,
  AlertTriangle,
} from "lucide-react";
import { NODE_COLORS } from "@/lib/utils";

/* ------------------------------------------------------------------ */
/*  Architecture layers                                                */
/* ------------------------------------------------------------------ */

const LAYERS = [
  {
    number: 1,
    name: "Neural Ingestion",
    subtitle: "From unstructured text to validated entities",
    color: "#3b82f6",
    icon: Brain,
    steps: [
      { name: "GLiNER NER", detail: "Named entity recognition pre-filter — identifies candidate conflict entities before LLM extraction" },
      { name: "Gemini 2.5 Flash", detail: "Structured extraction via Google Gemini — maps text to Conflict Grammar ontology with confidence scores" },
      { name: "Pydantic Validation", detail: "v2 strict validation with discriminated unions — ensures every extracted entity matches the ontology schema" },
    ],
  },
  {
    number: 2,
    name: "Symbolic Representation",
    subtitle: "Knowledge graph with conflict-specific semantics",
    color: "#6366f1",
    icon: Database,
    steps: [
      { name: "Conflict Grammar", detail: "Domain ontology with 15 node types, 20 edge types, and 25+ controlled vocabularies" },
      { name: "Neo4j Graph", detail: "Primary graph store in Neo4j Aura — TACITUS is in the Neo4j Startup Program" },
      { name: "15 Node Types, 20 Edge Types", detail: "actor, conflict, event, issue, interest, norm, process, outcome, narrative, emotional_state, trust_state, power_dynamic, location, evidence, role" },
    ],
  },
  {
    number: 3,
    name: "Reasoning & Inference",
    subtitle: "Deterministic rules fire FIRST, neural fills gaps",
    color: "#f59e0b",
    icon: Zap,
    steps: [
      { name: "25+ Symbolic Rules", detail: "Deterministic rules for escalation detection, ripeness assessment, trust dynamics, power analysis, and treaty violations" },
      { name: "GNN/KGE Neural", detail: "Graph Neural Networks and Knowledge Graph Embeddings for link prediction and pattern discovery" },
      { name: "Human Validates", detail: "All neural predictions flagged as 'probabilistic' — analysts review and confirm before conclusions become authoritative" },
    ],
  },
  {
    number: 4,
    name: "Decision Support",
    subtitle: "AI agents grounded in conflict theory",
    color: "#10b981",
    icon: Users,
    steps: [
      { name: "6 AI Agents", detail: "Analyst, Advisor, Comparator, Forecaster, Mediator, Theorist — each specialized for different conflict analysis tasks" },
      { name: "MCP Server", detail: "Model Context Protocol server — lets Claude Desktop interact directly with DIALECTICA knowledge graphs" },
    ],
  },
];

/* ------------------------------------------------------------------ */
/*  Package dependency graph                                           */
/* ------------------------------------------------------------------ */

const PACKAGES = [
  { name: "ontology", desc: "Pydantic models, enums, symbolic rules, theory", deps: [], color: "#6366f1" },
  { name: "graph", desc: "Neo4j client, FalkorDB adapter, graph interface", deps: ["ontology"], color: "#3b82f6" },
  { name: "extraction", desc: "GLiNER + Gemini pipeline, 10-step LangGraph DAG", deps: ["ontology", "graph"], color: "#f59e0b" },
  { name: "reasoning", desc: "Symbolic rules, GNN/KGE, 6 AI agents", deps: ["ontology", "graph", "extraction"], color: "#10b981" },
  { name: "api", desc: "FastAPI app, 14 routers, auth, tenant isolation", deps: ["ontology", "graph", "extraction", "reasoning"], color: "#f43f5e" },
];

const CONSUMERS = [
  { name: "apps/web", desc: "Next.js 15 frontend", color: "#14b8a6" },
  { name: "packages/mcp", desc: "MCP server for Claude", color: "#a855f7" },
  { name: "packages/sdk-typescript", desc: "TypeScript SDK", color: "#ec4899" },
];

/* ------------------------------------------------------------------ */
/*  15 theories                                                        */
/* ------------------------------------------------------------------ */

const THEORY_GROUPS = [
  {
    category: "Escalation & Dynamics",
    color: "#f43f5e",
    theories: [
      { id: "glasl", name: "Glasl Escalation Model", author: "Friedrich Glasl", use: "9-stage escalation tracking — determines intervention type based on conflict stage" },
      { id: "kriesberg", name: "Conflict Lifecycle", author: "Louis Kriesberg", use: "Maps emergence, escalation, de-escalation, and termination phases" },
      { id: "zartman", name: "Ripeness Theory", author: "I. William Zartman", use: "Detects Mutually Hurting Stalemate and readiness for negotiation" },
    ],
  },
  {
    category: "Negotiation & Resolution",
    color: "#14b8a6",
    theories: [
      { id: "fisher_ury", name: "Principled Negotiation", author: "Fisher & Ury", use: "Interest mapping, BATNA assessment, ZOPA identification" },
      { id: "thomas_kilmann", name: "Conflict Modes", author: "Thomas & Kilmann", use: "Classifies strategies: competing, collaborating, compromising, avoiding, accommodating" },
      { id: "ury_brett_goldberg", name: "Dispute Systems Design", author: "Ury, Brett & Goldberg", use: "Evaluates dispute resolution systems: interests, rights, and power-based approaches" },
      { id: "winslade_monk", name: "Narrative Mediation", author: "Winslade & Monk", use: "Analyzes dominant narratives and counter-stories shaping conflict perceptions" },
    ],
  },
  {
    category: "Structural & Cultural",
    color: "#6366f1",
    theories: [
      { id: "galtung", name: "Violence Triangle", author: "Johan Galtung", use: "Distinguishes direct, structural, and cultural violence dimensions" },
      { id: "lederach", name: "Peacebuilding", author: "John Paul Lederach", use: "Multi-track diplomacy and long-term transformation frameworks" },
      { id: "burton", name: "Basic Human Needs", author: "John Burton", use: "Links conflict to unmet identity, security, recognition, and participation needs" },
      { id: "deutsch", name: "Cooperation & Competition", author: "Morton Deutsch", use: "Models constructive vs. destructive conflict dynamics" },
    ],
  },
  {
    category: "Relational & Emotional",
    color: "#f59e0b",
    theories: [
      { id: "french_raven", name: "Bases of Power", author: "French & Raven", use: "Classifies power: legitimate, reward, coercive, expert, referent, informational" },
      { id: "mayer_trust", name: "Trust Model", author: "Mayer, Davis & Schoorman", use: "Tracks trust via ability, benevolence, and integrity dimensions" },
      { id: "plutchik", name: "Emotion Wheel", author: "Robert Plutchik", use: "Maps 8 primary emotions and their combinations to conflict behavior" },
      { id: "pearl_causal", name: "Causal Inference", author: "Judea Pearl", use: "do-calculus for counterfactual reasoning over conflict causes and effects" },
    ],
  },
];

/* ------------------------------------------------------------------ */
/*  Page                                                               */
/* ------------------------------------------------------------------ */

export default function ArchitecturePage() {
  const [expandedLayer, setExpandedLayer] = useState<number | null>(1);
  const [expandedSection, setExpandedSection] = useState<string>("layers");

  const toggleSection = (section: string) => {
    setExpandedSection((prev) => (prev === section ? "" : section));
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-text-primary flex items-center gap-2">
          <Layers size={20} className="text-accent" />
          Backend Architecture
        </h2>
        <a
          href="https://tacitus.me"
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs text-text-secondary hover:text-accent transition-colors flex items-center gap-1"
        >
          tacitus.me <ExternalLink size={10} />
        </a>
      </div>

      <p className="text-sm text-text-secondary max-w-3xl">
        DIALECTICA uses a 4-layer neurosymbolic architecture where deterministic symbolic
        conclusions are never overridden by probabilistic neural predictions. This is the
        core invariant of the system, enforced via confidence_type tagging.
      </p>

      {/* ---- 4-Layer Architecture ---- */}
      <div className="card space-y-4">
        <button
          onClick={() => toggleSection("layers")}
          className="w-full flex items-center justify-between"
        >
          <h3 className="font-semibold text-text-primary flex items-center gap-2">
            <Layers size={16} className="text-accent" />
            4-Layer Neurosymbolic Pipeline
          </h3>
          {expandedSection === "layers" ? (
            <ChevronDown size={16} className="text-text-secondary" />
          ) : (
            <ChevronRight size={16} className="text-text-secondary" />
          )}
        </button>

        {expandedSection === "layers" && (
          <div className="space-y-2">
            {LAYERS.map((layer, li) => {
              const LayerIcon = layer.icon;
              const isExpanded = expandedLayer === layer.number;
              return (
                <div key={layer.number}>
                  <button
                    onClick={() => setExpandedLayer(isExpanded ? null : layer.number)}
                    className="w-full rounded-lg border p-4 text-left transition-all hover:border-border-hover"
                    style={{
                      borderColor: isExpanded ? `${layer.color}40` : undefined,
                      backgroundColor: isExpanded ? `${layer.color}08` : undefined,
                    }}
                  >
                    <div className="flex items-center gap-4">
                      <div
                        className="w-12 h-12 rounded-lg flex items-center justify-center shrink-0 font-bold text-lg"
                        style={{ backgroundColor: `${layer.color}20`, color: layer.color }}
                      >
                        {layer.number}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <LayerIcon size={14} style={{ color: layer.color }} />
                          <h4 className="font-semibold text-text-primary">{layer.name}</h4>
                        </div>
                        <p className="text-xs text-text-secondary mt-0.5">{layer.subtitle}</p>
                      </div>
                      {isExpanded ? (
                        <ChevronDown size={16} className="text-text-secondary shrink-0" />
                      ) : (
                        <ChevronRight size={16} className="text-text-secondary shrink-0" />
                      )}
                    </div>

                    {isExpanded && (
                      <div className="mt-4 space-y-3 pl-16">
                        {layer.steps.map((step, si) => (
                          <div key={step.name}>
                            <div className="flex items-start gap-3">
                              <div
                                className="w-6 h-6 rounded-full flex items-center justify-center shrink-0 text-[10px] font-bold mt-0.5"
                                style={{ backgroundColor: `${layer.color}20`, color: layer.color }}
                              >
                                {si + 1}
                              </div>
                              <div>
                                <p className="text-sm font-medium text-text-primary">{step.name}</p>
                                <p className="text-xs text-text-secondary leading-relaxed mt-0.5">
                                  {step.detail}
                                </p>
                              </div>
                            </div>
                            {si < layer.steps.length - 1 && (
                              <div className="flex justify-start pl-3 py-1">
                                <ArrowDown size={12} className="text-text-secondary/30" />
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </button>

                  {li < LAYERS.length - 1 && (
                    <div className="flex justify-center py-1">
                      <ArrowDown size={14} className="text-text-secondary/30" />
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* ---- Neurosymbolic Firewall ---- */}
      <div className="card space-y-4">
        <button
          onClick={() => toggleSection("firewall")}
          className="w-full flex items-center justify-between"
        >
          <h3 className="font-semibold text-text-primary flex items-center gap-2">
            <Shield size={16} className="text-danger" />
            Neurosymbolic Firewall
          </h3>
          {expandedSection === "firewall" ? (
            <ChevronDown size={16} className="text-text-secondary" />
          ) : (
            <ChevronRight size={16} className="text-text-secondary" />
          )}
        </button>

        {expandedSection === "firewall" && (
          <div className="space-y-4">
            <p className="text-sm text-text-secondary">
              The critical invariant: deterministic symbolic conclusions are{" "}
              <span className="text-danger font-semibold">NEVER</span> overridden by probabilistic neural predictions.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Deterministic */}
              <div className="rounded-lg border border-success/20 bg-success/5 p-4 space-y-3">
                <div className="flex items-center gap-2">
                  <CheckCircle2 size={16} className="text-success" />
                  <h4 className="font-semibold text-text-primary text-sm">Deterministic (Symbolic)</h4>
                </div>
                <p className="text-xs text-text-secondary">
                  confidence_type = &quot;deterministic&quot;
                </p>
                <ul className="space-y-1.5">
                  {[
                    "Treaty violation detection",
                    "Legal constraint identification",
                    "Glasl stage derivation from events",
                    "Ripeness assessment (MHS/MEO)",
                    "Power base classification",
                    "Trust dimension scoring",
                  ].map((item) => (
                    <li key={item} className="text-xs text-text-secondary flex gap-2">
                      <CheckCircle2 size={10} className="text-success shrink-0 mt-0.5" />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Probabilistic */}
              <div className="rounded-lg border border-warning/20 bg-warning/5 p-4 space-y-3">
                <div className="flex items-center gap-2">
                  <AlertTriangle size={16} className="text-warning" />
                  <h4 className="font-semibold text-text-primary text-sm">Probabilistic (Neural)</h4>
                </div>
                <p className="text-xs text-text-secondary">
                  confidence_type = &quot;probabilistic&quot;
                </p>
                <ul className="space-y-1.5">
                  {[
                    "GNN link predictions",
                    "KGE embedding similarities",
                    "LLM-generated analysis",
                    "Community detection clusters",
                    "Sentiment scoring",
                    "Entity disambiguation",
                  ].map((item) => (
                    <li key={item} className="text-xs text-text-secondary flex gap-2">
                      <AlertTriangle size={10} className="text-warning shrink-0 mt-0.5" />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="rounded-lg border border-danger/20 bg-danger/5 p-3 flex items-start gap-3">
              <XCircle size={16} className="text-danger shrink-0 mt-0.5" />
              <div>
                <p className="text-sm text-text-primary font-semibold">Firewall Rule</p>
                <p className="text-xs text-text-secondary mt-1">
                  If a symbolic rule produces a deterministic conclusion (e.g., &quot;Glasl Stage 5 based on
                  loss-of-face events&quot;), no neural model can override it. The neural layer can only
                  fill gaps where no symbolic rule fires.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* ---- Package Dependency Graph ---- */}
      <div className="card space-y-4">
        <button
          onClick={() => toggleSection("packages")}
          className="w-full flex items-center justify-between"
        >
          <h3 className="font-semibold text-text-primary flex items-center gap-2">
            <Package size={16} className="text-accent" />
            Package Dependency Graph
          </h3>
          {expandedSection === "packages" ? (
            <ChevronDown size={16} className="text-text-secondary" />
          ) : (
            <ChevronRight size={16} className="text-text-secondary" />
          )}
        </button>

        {expandedSection === "packages" && (
          <div className="space-y-4">
            {/* Core packages */}
            <div className="space-y-2">
              <p className="text-xs text-text-secondary font-semibold uppercase tracking-wider">Core Pipeline</p>
              <div className="flex flex-wrap items-center gap-2">
                {PACKAGES.map((pkg, i) => (
                  <div key={pkg.name} className="flex items-center gap-2">
                    <div
                      className="rounded-lg border px-3 py-2 min-w-[120px]"
                      style={{ borderColor: `${pkg.color}40`, backgroundColor: `${pkg.color}08` }}
                    >
                      <p className="text-sm font-mono font-semibold" style={{ color: pkg.color }}>
                        {pkg.name}
                      </p>
                      <p className="text-[10px] text-text-secondary mt-0.5">{pkg.desc}</p>
                    </div>
                    {i < PACKAGES.length - 1 && (
                      <ArrowRight size={14} className="text-text-secondary/30 shrink-0" />
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Consumers */}
            <div className="space-y-2">
              <p className="text-xs text-text-secondary font-semibold uppercase tracking-wider">
                Consumers (depend on api)
              </p>
              <div className="flex flex-wrap gap-2">
                {CONSUMERS.map((c) => (
                  <div
                    key={c.name}
                    className="rounded-lg border px-3 py-2"
                    style={{ borderColor: `${c.color}40`, backgroundColor: `${c.color}08` }}
                  >
                    <p className="text-sm font-mono font-semibold" style={{ color: c.color }}>
                      {c.name}
                    </p>
                    <p className="text-[10px] text-text-secondary mt-0.5">{c.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* ---- Theoretical Foundations ---- */}
      <div className="card space-y-4">
        <button
          onClick={() => toggleSection("theories")}
          className="w-full flex items-center justify-between"
        >
          <h3 className="font-semibold text-text-primary flex items-center gap-2">
            <BookOpen size={16} className="text-accent" />
            Theoretical Foundations — 15 Frameworks
          </h3>
          {expandedSection === "theories" ? (
            <ChevronDown size={16} className="text-text-secondary" />
          ) : (
            <ChevronRight size={16} className="text-text-secondary" />
          )}
        </button>

        {expandedSection === "theories" && (
          <div className="space-y-6">
            {THEORY_GROUPS.map((group) => (
              <div key={group.category} className="space-y-2">
                <div className="flex items-center gap-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: group.color }}
                  />
                  <h4 className="text-sm font-semibold text-text-primary">{group.category}</h4>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2 pl-5">
                  {group.theories.map((theory) => (
                    <div
                      key={theory.id}
                      className="bg-background rounded-lg border border-border p-3 space-y-1"
                    >
                      <p className="text-sm font-medium text-text-primary">{theory.name}</p>
                      <p className="text-[10px] text-text-secondary font-medium">{theory.author}</p>
                      <p className="text-xs text-text-secondary leading-relaxed">{theory.use}</p>
                    </div>
                  ))}
                </div>
              </div>
            ))}
            <div className="text-center">
              <a
                href="/theory"
                className="btn-secondary inline-flex items-center gap-2 text-xs"
              >
                <BookOpen size={12} />
                View Full Theory Framework Details
                <ArrowRight size={12} />
              </a>
            </div>
          </div>
        )}
      </div>

      {/* ---- Footer ---- */}
      <div className="text-center text-xs text-text-secondary/50 pt-4 border-t border-border">
        DIALECTICA by{" "}
        <a
          href="https://tacitus.me"
          target="_blank"
          rel="noopener noreferrer"
          className="text-accent hover:text-accent-hover transition-colors"
        >
          TACITUS
        </a>{" "}
        — Neurosymbolic Conflict Intelligence
      </div>
    </div>
  );
}
