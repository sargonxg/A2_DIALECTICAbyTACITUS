"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import * as d3 from "d3";
import {
  Activity,
  ArrowRight,
  BarChart3,
  BookOpen,
  Brain,
  CheckCircle2,
  Clipboard,
  Cpu,
  Database,
  ExternalLink,
  FileCode,
  FileJson,
  FileText,
  GitBranch,
  Globe2,
  KeyRound,
  Layers,
  Network,
  Play,
  Route,
  Search,
  ServerCog,
  Settings2,
  Shield,
  Timer,
  Zap,
  Workflow,
} from "lucide-react";
import { getApiUrl } from "@/lib/config";
import { sampleText } from "@/lib/graphopsExtraction";

const WORKSPACE_ID = "syria-transition-demo";
const CASE_ID = "syria-transition-2026";
const OBJECTIVE =
  "Map Syria's transition as a source-grounded graph: actors, claims, constraints, leverage, events, humanitarian risks, external patrons, and unresolved verification questions.";
const SYRIA_TEXT = sampleText("syria-transition-2026") ?? "";

const sources = [
  {
    label: "UN Geneva, Jan. 22 2026",
    url: "https://www.ungeneva.org/en/news-media/news/2026/01/115115/syria-renewed-clashes-risk-derailing-fragile-transition",
    use: "Fragile transition, renewed clashes, humanitarian exposure.",
  },
  {
    label: "UN Geneva, Feb. 2026",
    url: "https://www.ungeneva.org/fr/news-media/news/2026/02/115852/la-transition-en-syrie-progresse-mais-la-violence-et-la-crise",
    use: "Transition momentum, Kurdish/SDF deal, violence and humanitarian risk.",
  },
  {
    label: "Security Council Report, May 2026",
    url: "https://www.securitycouncilreport.org/monthly-forecast/2026-05/syria-91.php",
    use: "Council-facing political, security, and humanitarian issue frame.",
  },
  {
    label: "CFR Conflict Tracker, Feb. 18 2026",
    url: "https://www.cfr.org/global-conflict-tracker/conflict/conflict-syria/",
    use: "Conflict background, SDF integration, investment and stabilization context.",
  },
  {
    label: "Reuters, Apr. 17 2026",
    url: "https://www.streetinsider.com/Reuters/EU%2Bto%2Brestore%2BSyria%2Brelations%2C%2Bstrengthen%2Btrade%2Band%2Bsecurity%2Bties%2C%2Bdocument%2Bshows/26326863.html",
    use: "EU engagement, cooperation agreement, political dialogue, sanctions adaptation.",
  },
  {
    label: "Brookings, 2026",
    url: "https://www.brookings.edu/articles/shaping-the-new-syria/",
    use: "U.S. policy challenges after Assad and the strategic shape of the new Syria.",
  },
  {
    label: "Chatham House Syria research",
    url: "https://www.chathamhouse.org/regions/middle-east-and-north-africa/syria-and-levant",
    use: "Transition, reconstruction, regional powers, governance, and international re-engagement.",
  },
  {
    label: "FDD reconstruction risk, Feb. 2026",
    url: "https://www.fdd.org/analysis/2026/02/10/foreign-investment-in-syrias-reconstruction-carries-terror-finance-risk/",
    use: "Investment, reconstruction, sanctions relief, terror-finance and compliance risk.",
  },
  {
    label: "Al Jazeera, Jan. 30 2026",
    url: "https://www.aljazeera.com/news/2026/1/30/kurdish-led-sdf-agrees-integration-with-syrian-government-forces",
    use: "SDF integration agreement, ceasefire sequence, northeast security architecture.",
  },
  {
    label: "UN Security Council Live, Apr. 22 2026",
    url: "https://www.un.org/en/security-council-live-regional-war-threatens-syria%E2%80%99s-fragile-transition",
    use: "Regional war pressure and fragility of Syria's transition.",
  },
  {
    label: "Project Gutenberg, War and Peace",
    url: "https://www.gutenberg.org/ebooks/2600",
    use: "Public-domain full text for large-scale book graph extraction and literary conflict ontology demos.",
  },
  {
    label: "Britannica, War and Peace",
    url: "https://www.britannica.com/topic/War-and-Peace",
    use: "Stable reference framing: publication history, Napoleonic setting, main characters, and historical scope.",
  },
  {
    label: "OFAC Syria sanctions relief, 2025",
    url: "https://ofac.treasury.gov/sanctions-programs-and-country-information/syria-related-sanctions",
    use: "Sanctions mechanism modeling: revoked authorities, remaining programs, relief conditions, and compliance checks.",
  },
  {
    label: "European Commission, Apr. 20 2026",
    url: "https://policy.trade.ec.europa.eu/news/commission-proposes-full-resumption-eu-syria-cooperation-agreement-2026-04-20_en",
    use: "EU-Syria cooperation agreement, trade/economic cooperation, financial support, and political partnership.",
  },
  {
    label: "U.S. Treasury, May 23 2025",
    url: "https://home.treasury.gov/news/press-releases/sb0148",
    use: "Immediate Syria sanctions relief, GL 25, investment opening, and conditions on safe haven/minority protection.",
  },
  {
    label: "UN Geneva, Mar. 18 2026",
    url: "https://www.ungeneva.org/en/news-media/news/2026/03/116903/middle-east-war-risks-undermining-syrias-fragile-recovery-security",
    use: "Regional escalation as a distinct temporal episode affecting fragile recovery.",
  },
];

const pipelineSteps = [
  {
    title: "Source Intake",
    detail: "Scope the case to May 2026 Syria transition reporting and attach source_ids to every object.",
  },
  {
    title: "Pre-Ingestion",
    detail: "Normalize source text into chunks, episodes, timestamps, case_id, workspace_id, confidence, and evidence spans.",
  },
  {
    title: "Dynamic Ontology",
    detail: "Activate the policy-analysis profile, then extend around Actor, Claim, Constraint, Leverage, Event, Narrative, Source, and Evidence.",
  },
  {
    title: "Graph Write",
    detail: "Write structured nodes and edges to the graph reasoning API with idempotent source hashing and provenance checks.",
  },
  {
    title: "Temporal Memory",
    detail: "Preserve episodes, valid time, observed time, source_ids, confidence, and source spans for later traceability.",
  },
  {
    title: "Reasoning Mirror",
    detail: "Use the Cozo/Datalog-style mirror for actor profiles, indirect constraints, leverage maps, timelines, and changed_since.",
  },
  {
    title: "Operator Output",
    detail: "Return a demo-ready brief: leverage map, constraint register, timeline, provenance trace, and verification queue.",
  },
];

const graphBackboneLayers = [
  {
    name: "Source / Evidence Graph",
    engine: "Cloud SQL audit + source_ids",
    color: "border-sky-500/40 bg-sky-500/10 text-sky-200",
    nodes: "Source, Evidence, SourceChunk, ExtractionRun",
    purpose: "Every claim points back to a document, span, timestamp, confidence, and ingestion run.",
  },
  {
    name: "Operational Graph",
    engine: "Neo4j Aura",
    color: "border-emerald-500/40 bg-emerald-500/10 text-emerald-200",
    nodes: "Actor, Claim, Constraint, Leverage, Event, Narrative",
    purpose: "The source of truth for connected questions about actors, pressure, constraints, events, and relationships.",
  },
  {
    name: "Temporal Memory",
    engine: "Graphiti on Neo4j",
    color: "border-amber-500/40 bg-amber-500/10 text-amber-200",
    nodes: "Episode, valid_from, valid_to, changed_since",
    purpose: "Tracks when something was observed, when it was valid, and how the situation changes over time.",
  },
  {
    name: "Reasoning Mirror",
    engine: "Cozo / Datalog",
    color: "border-fuchsia-500/40 bg-fuchsia-500/10 text-fuchsia-200",
    nodes: "actor, claim, constraint, leverage, edge",
    purpose: "Rebuildable mirror for fast logic queries: indirect constraints, leverage maps, provenance traces, and timelines.",
  },
  {
    name: "Analytical Lake",
    engine: "Databricks Delta",
    color: "border-violet-500/40 bg-violet-500/10 text-violet-200",
    nodes: "review_queue, graph_quality, benchmarks",
    purpose: "Large-scale extraction, quality scoring, ontology coverage, graph snapshots, and benchmark evidence.",
  },
  {
    name: "Product/API Layer",
    engine: "FastAPI + GraphOps UI",
    color: "border-cyan-500/40 bg-cyan-500/10 text-cyan-200",
    nodes: "health, ingest, search, reasoning, timeline",
    purpose: "Turns the graph backbone into usable workflows for policy, mediation, field analysis, and research teams.",
  },
];

const knowledgeLayers = [
  {
    title: "Actor Layer",
    items: ["Syrian Interim Government", "Ahmed al-Sharaa", "Kurdish-led SDF", "Turkey", "Israel", "United Nations/OCHA", "United States/EU", "Russia/Iran", "ISIS"],
  },
  {
    title: "Constraint Layer",
    items: ["intercommunal violence", "foreign military presence", "sanctions and recognition", "detention camp instability", "faction fragmentation", "accountability obligations", "humanitarian access"],
  },
  {
    title: "Leverage Layer",
    items: ["sanctions relief", "border security pressure", "military pressure", "oil and gas control", "stabilization funding", "counterterrorism cooperation", "international legitimacy"],
  },
  {
    title: "Verification Layer",
    items: ["source_ids", "evidence spans", "confidence", "created_at", "valid_from/valid_to", "changed_since", "operator review flags"],
  },
];

const animatedGraphNodes = [
  { id: "source", label: "UN / SCR / CFR", type: "Source", x: "8%", y: "22%", tone: "bg-sky-500" },
  { id: "evidence", label: "Evidence", type: "Span", x: "22%", y: "58%", tone: "bg-blue-500" },
  { id: "gov", label: "Interim Gov", type: "Actor", x: "42%", y: "18%", tone: "bg-emerald-500" },
  { id: "sdf", label: "SDF", type: "Actor", x: "57%", y: "60%", tone: "bg-emerald-400" },
  { id: "turkey", label: "Turkey", type: "Leverage", x: "74%", y: "27%", tone: "bg-amber-500" },
  { id: "israel", label: "Israel", type: "Leverage", x: "84%", y: "68%", tone: "bg-amber-400" },
  { id: "constraint", label: "Detention / sanctions", type: "Constraint", x: "48%", y: "82%", tone: "bg-rose-500" },
  { id: "reasoning", label: "Datalog answers", type: "Cozo", x: "70%", y: "84%", tone: "bg-fuchsia-500" },
];

const animatedGraphEdges = [
  ["source", "evidence", "EVIDENCES"],
  ["evidence", "gov", "SUPPORTS_CLAIM"],
  ["gov", "sdf", "NEGOTIATES_INTEGRATION"],
  ["turkey", "sdf", "HAS_LEVERAGE"],
  ["israel", "gov", "SECURITY_PRESSURE"],
  ["sdf", "constraint", "CONSTRAINED_BY"],
  ["constraint", "reasoning", "FEEDS_RULES"],
  ["turkey", "reasoning", "LEVERAGE_MAP"],
];

type OntologyForceNode = d3.SimulationNodeDatum & {
  id: string;
  label: string;
  layer: "source" | "ontology" | "case" | "engine" | "query" | "temporal" | "causal" | "benchmark";
  radius: number;
};

type OntologyForceLink = d3.SimulationLinkDatum<OntologyForceNode> & {
  source: string | OntologyForceNode;
  target: string | OntologyForceNode;
  relation: string;
};

const ontologyNodeGroups: Array<{ layer: OntologyForceNode["layer"]; items: string[] }> = [
  {
    layer: "source",
    items: [
      "UN brief Jan",
      "UN brief Feb",
      "Security Council forecast",
      "CFR tracker",
      "humanitarian update",
      "diplomatic statement",
      "book chapter",
      "scene evidence",
      "field note",
      "policy memo",
    ],
  },
  {
    layer: "ontology",
    items: [
      "Actor",
      "Claim",
      "Constraint",
      "Leverage",
      "Event",
      "Narrative",
      "Source",
      "Evidence",
      "Interest",
      "Commitment",
      "Norm",
      "Process",
      "Outcome",
      "Location",
    ],
  },
  {
    layer: "case",
    items: [
      "Syrian Interim Government",
      "Ahmed al-Sharaa",
      "SDF",
      "Turkey",
      "Israel",
      "United Nations",
      "US/EU",
      "Russia/Iran",
      "ISIS",
      "Romeo",
      "Juliet",
      "Capulet",
      "Montague",
      "Friar Laurence",
      "War and Peace",
      "Pierre Bezukhov",
      "Natasha Rostova",
      "Andrei Bolkonsky",
      "Napoleon",
      "Tsar Alexander I",
      "Kutuzov",
      "Battle of Borodino",
      "Moscow evacuation",
    ],
  },
  {
    layer: "temporal",
    items: [
      "observed_at",
      "valid_from",
      "valid_to",
      "changed_since",
      "episode",
      "transition phase",
      "escalation window",
      "scene sequence",
    ],
  },
  {
    layer: "causal",
    items: [
      "causal claim",
      "blocked option",
      "trigger event",
      "enabling condition",
      "risk pathway",
      "counterfactual",
      "confidence score",
      "review flag",
    ],
  },
  {
    layer: "engine",
    items: ["Neo4j", "Graphiti", "Cozo", "Databricks", "Colab", "Cloud SQL", "FastAPI", "GraphOps UI"],
  },
  {
    layer: "query",
    items: [
      "actor_profile",
      "leverage_map",
      "timeline",
      "provenance_trace",
      "indirect_constraints",
      "changed_since query",
      "document builder",
      "review queue",
    ],
  },
  {
    layer: "benchmark",
    items: [
      "baseline answer",
      "graph answer",
      "provenance score",
      "causal score",
      "leverage score",
      "reviewability score",
    ],
  },
];

function graphId(label: string) {
  return label.toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_|_$/g, "");
}

const forceOntologyNodes: OntologyForceNode[] = ontologyNodeGroups.flatMap((group) =>
  group.items.map((label) => ({
    id: graphId(label),
    label,
    layer: group.layer,
    radius:
      group.layer === "case" ? 18 : group.layer === "engine" ? 17 : group.layer === "ontology" ? 16 : 14,
  })),
);

function graphLink(source: string, target: string, relation: string): OntologyForceLink {
  return { source: graphId(source), target: graphId(target), relation };
}

const forceOntologyLinks: OntologyForceLink[] = [
  graphLink("UN brief Jan", "Evidence", "extracts"),
  graphLink("UN brief Feb", "Evidence", "extracts"),
  graphLink("Security Council forecast", "Evidence", "extracts"),
  graphLink("CFR tracker", "Source", "registers"),
  graphLink("humanitarian update", "Event", "observes"),
  graphLink("diplomatic statement", "Claim", "asserts"),
  graphLink("book chapter", "scene evidence", "contains"),
  graphLink("scene evidence", "Event", "grounds"),
  graphLink("field note", "review flag", "may require"),
  graphLink("policy memo", "Norm", "contains"),
  graphLink("Evidence", "Claim", "supports"),
  graphLink("Evidence", "Event", "supports"),
  graphLink("Claim", "Actor", "made_by"),
  graphLink("Actor", "Interest", "has"),
  graphLink("Actor", "Commitment", "makes"),
  graphLink("Actor", "Leverage", "has"),
  graphLink("Actor", "Narrative", "promotes"),
  graphLink("Constraint", "blocked option", "blocks"),
  graphLink("Norm", "Constraint", "creates"),
  graphLink("Event", "causal claim", "feeds"),
  graphLink("Event", "observed_at", "observed"),
  graphLink("Process", "Outcome", "produces"),
  graphLink("Location", "Event", "locates"),
  graphLink("Syrian Interim Government", "Claim", "asserts"),
  graphLink("Ahmed al-Sharaa", "Process", "leads"),
  graphLink("SDF", "Commitment", "negotiates"),
  graphLink("Turkey", "Leverage", "uses"),
  graphLink("Israel", "Leverage", "uses"),
  graphLink("Israel", "Constraint", "creates"),
  graphLink("United Nations", "Norm", "frames"),
  graphLink("US/EU", "Leverage", "sanctions"),
  graphLink("Russia/Iran", "Narrative", "legacy networks"),
  graphLink("ISIS", "risk pathway", "creates"),
  graphLink("Romeo", "Commitment", "makes"),
  graphLink("Juliet", "Commitment", "makes"),
  graphLink("Capulet", "Constraint", "imposes"),
  graphLink("Montague", "Narrative", "family frame"),
  graphLink("Friar Laurence", "Process", "mediates"),
  graphLink("War and Peace", "book chapter", "contains"),
  graphLink("War and Peace", "Narrative", "contains"),
  graphLink("Pierre Bezukhov", "Interest", "searches for"),
  graphLink("Pierre Bezukhov", "Commitment", "transforms"),
  graphLink("Natasha Rostova", "Commitment", "changes"),
  graphLink("Natasha Rostova", "Narrative", "embodies"),
  graphLink("Andrei Bolkonsky", "Process", "returns to war"),
  graphLink("Andrei Bolkonsky", "causal claim", "tests"),
  graphLink("Napoleon", "Leverage", "military invasion"),
  graphLink("Tsar Alexander I", "Claim", "declares war"),
  graphLink("Kutuzov", "Process", "commands"),
  graphLink("Battle of Borodino", "Event", "is"),
  graphLink("Battle of Borodino", "causal claim", "supports"),
  graphLink("Moscow evacuation", "Event", "is"),
  graphLink("Moscow evacuation", "Constraint", "creates"),
  graphLink("valid_from", "transition phase", "bounds"),
  graphLink("valid_to", "transition phase", "bounds"),
  graphLink("changed_since", "changed_since query", "powers"),
  graphLink("episode", "scene sequence", "orders"),
  graphLink("escalation window", "risk pathway", "contains"),
  graphLink("trigger event", "causal claim", "supports"),
  graphLink("enabling condition", "causal claim", "qualifies"),
  graphLink("counterfactual", "causal claim", "tests"),
  graphLink("confidence score", "review flag", "sets"),
  graphLink("Neo4j", "Actor", "stores"),
  graphLink("Neo4j", "Claim", "stores"),
  graphLink("Neo4j", "Leverage", "stores"),
  graphLink("Graphiti", "episode", "tracks"),
  graphLink("Graphiti", "changed_since", "tracks"),
  graphLink("Cozo", "indirect_constraints", "answers"),
  graphLink("Cozo", "leverage_map", "answers"),
  graphLink("Databricks", "document builder", "runs"),
  graphLink("Databricks", "review queue", "creates"),
  graphLink("Colab", "document builder", "inspects"),
  graphLink("Cloud SQL", "review queue", "audits"),
  graphLink("FastAPI", "actor_profile", "serves"),
  graphLink("GraphOps UI", "document builder", "controls"),
  graphLink("actor_profile", "graph answer", "generates"),
  graphLink("timeline", "graph answer", "generates"),
  graphLink("provenance_trace", "provenance score", "scores"),
  graphLink("indirect_constraints", "causal score", "scores"),
  graphLink("leverage_map", "leverage score", "scores"),
  graphLink("baseline answer", "graph answer", "compares"),
  graphLink("graph answer", "reviewability score", "scores"),
  graphLink("Databricks", "baseline answer", "benchmarks"),
  graphLink("Databricks", "graph answer", "benchmarks"),
  graphLink("review queue", "reviewability score", "feeds"),
];

const ontologyFlow = [
  {
    stage: "Raw reporting",
    tokens: ["renewed clashes", "Kurdish deal", "humanitarian access", "sanctions relief"],
  },
  {
    stage: "Canonical objects",
    tokens: ["Actor", "Claim", "Constraint", "Leverage", "Event", "Evidence"],
  },
  {
    stage: "Lenses",
    tokens: ["statecraft", "mediation", "humanitarian", "counter-ISIS", "legitimacy"],
  },
  {
    stage: "Queries",
    tokens: ["leverage_map", "timeline", "provenance_trace", "changed_since"],
  },
];

const policyConflictLayers = [
  {
    title: "Policy / Statecraft Graph",
    question: "Which recognition, sanctions, security, funding, and legitimacy constraints shape feasible options?",
    semanticLayer: "Actor -> Claim -> Norm/Constraint -> Leverage -> PolicyOption",
    output: "statecraft options with blockers, external patrons, and source-backed assumptions",
  },
  {
    title: "Conflict Resolution Graph",
    question: "What process could reduce escalation risk between the interim government, SDF, communities, and external actors?",
    semanticLayer: "Actor -> Interest -> Commitment -> Trust/Guarantee -> Process",
    output: "mediation openings, guarantees, sequencing, and verification questions",
  },
  {
    title: "Humanitarian Protection Graph",
    question: "Where do violence, camps, detention facilities, access limits, and civilian protection needs intersect?",
    semanticLayer: "Event -> Location -> Constraint -> AffectedGroup -> Evidence",
    output: "risk register, source trace, priority gaps, and changed_since alerts",
  },
  {
    title: "Strategic Leverage Graph",
    question: "Who can change the transition outcome without directly governing the transition?",
    semanticLayer: "ExternalActor -> Leverage -> Constraint -> Actor -> Outcome",
    output: "Turkey, Israel, US/EU, Russia/Iran, UN, and funding/recognition pressure map",
  },
];

const engineStack = [
  { name: "FastAPI", role: "public service API", status: "live", icon: ServerCog },
  { name: "Neo4j", role: "primary graph memory", status: "source of truth", icon: Network },
  { name: "Graphiti", role: "temporal/provenance layer", status: "Neo4j-backed", icon: Timer },
  { name: "Cozo", role: "Datalog mirror", status: "read-optimized", icon: Cpu },
  { name: "Cloud SQL", role: "run audit + pipeline history", status: "durable", icon: Database },
  { name: "Databricks", role: "scale extraction + benchmarks", status: "analytical", icon: BarChart3 },
];

const demoCaseConfigs = [
  {
    id: "syria",
    label: "Syria Transition",
    icon: Globe2,
    workspaceId: WORKSPACE_ID,
    caseId: CASE_ID,
    sourcePack: "UN Geneva + Security Council Report + CFR conflict tracker",
    sourceType: "current-affairs-policy-brief",
    defaultQuery: "Which actors have leverage over Syria's transition?",
    configUrl: "/demo-configs/syria-transition-dialectica.config.json",
    lenses: [
      "policy-statecraft",
      "mediation-integration",
      "humanitarian-protection",
      "strategic-leverage",
      "counter-isis-risk",
    ],
    canonicalObjects: ["Actor", "Claim", "Constraint", "Leverage", "Event", "Narrative", "Source", "Evidence"],
    benchmark: "Does graph grounding improve leverage precision, provenance, and next-question quality?",
  },
  {
    id: "book",
    label: "Book Conflict Graph",
    icon: BookOpen,
    workspaceId: "books-conflict-resolution-lab",
    caseId: "romeo-juliet-conflict-resolution",
    sourcePack: "Project Gutenberg Romeo and Juliet",
    sourceType: "public-domain-book",
    defaultQuery: "How do family power, secrecy, banishment, and failed mediation interact?",
    configUrl: "/demo-configs/book-conflict-dialectica.config.json",
    lenses: [
      "literary-conflict",
      "mediation-resolution",
      "escalation-timeline",
      "narrative-identity",
      "commitment-tracking",
    ],
    canonicalObjects: ["Actor", "Event", "Narrative", "Constraint", "Commitment", "Interest", "Evidence", "Episode"],
    benchmark: "Does graph grounding preserve causality, character commitments, and evidence better than summary-only LLM answers?",
  },
  {
    id: "war-peace",
    label: "War and Peace Graph",
    icon: BookOpen,
    workspaceId: "gutenberg-conflict-lab",
    caseId: "war-and-peace-conflictual-relations",
    sourcePack: "Project Gutenberg War and Peace + stable literary reference notes",
    sourceType: "public-domain-book-large-scale",
    defaultQuery: "How do war, family, ideology, and personal transformation interact across the novel?",
    configUrl: "/demo-configs/war-and-peace-dialectica.config.json",
    lenses: [
      "literary-conflict",
      "historical-causality",
      "character-transformation",
      "battlefield-episode",
      "family-social-pressure",
      "philosophy-of-history",
    ],
    canonicalObjects: ["Actor", "Event", "Narrative", "Constraint", "Commitment", "Interest", "Evidence", "Episode", "CausalClaim"],
    benchmark: "Does graph grounding separate Tolstoy's causal theory, historical events, and character commitments better than summary-only LLM answers?",
  },
];

const extractionPipeline = [
  { stage: "Source Pack", detail: "reports, books, transcripts, notes", icon: FileText },
  { stage: "Pre-Digest", detail: "chunk, source hash, evidence spans", icon: FileCode },
  { stage: "Ontology Lens", detail: "expert schema + canonical mappings", icon: Settings2 },
  { stage: "Databricks / Colab", detail: "scale extraction, notebooks, QA", icon: BarChart3 },
  { stage: "Neo4j + Graphiti", detail: "primary graph + temporal memory", icon: Network },
  { stage: "Cozo Reasoning", detail: "Datalog mirror + query layer", icon: Cpu },
  { stage: "Benchmark", detail: "plain LLM vs graph-grounded answer", icon: Zap },
];

const benchmarkComparison = [
  {
    metric: "Provenance",
    baseline: 42,
    dialectica: 91,
    why: "Plain LLM cites general context; Dialectica returns object source_ids and evidence spans.",
  },
  {
    metric: "Causal precision",
    baseline: 48,
    dialectica: 84,
    why: "Events, constraints, and claims are separated before reasoning.",
  },
  {
    metric: "Leverage mapping",
    baseline: 52,
    dialectica: 88,
    why: "Leverage is typed as graph structure, not hidden in prose.",
  },
  {
    metric: "Reviewability",
    baseline: 36,
    dialectica: 93,
    why: "Every answer can be traced to graph objects, runs, and sources.",
  },
];

const caseBlueprints = [
  {
    title: "Syria: political process and Israel relations",
    objective:
      "Structure the transition as a statecraft graph where domestic consolidation, SDF integration, Israeli security pressure, sanctions, humanitarian access, and recognition are all separate but connected layers.",
    expertQuestions: [
      "Which constraints are internal to the transition and which come from external leverage?",
      "How do Israeli security demands and southern Syria dynamics constrain the interim government's political process?",
      "Which claims require source verification before policy conclusions are safe?",
      "What changed since the last UN or Security Council reporting window?",
    ],
    ontology: ["Actor", "Claim", "Constraint", "Leverage", "Event", "Narrative", "Source", "Evidence", "Norm"],
    relations: ["HAS_LEVERAGE", "CONSTRAINS", "EVIDENCED_BY", "CHANGED_SINCE", "FRAMES", "BLOCKS_OPTION"],
  },
  {
    title: "Book: conflict dynamics inside a narrative",
    objective:
      "Structure a book as a conflict-resolution graph so a reader can inspect actors, escalation events, commitments, constraints, failed mediation, narrative identity, and evidence from scenes.",
    expertQuestions: [
      "Which events cause escalation rather than merely happen later?",
      "Which commitments constrain the characters?",
      "Where does failed mediation change the trajectory?",
      "Which narrative frames drive actors into incompatible choices?",
    ],
    ontology: ["Actor", "Event", "Commitment", "Constraint", "Interest", "Narrative", "Evidence", "Episode"],
    relations: ["PARTICIPATES_IN", "CAUSED", "HAS_INTEREST", "CONSTRAINED_BY", "PROMOTES", "EVIDENCED_BY"],
  },
];

const colabNotebookSteps = [
  {
    name: "Load config",
    code: "config = json.load(open('syria-transition-dialectica.config.json'))",
  },
  {
    name: "Inspect coverage",
    code: "coverage = dialectica.profile_coverage(config, extracted_objects)",
  },
  {
    name: "Review weak claims",
    code: "review_queue = dialectica.rank_review_items(objects, min_confidence=0.72)",
  },
  {
    name: "Benchmark answer",
    code: "score = dialectica.compare_baseline_vs_graph(question, baseline, graph_answer)",
  },
];

const pageMap = [
  {
    title: "1. Orient",
    detail: "Show what Dialectica is: a situation graph backbone, not a one-off Syria dashboard.",
  },
  {
    title: "2. Build",
    detail: "Turn documents into source IDs, evidence spans, ontology objects, temporal layers, and causal claims.",
  },
  {
    title: "3. Reason",
    detail: "Use Neo4j, Graphiti, Cozo, and Databricks to answer actor, leverage, timeline, and provenance questions.",
  },
  {
    title: "4. Benchmark",
    detail: "Generate hard questions and compare plain LLM answers against graph-grounded answers.",
  },
];

const demoReadinessChecks = [
  {
    label: "Story opens fast",
    detail: "The first screen explains Dialectica as a general graph backbone before Syria, books, or any single case.",
  },
  {
    label: "Controls are real",
    detail: "Health, ingest, runs, search, and actor reasoning call the deployed API rather than canned responses.",
  },
  {
    label: "Visuals show structure",
    detail: "D3 and animated graphs show source, ontology, temporal, causal, engine, query, and benchmark layers.",
  },
  {
    label: "Demo has fallbacks",
    detail: "If the API key is not entered, the page still records well through configs, graph visuals, source links, and benchmark examples.",
  },
];

const demoJumpLinks = [
  { label: "Backbone", href: "#graph-backbone" },
  { label: "D3 graph", href: "#d3-ontology" },
  { label: "Temporal", href: "#temporal-episodes" },
  { label: "Config", href: "#config-builder" },
  { label: "Live API", href: "#live-controls" },
  { label: "Sources", href: "#case-brief" },
];

const statecraftOntology = [
  {
    category: "Political Process",
    objects: ["TransitionAuthority", "Recognition", "ConstitutionalProcess", "CivilSociety", "LegitimacyClaim"],
    question: "Who can make the process credible, and who can delegitimize it?",
  },
  {
    category: "External Leverage",
    objects: ["SanctionsRelief", "BorderPressure", "MilitaryPosture", "Funding", "DiplomaticRecognition"],
    question: "Which outside actor can change incentives without directly governing?",
  },
  {
    category: "Security Architecture",
    objects: ["SDFIntegration", "DetentionFacility", "CounterISISRisk", "SouthernSecurityDemand", "ForeignPresence"],
    question: "Which security constraints block or enable political settlement?",
  },
  {
    category: "Humanitarian Governance",
    objects: ["HumanitarianAccess", "Displacement", "CampSecurity", "ProtectionNeed", "Accountability"],
    question: "Where does civilian protection shape legitimacy and available options?",
  },
];

const conflictOntology = [
  {
    layer: "Actors and roles",
    structure: "Actor -> Role -> Process",
    example: "Interim government as transition authority; UN as process legitimizer; Friar Laurence as failed mediator.",
  },
  {
    layer: "Interests and constraints",
    structure: "Actor -> Interest -> Constraint -> Option",
    example: "SDF seeks autonomy/security guarantees; Juliet seeks agency under family constraint.",
  },
  {
    layer: "Commitments and trust",
    structure: "Actor -> Commitment -> Evidence -> TrustState",
    example: "Integration promises and ceasefire terms; secret marriage and failed disclosure.",
  },
  {
    layer: "Narratives and escalation",
    structure: "Narrative -> Event -> CausalClaim -> Phase",
    example: "Security narratives around southern Syria; family honor narratives in Romeo and Juliet.",
  },
];

const temporalCausalLayers = [
  {
    name: "Observed Time",
    purpose: "When the system read or observed a claim.",
    graph: "Source -> Evidence -> observed_at",
  },
  {
    name: "Valid Time",
    purpose: "When the claim was true or relevant in the world.",
    graph: "Claim/Event -> valid_from -> valid_to",
  },
  {
    name: "Episode Time",
    purpose: "How events cluster into phases, chapters, or reporting windows.",
    graph: "Event -> Episode -> TransitionPhase",
  },
  {
    name: "Causal Layer",
    purpose: "Separates sequence from actual causal assertions.",
    graph: "TriggerEvent -> CausalClaim -> RiskPathway -> Outcome",
  },
];

const realSituationBoard = [
  {
    phase: "legacy conflict system",
    period: "pre-transition baseline",
    node: "Assad-era war legacy",
    source: "CFR + Brookings",
    structure: "Episode -> Constraint -> LegitimacyRisk",
    edge: "CONSTRAINS transition authority, reconstruction, returns, and accountability.",
  },
  {
    phase: "post-Assad transition",
    period: "2025-2026",
    node: "Interim government consolidation",
    source: "UN + Security Council Report",
    structure: "Actor -> Claim -> RecognitionConstraint",
    edge: "REQUIRES security delivery, inclusion, and credible political process.",
  },
  {
    phase: "northeast settlement",
    period: "Jan-Feb 2026",
    node: "SDF integration bargain",
    source: "UN + CFR + FDD Long War Journal",
    structure: "Actor -> Commitment -> TrustState -> SecurityArchitecture",
    edge: "AFFECTS counter-ISIS, detention sites, oil/gas control, and national army design.",
  },
  {
    phase: "southern security pressure",
    period: "2026 reporting window",
    node: "Israel and southern Syria security demands",
    source: "Security Council Report + UN",
    structure: "ExternalActor -> Leverage -> Constraint -> PoliticalOption",
    edge: "CONSTRAINS border posture, foreign militia risk, Druze protection, and recognition strategy.",
  },
  {
    phase: "economic re-entry",
    period: "Apr 2026",
    node: "EU re-engagement and trade/security ties",
    source: "Reuters + European Commission",
    structure: "ExternalActor -> Incentive -> SanctionsRelief -> ReformCondition",
    edge: "ENABLES cooperation while preserving compliance, security, and political conditions.",
  },
  {
    phase: "reconstruction risk",
    period: "2026",
    node: "Investment, sanctions, terror-finance exposure",
    source: "Brookings + Chatham House + FDD",
    structure: "CapitalFlow -> ComplianceRisk -> Evidence -> ReviewQueue",
    edge: "BLOCKS unsafe financing and flags projects needing provenance and beneficiary checks.",
  },
];

const didacticMirrorSteps = [
  {
    step: "1. Read",
    title: "Documents become evidence, not summaries",
    detail: "The LLM chunks reports, books, transcripts, and briefs into source-bound evidence spans with source_ids, timestamps, and confidence.",
  },
  {
    step: "2. Extract",
    title: "Evidence becomes typed candidates",
    detail: "Each span proposes Actors, Claims, Constraints, Leverage, Events, Narratives, Commitments, and causal claims.",
  },
  {
    step: "3. Canonicalize",
    title: "Dynamic ontology removes boilerplate",
    detail: "A case lens can add SDFIntegration, SanctionsRelief, or SceneConflict while mapping back to canonical graph primitives.",
  },
  {
    step: "4. Temporalize",
    title: "Episodes preserve situation change",
    detail: "Pre-Assad legacy, post-Assad transition, SDF integration, Israel pressure, and sanctions windows become comparable phases.",
  },
  {
    step: "5. Reason",
    title: "Graphs make the answer inspectable",
    detail: "Neo4j keeps the connected graph, Graphiti records temporal/provenance memory, and Cozo answers Datalog-style constraints.",
  },
  {
    step: "6. Benchmark",
    title: "The graph competes with a plain LLM",
    detail: "The same question is answered by a baseline LLM and a graph-grounded workflow, then scored for source use and reasoning quality.",
  },
];

const economicSanctionsOntology = [
  {
    category: "Sanctions and Relief",
    objects: ["SanctionsMeasure", "ReliefCondition", "LicensingPath", "DesignatedEntity", "ComplianceException"],
    question: "Which restrictions block aid, investment, trade, banking, or reconstruction, and which relief paths are credible?",
  },
  {
    category: "Reconstruction Finance",
    objects: ["CapitalFlow", "Beneficiary", "ProjectSponsor", "ProcurementRisk", "VerificationRequirement"],
    question: "Who benefits from reconstruction money, and what evidence proves the flow is legitimate?",
  },
  {
    category: "Economic Development",
    objects: ["TradeCorridor", "EnergyAsset", "LaborMarket", "MunicipalService", "PrivateSectorReform"],
    question: "Which economic moves stabilize households and institutions without empowering violent or corrupt networks?",
  },
  {
    category: "Security-Economy Coupling",
    objects: ["BorderRevenue", "CaptagonNetwork", "MilitiaTaxation", "CounterTerrorRisk", "PoliceCapacity"],
    question: "Where do trade, borders, police capacity, and organized crime create political leverage?",
  },
];

const backboneContracts = [
  {
    layer: "Canonical Primitives",
    deterministic: "IDs, hashes, relation names, timestamps, source_ids, confidence bounds, and required provenance.",
    aiAugmented: "LLM proposes object candidates, relation labels, uncertainty notes, and ontology extensions.",
    query: "show me every unsupported Claim or orphaned Event before graph write",
  },
  {
    layer: "Dynamic Ontology Compiler",
    deterministic: "Custom types map to Actor, Claim, Constraint, Leverage, Commitment, Event, Narrative, Source, Evidence.",
    aiAugmented: "The model suggests domain-specific types like SanctionsRelief, TrustInjury, or BattleEpisode.",
    query: "which custom types are used in this workspace and what canonical primitive do they compile to?",
  },
  {
    layer: "Temporal and Causal Kernel",
    deterministic: "Observed time, valid time, episode membership, edge validity, and causal confidence are explicit fields.",
    aiAugmented: "The model flags likely causality, counterfactuals, and phase changes for review.",
    query: "what changed since the last source pack, and which causal edges are low confidence?",
  },
  {
    layer: "Reasoning and Benchmark Layer",
    deterministic: "Cozo rules, graph traversals, provenance traces, and score rubrics are repeatable.",
    aiAugmented: "The model drafts answers, generates benchmark questions, and explains graph paths in prose.",
    query: "compare the plain LLM answer with the graph-grounded answer and list missing evidence",
  },
];

const bookGutenbergUseCases = [
  {
    book: "War and Peace",
    source: "Project Gutenberg eBook 2600",
    focus: "Conflictual relations across families, armies, states, social salons, battlefield episodes, and inner moral change.",
    captures: [
      "Pierre's search for meaning as Interest and IdentityShift nodes.",
      "Andrei's military ambition, disillusionment, love, and forgiveness as temporal commitments.",
      "Natasha's engagement, breach, recovery, and evacuation choices as causal episode evidence.",
      "Napoleon, Alexander, Kutuzov, Borodino, and Moscow as historical actors/events connected to fictional lives.",
    ],
    queries: [
      "Which personal conflicts are intensified by the 1812 invasion?",
      "Which characters change commitments after Borodino or Moscow?",
      "Where does Tolstoy challenge great-man causality with distributed social causality?",
    ],
  },
  {
    book: "Romeo and Juliet",
    source: "Public-domain dramatic text",
    focus: "Escalation, family identity, secret commitments, failed mediation, honor norms, and irreversible timing.",
    captures: [
      "Family feud as Narrative plus Constraint, not just a background fact.",
      "Secret marriage as Commitment with hidden validity and later consequence.",
      "Banishment as Event that changes available mediation options.",
      "Friar Laurence as ProcessActor with failed delivery and trust consequences.",
    ],
    queries: [
      "Which event closes the last feasible mediation window?",
      "Which commitments are hidden from which actors?",
      "Which causal edges are evidence-backed versus inferred by the analyst?",
    ],
  },
];

const warPeaceRelationExamples = [
  {
    relation: "Napoleon --INVADES--> Russia",
    ontology: "HistoricalActor -> Event -> Location",
    why: "A deterministic event edge anchors the novel's social and personal arcs in a dated historical episode.",
  },
  {
    relation: "Battle of Borodino --CHANGES_OPTIONS_FOR--> Andrei",
    ontology: "Event -> CausalClaim -> ActorState",
    why: "The system distinguishes the battle's chronology from claims about how it changes a character trajectory.",
  },
  {
    relation: "Natasha --REPAIRS_LEGITIMACY_THROUGH--> Moscow evacuation choice",
    ontology: "Actor -> Action -> MoralNarrative -> Evidence",
    why: "A literary interpretation becomes inspectable because it is attached to scene evidence and review flags.",
  },
  {
    relation: "Pierre --CONSTRAINED_BY--> inheritance, marriage, captivity, ideology",
    ontology: "Actor -> Constraint -> IdentityShift",
    why: "The graph lets readers ask whether personal growth follows social pressure, war experience, or internal commitment.",
  },
  {
    relation: "Tolstoy narrator --CONTESTS--> great-man theory",
    ontology: "Narrative -> Claim -> CounterClaim -> Evidence",
    why: "Abstract philosophical argument is captured as queryable claims connected to events and examples.",
  },
];

const syriaConflictCapture = [
  {
    object: "SDF integration",
    captures: "Ceasefire, security institutions, territorial control, detention/counter-ISIS exposure, trust, and guarantees.",
    graph: "SDF -> Commitment -> IntegrationProcess -> Constraint -> CounterISISRisk",
    question: "Which guarantees make integration credible, and which weak sources need review?",
  },
  {
    object: "Israel and southern Syria",
    captures: "Security posture, border pressure, Druze protection claims, militia-crossing risk, and recognition constraints.",
    graph: "Israel -> Leverage -> SouthernSecurityConstraint -> PoliticalOption",
    question: "How does southern security pressure alter the interim government's feasible diplomatic sequence?",
  },
  {
    object: "Intercommunal violence",
    captures: "Events, affected groups, accountability claims, humanitarian access, retaliation risk, and legitimacy loss.",
    graph: "Event -> AffectedGroup -> Constraint -> LegitimacyClaim -> Source",
    question: "Which events create the largest indirect constraints on political legitimacy?",
  },
  {
    object: "External patrons",
    captures: "Turkey, US/EU, Russia/Iran, UN, Gulf investors, and how each uses different leverage channels.",
    graph: "ExternalActor -> LeverageType -> Actor/Constraint -> Outcome",
    question: "Which outside actor can change incentives without formally owning the transition?",
  },
];

const syriaEconomicCapture = [
  {
    object: "Sanctions relief",
    captures: "Licensing, delisting, sectoral restrictions, humanitarian exceptions, banking access, and political conditions.",
    graph: "SanctionsMeasure -> ReliefCondition -> CapitalFlow -> VerificationRequirement",
    question: "Which recovery actions are blocked by sanctions, and which only require compliance controls?",
  },
  {
    object: "Reconstruction finance",
    captures: "Investor, sponsor, contractor, beneficiary, location, procurement risk, and terror-finance review queue.",
    graph: "Project -> CapitalFlow -> Beneficiary -> ComplianceRisk -> Evidence",
    question: "Who benefits from this project, and what evidence proves funds do not strengthen violent networks?",
  },
  {
    object: "Trade and security cooperation",
    captures: "EU engagement, police capacity, organized crime/captagon risk, border management, and private sector reform.",
    graph: "EU -> Incentive -> SecurityCooperation -> ReformCondition -> Outcome",
    question: "Which trade incentives depend on security cooperation or institutional reform?",
  },
  {
    object: "Service delivery legitimacy",
    captures: "Electricity, health, food systems, local administration, return conditions, and public trust.",
    graph: "ServiceNeed -> DeliveryConstraint -> LegitimacyOutcome -> Source",
    question: "Which service failures most directly undermine recognition and stabilization?",
  },
];

const queryWorkbenchExamples = [
  {
    prompt: "Show me all leverage on the Syria transition, grouped by channel and source confidence.",
    graphQuery: "MATCH (a:Actor)-[:HAS_LEVERAGE]->(l:Leverage)-[:AFFECTS]->(x) RETURN a,l,x,source_ids",
    answerShape: "Actor profile, leverage type, target constraint, evidence spans, confidence, review flags.",
  },
  {
    prompt: "Which War and Peace episodes transform Pierre's commitments?",
    graphQuery: "MATCH (p:Actor {name:'Pierre Bezukhov'})-[:HAS_COMMITMENT|CONSTRAINED_BY|PARTICIPATES_IN*1..3]->(e) RETURN e",
    answerShape: "Episode timeline with scenes, constraints, commitment changes, and textual evidence.",
  },
  {
    prompt: "What changed in Syria since the last reporting window?",
    graphQuery: "changed_since(timestamp) over Event, Claim, Constraint, Leverage, Source",
    answerShape: "New or revised objects, invalidated edges, changed confidence, and provenance trace.",
  },
  {
    prompt: "Generate benchmark questions for this ontology.",
    graphQuery: "coverage gaps + high-centrality nodes + low-confidence causal edges",
    answerShape: "Questions, expected graph paths, scoring rubric, baseline LLM failure modes.",
  },
];

const criticalLayerGraph = [
  {
    layer: "Evidence Layer",
    requiredObjects: ["Source", "Evidence", "SourceChunk", "ExtractionRun"],
    invariant: "No Claim, Event, Leverage, or Constraint can exist without source_ids and evidence_span.",
    query: "find graph objects missing provenance before they reach Neo4j",
  },
  {
    layer: "Temporal Episode Layer",
    requiredObjects: ["Episode", "TransitionPhase", "Scene", "ReportingWindow", "valid_from", "valid_to"],
    invariant: "Every situation-changing edge belongs to an episode, so timelines are first-class graph structure.",
    query: "show all edges that changed between the January, February, April, and May Syria reporting windows",
  },
  {
    layer: "Causal Mechanism Layer",
    requiredObjects: ["Trigger", "Mechanism", "TransmissionChannel", "Impact", "Counterfactual", "Confidence"],
    invariant: "A causal edge must name how influence travels, not only that two events are related.",
    query: "which sanctions effects are direct legal prohibitions, indirect banking risk, or political signaling?",
  },
  {
    layer: "Statecraft / Conflict Layer",
    requiredObjects: ["Actor", "Interest", "Constraint", "Leverage", "Commitment", "Guarantee", "TrustState"],
    invariant: "Actors are never just names; they carry interests, constraints, commitments, leverage, and time-bound roles.",
    query: "which actors can credibly change an outcome, and what constrains their ability to do so?",
  },
];

const temporalEpisodeExamples = [
  {
    case: "Syria",
    episode: "Legacy conflict inheritance",
    window: "2011-2024 baseline",
    graph: "Episode -> AssadEraLegacy -> Constraint -> AccountabilityNeed",
    nodes: ["detention legacy", "sanctions architecture", "displacement", "war-crimes accountability"],
    question: "Which constraints belong to the pre-transition legacy and should not be mistaken for new policy choices?",
  },
  {
    case: "Syria",
    episode: "Post-Assad political transition",
    window: "2025-2026",
    graph: "Episode -> InterimGovernment -> Claim -> RecognitionCondition",
    nodes: ["interim authority", "UN process", "inclusive transition", "legitimacy claim"],
    question: "Which claims changed after recognition, elections, or new Security Council reporting?",
  },
  {
    case: "Syria",
    episode: "SDF integration and northeast security",
    window: "Jan-Feb 2026",
    graph: "Episode -> SDFIntegration -> Commitment -> SecurityArchitecture",
    nodes: ["ceasefire", "integration bargain", "detention risk", "counter-ISIS requirement"],
    question: "Which commitments are implemented, delayed, violated, or only claimed by one source?",
  },
  {
    case: "Syria",
    episode: "EU economic re-engagement",
    window: "Apr-May 2026",
    graph: "Episode -> CooperationAgreement -> Incentive -> ReformCondition",
    nodes: ["trade framework", "financial support", "police capacity", "private-sector financing"],
    question: "Which economic incentives depend on security, reform, or compliance conditions?",
  },
  {
    case: "War and Peace",
    episode: "St. Petersburg salon",
    window: "1805 opening social field",
    graph: "Scene -> SocialNetwork -> Narrative -> CommitmentPressure",
    nodes: ["Pierre", "Andrei", "Kuragin circle", "Rostov/Bolkonsky families"],
    question: "Which social constraints exist before the battlefield changes the actors' options?",
  },
  {
    case: "War and Peace",
    episode: "Borodino and Moscow",
    window: "1812 war episode",
    graph: "BattleEpisode -> CausalClaim -> IdentityShift -> LaterCommitment",
    nodes: ["Napoleon", "Kutuzov", "Andrei", "Pierre", "Natasha", "Moscow evacuation"],
    question: "Which character transformations are tied to war events, and which are interpretive claims?",
  },
];

const sanctionsCausalMechanisms = [
  {
    mechanism: "Legal authority change",
    chain: "SanctionsAuthority -> Revocation/License -> AuthorizedActivity -> ComplianceBoundary",
    example: "OFAC relief can authorize broad activity while still requiring checks against remaining designations or export controls.",
    deterministicCheck: "Store authority_id, effective_date, allowed_activity, prohibited_party_screening, and valid_to.",
  },
  {
    mechanism: "Banking risk transmission",
    chain: "SanctionsSignal -> BankRiskPolicy -> PaymentAccess -> ProjectFeasibility",
    example: "Even after relief, banks may delay transactions until counterparties, sectors, and beneficiaries are verified.",
    deterministicCheck: "Track counterparty, sector, beneficiary, screening status, evidence_span, and confidence.",
  },
  {
    mechanism: "Political conditionality",
    chain: "ExternalActor -> ReliefCondition -> GovernmentBehavior -> Recognition/Support",
    example: "EU cooperation can create incentives around reform, security cooperation, private-sector financing, and political partnership.",
    deterministicCheck: "Represent condition, actor, expected behavior, evidence, deadline, and review owner.",
  },
  {
    mechanism: "Indirect conflict impact",
    chain: "ReliefOrRestriction -> CapitalFlow -> LocalPowerBalance -> ConflictRisk",
    example: "Reconstruction money can stabilize services or empower violent/corrupt networks depending on beneficiaries.",
    deterministicCheck: "Require beneficiary graph, procurement risk, local actor links, and human review before acceptance.",
  },
];

const userTrackingNeeds = [
  {
    need: "What changed?",
    tracks: "new sources, revised claims, changed confidence, invalidated edges, new episodes",
    example: "A May Security Council update changes the southern Syria pressure layer and the SDF integration risk layer.",
  },
  {
    need: "Who can influence outcomes?",
    tracks: "leverage channels, constraints, interests, commitments, guarantees, external patrons",
    example: "Turkey, Israel, EU, US, UN, SDF, and the interim government all have different channels and limits.",
  },
  {
    need: "What is evidence and what is interpretation?",
    tracks: "source spans, extraction run, causal confidence, analyst review, benchmark failures",
    example: "A War and Peace scene edge is evidence; a claim about Tolstoy's theory of causality is interpretive and needs review.",
  },
  {
    need: "Which decision is safer?",
    tracks: "options, blockers, second-order effects, sanctions compliance, humanitarian impact, legitimacy risk",
    example: "A reconstruction project is only safe if capital flow, beneficiary, procurement, and local conflict effects are represented.",
  },
];

const articleGraphExamples = [
  {
    source: "Security Council Report, May 2026",
    sourceGraph: "Source -> Evidence -> IsraelMilitaryActivity -> SouthernSecurityConstraint",
    meaning: "The graph shows Israeli military activity as a pressure channel affecting Syria's political process, not as an isolated event.",
    query: "Which southern security claims constrain recognition or border policy?",
  },
  {
    source: "UN Security Council, Apr. 22 2026",
    sourceGraph: "Source -> ReportingWindow -> RegionalWarRisk -> FragileTransition",
    meaning: "Regional escalation becomes a temporal risk episode with effects on recovery, aid, and diplomacy.",
    query: "What changed in transition risk after the April Security Council meeting?",
  },
  {
    source: "European Commission, Apr. 2026",
    sourceGraph: "Source -> CooperationAgreement -> TradeFramework -> ReformCondition",
    meaning: "The EU item becomes incentives, conditions, financial support, and security cooperation nodes.",
    query: "Which EU incentives require reform, police capacity, or private-sector financing conditions?",
  },
  {
    source: "OFAC / Treasury relief",
    sourceGraph: "Source -> SanctionsAuthority -> License/Revocation -> AuthorizedActivity",
    meaning: "Sanctions relief is modeled as executable policy logic: what became allowed, when, for whom, and with which residual checks.",
    query: "Which project actions are authorized, risky, or still blocked?",
  },
];

const researchDossier = [
  {
    source: "European Commission, Apr. 20 2026",
    specificBit:
      "The Commission proposed full resumption of the EU-Syria Cooperation Agreement, including political partnership, enhanced trade/economic cooperation, and about EUR620M in support for 2026-2027.",
    graphObjects: ["CooperationAgreement", "FinancialSupportPackage", "TradeFramework", "ReformCondition", "EU"],
    graphPath: "Source -> Evidence -> CooperationAgreement -> Incentive -> ReformCondition -> PolicyOption",
    praxisUse: "Drafts an EU engagement brief with conditions, beneficiaries, risks, and follow-up questions.",
  },
  {
    source: "Security Council Report, May 2026",
    specificBit:
      "The forecast links Israel's continued military activities in southern Syria, SDF/DAANES integration into government institutions, and accountability/humanitarian concerns.",
    graphObjects: ["SouthernSecurityConstraint", "SDFIntegration", "AccountabilityRisk", "HumanitarianConstraint"],
    graphPath: "Source -> ReportingWindow -> Event/Claim -> Constraint -> LeverageMap",
    praxisUse: "Builds a policy memo section separating security pressure, integration commitments, and civilian-risk evidence.",
  },
  {
    source: "UN Security Council, Apr. 22 2026",
    specificBit:
      "The meeting framed Syria's transition as fragile under regional war pressure, making escalation a temporal risk episode rather than generic context.",
    graphObjects: ["RegionalWarRisk", "FragileTransition", "ReportingWindow", "RecoveryConstraint"],
    graphPath: "Source -> Episode -> RegionalRisk -> TransitionConstraint -> ChangedSince",
    praxisUse: "Creates a timeline update and flags which recommendations changed after the April reporting window.",
  },
  {
    source: "OFAC / Treasury, May 2025",
    specificBit:
      "GL 25 authorized broad Syria-related transactions while preserving compliance checks and political conditions tied to safe haven and minority protection.",
    graphObjects: ["GeneralLicense25", "AuthorizedActivity", "ComplianceBoundary", "PoliticalCondition"],
    graphPath: "SanctionsAuthority -> License -> AuthorizedActivity -> ResidualRisk -> ReviewQueue",
    praxisUse: "Supports sanctions-aware drafting: what is allowed, what remains risky, and what counsel should review.",
  },
  {
    source: "Project Gutenberg, War and Peace",
    specificBit:
      "A long public-domain text can be split into scenes and episodes, connecting Pierre, Natasha, Andrei, Napoleon, Borodino, Moscow, and Tolstoy's causality claims.",
    graphObjects: ["SceneEvidence", "BattleEpisode", "IdentityShift", "NarrativeClaim", "CausalClaim"],
    graphPath: "Chapter -> Scene -> Evidence -> ActorState -> CausalClaim -> InterpretationReview",
    praxisUse: "Generates reading guides, conflict maps, character-arc analysis, and evidence-backed essay drafts.",
  },
];

const internalDocumentExamples = [
  {
    title: "Ministerial briefing note",
    kind: "internal policy memo",
    storedAs: "Document -> SourceChunk -> Claim -> PolicyOption -> Evidence",
    captures: "recommendations, assumptions, contested claims, owners, deadlines, and source-backed objections",
    praxisOutput: "briefing draft, decision memo, talking points, and red-team questions",
  },
  {
    title: "Sanctions compliance worksheet",
    kind: "legal / finance review",
    storedAs: "Project -> Counterparty -> Beneficiary -> LicenseCheck -> ResidualRisk",
    captures: "allowed activities, blocked parties, remaining restrictions, bank-risk notes, and review status",
    praxisOutput: "compliance summary, risk register, counsel review packet, and implementation checklist",
  },
  {
    title: "Field interview digest",
    kind: "human source / field note",
    storedAs: "Interview -> EvidenceSpan -> ActorClaim -> Confidence -> ReviewFlag",
    captures: "who said what, when it was observed, contradiction with other sources, and reliability caveats",
    praxisOutput: "collection gap list, confidence notes, source caveat paragraph, and follow-up interview questions",
  },
  {
    title: "Negotiation transcript",
    kind: "mediation record",
    storedAs: "Transcript -> Commitment -> TrustState -> Guarantee -> ImplementationRisk",
    captures: "offers, commitments, hidden constraints, trust injuries, proposed guarantees, and sequencing",
    praxisOutput: "mediator brief, options table, guarantee design, and implementation timeline",
  },
  {
    title: "Book chapter extraction sheet",
    kind: "Gutenberg / literary analysis",
    storedAs: "Chapter -> Scene -> Actor -> Commitment -> CausalClaim -> Evidence",
    captures: "character relations, conflictual commitments, scene evidence, interpretive claims, and episode order",
    praxisOutput: "seminar guide, essay plan, quote map, and debate questions",
  },
];

const praxisToolchain = [
  {
    tool: "Situation Brief",
    input: "actor_profile + leverage_map + timeline",
    output: "A concise PRAXIS brief with source-backed claims, weak assumptions, and decision constraints.",
  },
  {
    tool: "Drafting Studio",
    input: "claim graph + evidence spans + policy options",
    output: "Memos, talking points, strategy notes, and footnoted analysis that can trace every assertion.",
  },
  {
    tool: "Red-Team Review",
    input: "low-confidence edges + missing provenance + causal claims",
    output: "Challenge questions, contradiction map, and review queue for analysts or counsel.",
  },
  {
    tool: "Negotiation Planner",
    input: "interests + commitments + guarantees + trust states",
    output: "Sequencing plan, credible guarantees, risk triggers, and mediation openings.",
  },
  {
    tool: "Benchmark Judge",
    input: "baseline LLM answer + graph-grounded answer + rubric",
    output: "Scorecard for provenance, temporal correctness, causal discipline, and actionability.",
  },
];

const praxisRelaySteps = [
  { label: "Research", detail: "UN, EU, Treasury, SCR, books", icon: FileText },
  { label: "Graph", detail: "source_ids, spans, episodes, edges", icon: Network },
  { label: "Reason", detail: "Cozo rules + Neo4j traversals", icon: Cpu },
  { label: "PRAXIS", detail: "briefs, drafts, plans, review", icon: Brain },
  { label: "Action", detail: "decisions, benchmarks, handoff", icon: Zap },
];

const domainOntologyExamples = [
  {
    domain: "Conflict Resolution",
    lens: "Interest, constraint, commitment, trust injury, guarantee, escalation pathway",
    example: "SDF integration is represented as a security architecture problem, not only an actor relationship.",
  },
  {
    domain: "Economic Development",
    lens: "Capital flow, compliance risk, beneficiary, project dependency, service delivery, reform condition",
    example: "A reconstruction project links to sanctions relief, procurement risk, and local legitimacy outcomes.",
  },
  {
    domain: "Statecraft",
    lens: "Recognition, coercive leverage, legitimacy, external patron, veto point, diplomatic sequence",
    example: "EU re-engagement and Israeli security pressure become separate levers on the same transition graph.",
  },
  {
    domain: "Book / Narrative Analysis",
    lens: "Character, scene, commitment, secret, norm, failed mediation, causal episode",
    example: "A novel becomes a conflict graph where scene evidence supports escalation and mediation claims.",
  },
  {
    domain: "Organizational Strategy",
    lens: "Stakeholder, incentive, blocker, decision right, dependency, implementation risk",
    example: "A company reorg can be queried like a situation: who blocks, who benefits, what changed, and why.",
  },
  {
    domain: "Legal / Policy Implementation",
    lens: "Rule, obligation, exception, affected party, evidence, enforcement path",
    example: "A policy memo becomes a graph of obligations, exceptions, enforcement risks, and affected groups.",
  },
];

const mediaBackedEdges = [
  {
    source: "UN brief",
    edge: "violence_risk CONSTRAINS political_transition",
    why: "Separates immediate security risk from long-term constitutional design.",
  },
  {
    source: "Security Council Report",
    edge: "southern_security_pressure AFFECTS recognition_strategy",
    why: "Makes Israeli and regional security concerns queryable instead of burying them in narrative prose.",
  },
  {
    source: "Reuters",
    edge: "eu_reengagement ENABLES trade_security_cooperation",
    why: "Turns a diplomatic news item into incentives, conditions, and follow-up verification tasks.",
  },
  {
    source: "Brookings",
    edge: "sanctions_adjustment ENABLES reconstruction_but_requires_risk_controls",
    why: "Captures that economic opening and compliance exposure are simultaneous, not contradictory.",
  },
  {
    source: "FDD",
    edge: "foreign_investment CREATES terror_finance_review_queue",
    why: "Forces high-risk reconstruction claims into a reviewable compliance layer.",
  },
  {
    source: "CFR",
    edge: "isis_detention_risk CONSTRAINS sdf_integration",
    why: "Connects counterterrorism, detention facilities, and the political bargain.",
  },
];

const benchmarkRubricDetails = [
  {
    criterion: "Provenance coverage",
    baselineFailure: "Mentions Syria context without pointing to source-backed graph objects.",
    graphExpectation: "Returns object IDs, source_ids, evidence spans, confidence, and observed_at.",
  },
  {
    criterion: "Temporal correctness",
    baselineFailure: "Mixes legacy Assad-era constraints with current post-Assad transition claims.",
    graphExpectation: "Separates legacy, transition, SDF integration, southern security, and sanctions episodes.",
  },
  {
    criterion: "Causal discipline",
    baselineFailure: "Treats events that happen near each other as causal.",
    graphExpectation: "Marks causal claims only when evidence supports trigger, mechanism, and confidence.",
  },
  {
    criterion: "Leverage precision",
    baselineFailure: "Lists powerful actors without explaining channels of influence.",
    graphExpectation: "Maps leverage type: sanctions, borders, recognition, military pressure, funding, legitimacy.",
  },
  {
    criterion: "Decision usefulness",
    baselineFailure: "Produces a polished brief but no review queue or next action.",
    graphExpectation: "Returns blockers, weak assumptions, missing sources, and the next expert question.",
  },
];

const documentBuildWorkflow = [
  {
    action: "Read this",
    detail: "Load source packs: UN briefings, Security Council forecasts, CFR tracker, or book chapters.",
  },
  {
    action: "Check this",
    detail: "Detect missing source IDs, weak evidence, duplicated chunks, time ambiguity, and unsupported claims.",
  },
  {
    action: "Structure this",
    detail: "Map text into Actor, Claim, Constraint, Leverage, Event, Narrative, Evidence, and temporal objects.",
  },
  {
    action: "Ask this",
    detail: "Generate expert queries: leverage, indirect constraints, timeline, provenance, causality, and review priority.",
  },
  {
    action: "Benchmark this",
    detail: "Run a plain LLM answer and a graph-grounded answer against the same rubric.",
  },
];

const benchmarkQuestionPlan = [
  {
    topic: "Syria leverage",
    generatedQuestion:
      "Which actors can materially influence the Syrian political process through sanctions, borders, military pressure, recognition, or humanitarian legitimacy?",
    evaluates: "leverage precision, external/internal constraint separation, provenance coverage",
  },
  {
    topic: "Syria political process and Israel",
    generatedQuestion:
      "How do Israeli security demands and southern Syria dynamics constrain the interim government's political process and international recognition strategy?",
    evaluates: "multi-hop constraint reasoning, temporal freshness, source traceability",
  },
  {
    topic: "Book conflict causality",
    generatedQuestion:
      "Which events in Romeo and Juliet cause escalation rather than merely occur in sequence, and what evidence supports each causal edge?",
    evaluates: "causal precision, episode ordering, quote/evidence grounding",
  },
  {
    topic: "Mediation options",
    generatedQuestion:
      "What process intervention would be plausible now, what trust or guarantee is required, and which assumptions remain weak?",
    evaluates: "intervention usefulness, uncertainty handling, review queue quality",
  },
];

const demoClicks = [
  "Open /situation-demo and start at the two-column Situation Board.",
  "Show the didactic mirror: evidence spans become canonical objects, episodes, causal claims, and graph writes.",
  "Scroll to the D3 graph and drag nodes to show the dynamic ontology layers.",
  "Open the economic sanctions ontology and explain why finance, compliance, and security have to be modeled together.",
  "Click Check health and show Neo4j, Graphiti compatibility, Cozo, Cloud SQL, and API status.",
  "Click Ingest Syria case and wait for the pipeline summary.",
  "Click Search graph, then use a returned actor id in Actor Reasoning.",
  "Close with the benchmark: plain LLM vs graph-grounded answer with provenance and temporality.",
];

const backboneSurfaces = [
  {
    title: "Ontology Picker",
    detail: "Selects policy, mediation, field-intelligence, legal, literary, or custom lenses and maps every extension back to canonical primitives.",
  },
  {
    title: "Graph Creator",
    detail: "Turns documents, briefings, transcripts, reports, and notes into Actor, Claim, Constraint, Leverage, Event, Source, and Evidence objects.",
  },
  {
    title: "Reasoning API",
    detail: "Exposes health, ingestion, graph search, actor reasoning, constraints, leverage, timeline, provenance, and changed_since endpoints.",
  },
  {
    title: "Benchmark Loop",
    detail: "Compares ordinary LLM answers against graph-grounded answers for provenance, causal precision, ambiguity handling, and actionability.",
  },
];

const situationOptions = [
  {
    name: "Syria Transition",
    type: "statecraft + security",
    objective: "Map who can stabilize, block, finance, escalate, legitimize, or verify the transition.",
  },
  {
    name: "Policy Constraint Map",
    type: "governance",
    objective: "Extract institutions, rules, veto points, fiscal limits, implementation risks, and public narratives.",
  },
  {
    name: "Mediation Case File",
    type: "negotiation",
    objective: "Separate positions from interests, commitments, trust injuries, BATNA hints, and process options.",
  },
  {
    name: "Field Situation Portal",
    type: "operations",
    objective: "Track reports, observed events, source reliability, uncertainty, collection gaps, and what changed.",
  },
];

const syriaLenses = [
  {
    name: "Political Transition",
    question: "Which actors recognize, contest, or condition the new authority?",
    graph: "Actor -> Claim -> Constraint -> Source",
  },
  {
    name: "Mediation / Integration",
    question: "What would make SDF integration credible, reversible, or blocked?",
    graph: "Actor -> Commitment -> Constraint -> Event",
  },
  {
    name: "External Leverage",
    question: "Who can apply pressure through borders, sanctions, military posture, funding, or legitimacy?",
    graph: "Actor -> Leverage -> Actor/Constraint",
  },
  {
    name: "Humanitarian Risk",
    question: "Which constraints threaten civilians, camps, return, access, women, girls, and displaced people?",
    graph: "Event -> Constraint -> Evidence -> Source",
  },
  {
    name: "Counter-ISIS / Detention",
    question: "Which facilities, territories, and armed actors create resurgence risk?",
    graph: "Actor -> Event -> Constraint -> Timeline",
  },
  {
    name: "Accountability / Legitimacy",
    question: "Where do sanctions relief, recognition, civil society, and war-crimes accountability collide?",
    graph: "Claim -> Norm -> Constraint -> Provenance",
  },
];

const canonicalRelations = [
  "ACTOR_MAKES_CLAIM",
  "CLAIM_EVIDENCED_BY_SOURCE",
  "ACTOR_HAS_INTEREST",
  "ACTOR_HAS_LEVERAGE",
  "CONSTRAINT_BLOCKS_OPTION",
  "EVENT_CHANGES_STATUS",
  "NARRATIVE_FRAMES_EVENT",
  "OBJECT_CHANGED_SINCE",
];

const queryExamples = [
  "actor_profile('Syrian Interim Government')",
  "leverage_map('SDF')",
  "indirect_constraints('Ahmed al-Sharaa')",
  "timeline(['SDF','Turkey','Israel'], start, end)",
  "provenance_trace('leverage_b678...')",
  "changed_since('2026-05-02T00:00:00Z')",
];

const fortyFiveSecondScript = [
  {
    time: "0-4s",
    line:
      "Dialectica is the graph backbone: it turns messy sources into structured, queryable knowledge.",
  },
  {
    time: "4-9s",
    line:
      "This page uses Syria as one example, but the same engine works for policy files, mediation cases, field reports, or books.",
  },
  {
    time: "9-17s",
    line:
      "Pick an expert ontology lens: statecraft, mediation, humanitarian risk, leverage, or literary conflict.",
  },
  {
    time: "17-27s",
    line:
      "The pre-digest stage chunks the sources, attaches evidence spans, and creates a configuration that Databricks, Colab, or the API can run.",
  },
  {
    time: "27-37s",
    line:
      "Neo4j stores the operational graph, Graphiti tracks time and provenance, Cozo mirrors reasoning, and Databricks benchmarks quality at scale.",
  },
  {
    time: "37-45s",
    line:
      "Now we can ask better questions: who has leverage, what blocks stabilization, what changed, and exactly which source supports the answer?",
  },
];

const fourSecondHook =
  "Dialectica turns messy Syria sources into a live, multi-layer graph you can query, verify, and benchmark.";

function MultiGraphBackboneVisual() {
  const nodeLookup = Object.fromEntries(animatedGraphNodes.map((node) => [node.id, node]));
  return (
    <div className="relative min-h-[430px] overflow-hidden rounded-lg border border-border bg-background p-5">
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-accent/60 to-transparent" />
      <div className="relative z-10 flex items-center justify-between gap-3">
        <div>
          <p className="text-sm font-semibold text-text-primary">Animated Syria Situation Graph</p>
          <p className="mt-1 max-w-2xl text-xs leading-5 text-text-secondary">
            The animation shows the same source material becoming multiple synchronized graph layers: evidence,
            operational actors, temporal episodes, leverage, constraints, and Datalog reasoning.
          </p>
        </div>
        <span className="rounded-md border border-accent/30 bg-accent/10 px-2 py-1 text-[11px] text-accent">
          live backbone
        </span>
      </div>

      <svg className="absolute inset-0 h-full w-full" aria-hidden="true">
        <defs>
          <marker id="arrow-syria" markerHeight="6" markerWidth="6" orient="auto" refX="5" refY="3">
            <path d="M0,0 L6,3 L0,6 Z" fill="rgb(94 234 212 / 0.55)" />
          </marker>
        </defs>
        {animatedGraphEdges.map(([from, to], index) => {
          const source = nodeLookup[from];
          const target = nodeLookup[to];
          if (!source || !target) return null;
          return (
            <line
              key={`${from}-${to}`}
              x1={source.x}
              y1={source.y}
              x2={target.x}
              y2={target.y}
              className="dialectica-graph-edge"
              markerEnd="url(#arrow-syria)"
              style={{ animationDelay: `${index * 0.35}s` }}
            />
          );
        })}
      </svg>

      {animatedGraphNodes.map((node, index) => (
        <div
          key={node.id}
          className="dialectica-graph-node absolute z-10 w-[132px] rounded-lg border border-border bg-surface/95 p-3 shadow-lg shadow-black/20"
          style={{ left: node.x, top: node.y, animationDelay: `${index * 0.18}s` }}
        >
          <div className="flex items-center gap-2">
            <span className={`h-2.5 w-2.5 rounded-full ${node.tone}`} />
            <p className="truncate text-xs font-semibold text-text-primary">{node.label}</p>
          </div>
          <p className="mt-1 text-[10px] uppercase tracking-wide text-text-secondary">{node.type}</p>
        </div>
      ))}

      <div className="absolute bottom-4 left-4 right-4 z-10 grid gap-2 md:grid-cols-4">
        {["source_ids", "confidence", "valid_time", "queryable_edges"].map((item) => (
          <code key={item} className="rounded-md border border-border bg-background/80 px-2 py-1 text-[10px] text-accent">
            {item}
          </code>
        ))}
      </div>
    </div>
  );
}

function DynamicOntologyVisual() {
  return (
    <div className="rounded-lg border border-border bg-background p-5">
      <div className="flex flex-col justify-between gap-3 md:flex-row md:items-center">
        <div>
          <p className="text-sm font-semibold text-text-primary">Dynamic Ontology Lens Shift</p>
          <p className="mt-1 max-w-2xl text-xs leading-5 text-text-secondary">
            Dialectica does not freeze one schema. It chooses a lens, captures case-specific structure,
            then maps every custom concept back to canonical graph primitives.
          </p>
        </div>
        <span className="rounded-md bg-fuchsia-500/10 px-2 py-1 text-[11px] text-fuchsia-200">ontology runtime</span>
      </div>
      <div className="mt-5 grid gap-3 lg:grid-cols-4">
        {ontologyFlow.map((stage, index) => (
          <div
            key={stage.stage}
            className="dialectica-ontology-stage rounded-lg border border-border bg-surface p-4"
            style={{ animationDelay: `${index * 0.3}s` }}
          >
            <p className="text-xs font-semibold uppercase tracking-wide text-accent">{stage.stage}</p>
            <div className="mt-3 flex flex-wrap gap-2">
              {stage.tokens.map((token, tokenIndex) => (
                <span
                  key={token}
                  className="dialectica-token rounded-md bg-background px-2 py-1 text-[11px] text-text-secondary"
                  style={{ animationDelay: `${index * 0.35 + tokenIndex * 0.12}s` }}
                >
                  {token}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function D3OntologyGraph() {
  const svgRef = useRef<SVGSVGElement | null>(null);
  const [activeLayer, setActiveLayer] = useState<OntologyForceNode["layer"] | "all">("all");
  const [selectedNode, setSelectedNode] = useState<OntologyForceNode | null>(null);
  const [graphVersion, setGraphVersion] = useState(0);
  const layerColors: Record<OntologyForceNode["layer"], string> = {
    source: "#38bdf8",
    ontology: "#2dd4bf",
    case: "#f59e0b",
    engine: "#a78bfa",
    query: "#f472b6",
    temporal: "#fbbf24",
    causal: "#fb7185",
    benchmark: "#22c55e",
  };

  useEffect(() => {
    const svgElement = svgRef.current;
    if (!svgElement) return;

    const width = 900;
    const height = 430;
    const nodes = forceOntologyNodes.map((node) => ({ ...node }));
    const links = forceOntologyLinks.map((link) => ({ ...link }));
    const activeNodeIds = new Set(nodes.filter((node) => activeLayer === "all" || node.layer === activeLayer).map((node) => node.id));
    const linkTouchesActive = (item: OntologyForceLink) => {
      const sourceId = typeof item.source === "string" ? item.source : item.source.id;
      const targetId = typeof item.target === "string" ? item.target : item.target.id;
      return activeLayer === "all" || activeNodeIds.has(sourceId) || activeNodeIds.has(targetId);
    };

    const svg = d3.select(svgElement);
    svg.selectAll("*").remove();
    svg.attr("viewBox", `0 0 ${width} ${height}`);

    const root = svg.append("g");
    root
      .append("rect")
      .attr("width", width)
      .attr("height", height)
      .attr("rx", 8)
      .attr("fill", "#020617");

    const defs = root.append("defs");
    const glow = defs.append("filter").attr("id", "ontology-glow");
    glow.append("feGaussianBlur").attr("stdDeviation", "3").attr("result", "coloredBlur");
    const merge = glow.append("feMerge");
    merge.append("feMergeNode").attr("in", "coloredBlur");
    merge.append("feMergeNode").attr("in", "SourceGraphic");
    defs
      .append("marker")
      .attr("id", "ontology-arrow")
      .attr("viewBox", "0 -5 10 10")
      .attr("refX", 18)
      .attr("refY", 0)
      .attr("markerWidth", 5)
      .attr("markerHeight", 5)
      .attr("orient", "auto")
      .append("path")
      .attr("d", "M0,-5L10,0L0,5")
      .attr("fill", "#475569")
      .attr("opacity", 0.8);

    const linkGroup = root.append("g").attr("stroke", "#334155").attr("stroke-opacity", 0.75);
    const nodeGroup = root.append("g");
    const labelGroup = root.append("g");
    const zoom = d3
      .zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.65, 2.1])
      .on("zoom", (event) => {
        root.attr("transform", event.transform);
      });
    svg.call(zoom);

    const simulation = d3
      .forceSimulation<OntologyForceNode>(nodes)
      .force(
        "link",
        d3
          .forceLink<OntologyForceNode, OntologyForceLink>(links)
          .id((node) => node.id)
          .distance((link) => (String(link.relation).includes("memory") ? 92 : 70))
          .strength(0.46),
      )
      .force("charge", d3.forceManyBody().strength(-145))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide<OntologyForceNode>().radius((node) => node.radius + 6));

    const link = linkGroup
      .selectAll("line")
      .data(links)
      .join("line")
      .attr("stroke-width", 1.4)
      .attr("stroke-dasharray", "4 6")
      .attr("marker-end", "url(#ontology-arrow)")
      .attr("opacity", (item) => (linkTouchesActive(item) ? 0.9 : 0.12));

    const relation = labelGroup
      .selectAll("text.relation")
      .data(links)
      .join("text")
      .attr("class", "relation")
      .attr("fill", "#64748b")
      .attr("font-size", 9)
      .attr("text-anchor", "middle")
      .attr("opacity", (item) => (linkTouchesActive(item) ? 0.95 : 0.1))
      .text((linkItem) => linkItem.relation);

    const dragBehavior = d3
      .drag<SVGGElement, OntologyForceNode>()
      .on("start", (event, dragged) => {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        dragged.fx = dragged.x;
        dragged.fy = dragged.y;
      })
      .on("drag", (event, dragged) => {
        dragged.fx = event.x;
        dragged.fy = event.y;
      })
      .on("end", (event, dragged) => {
        if (!event.active) simulation.alphaTarget(0);
        dragged.fx = null;
        dragged.fy = null;
      });

    const node = nodeGroup
      .selectAll<SVGGElement, OntologyForceNode>("g")
      .data(nodes)
      .join("g")
      .attr("cursor", "grab")
      .attr("opacity", (item) => (activeLayer === "all" || item.layer === activeLayer ? 1 : 0.22))
      .on("click", (_event, item) => setSelectedNode(item))
      .call(dragBehavior);

    node.append("title").text((item) => `${item.label} (${item.layer})`);

    node
      .append("circle")
      .attr("r", (item) => item.radius)
      .attr("fill", (item) => layerColors[item.layer])
      .attr("fill-opacity", 0.2)
      .attr("stroke", (item) => layerColors[item.layer])
      .attr("stroke-width", 1.8)
      .attr("filter", "url(#ontology-glow)");

    node
      .append("text")
      .attr("text-anchor", "middle")
      .attr("dy", 3)
      .attr("fill", "#e2e8f0")
      .attr("font-size", 10)
      .attr("font-weight", 650)
      .text((item) => (item.label.length > 18 ? `${item.label.slice(0, 16)}...` : item.label));

    const layerLegend = root
      .append("g")
      .attr("transform", "translate(18, 24)")
      .selectAll("g")
      .data(Object.entries(layerColors))
      .join("g")
      .attr("transform", (_item, index) => `translate(0, ${index * 22})`);

    layerLegend.append("circle").attr("r", 5).attr("fill", ([, color]) => color);
    layerLegend
      .append("text")
      .attr("x", 12)
      .attr("y", 4)
      .attr("fill", "#94a3b8")
      .attr("font-size", 11)
      .text(([name]) => name);

    simulation.on("tick", () => {
      link
        .attr("x1", (item) => (item.source as OntologyForceNode).x ?? 0)
        .attr("y1", (item) => (item.source as OntologyForceNode).y ?? 0)
        .attr("x2", (item) => (item.target as OntologyForceNode).x ?? 0)
        .attr("y2", (item) => (item.target as OntologyForceNode).y ?? 0);

      relation
        .attr("x", (item) => (((item.source as OntologyForceNode).x ?? 0) + ((item.target as OntologyForceNode).x ?? 0)) / 2)
        .attr("y", (item) => (((item.source as OntologyForceNode).y ?? 0) + ((item.target as OntologyForceNode).y ?? 0)) / 2);

      node.attr("transform", (item) => `translate(${item.x ?? 0},${item.y ?? 0})`);
    });

    const pulse = d3.interval(() => {
      node
        .select("circle")
        .transition()
        .duration(650)
        .attr("fill-opacity", 0.36)
        .transition()
        .duration(650)
        .attr("fill-opacity", 0.18);
      simulation.alpha(0.18).restart();
    }, 2300);

    return () => {
      pulse.stop();
      simulation.stop();
      svg.selectAll("*").remove();
    };
  }, [activeLayer, graphVersion]);

  const activeNodes = activeLayer === "all" ? forceOntologyNodes : forceOntologyNodes.filter((node) => node.layer === activeLayer);
  const activeNodeIds = new Set(activeNodes.map((node) => node.id));
  const activeEdgeCount =
    activeLayer === "all"
      ? forceOntologyLinks.length
      : forceOntologyLinks.filter((link) => activeNodeIds.has(String(link.source)) || activeNodeIds.has(String(link.target))).length;

  return (
    <div id="d3-ontology" className="scroll-mt-6 rounded-lg border border-border bg-background p-5">
      <div className="flex flex-col justify-between gap-3 md:flex-row md:items-center">
        <div>
          <p className="text-sm font-semibold text-text-primary">D3 Dynamic Ontology Graph</p>
          <p className="mt-1 max-w-3xl text-xs leading-5 text-text-secondary">
            This is a real D3 force graph with 50+ nodes and dense edges. Drag nodes while recording to show
            sources becoming canonical objects, temporal/causal layers, case lenses, graph engines,
            expert queries, and benchmark metrics.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <span className="rounded-md bg-accent/10 px-2 py-1 text-[11px] text-accent">
            {activeNodes.length} nodes / {activeEdgeCount} edges
          </span>
          <button
            onClick={() => {
              setActiveLayer("all");
              setSelectedNode(null);
              setGraphVersion((version) => version + 1);
            }}
            className="rounded-md border border-border bg-surface px-2 py-1 text-[11px] text-text-secondary hover:border-border-hover"
          >
            reset graph
          </button>
        </div>
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        <button
          onClick={() => setActiveLayer("all")}
          className={`rounded-md border px-2 py-1 text-[11px] ${
            activeLayer === "all" ? "border-accent bg-accent/10 text-accent" : "border-border bg-surface text-text-secondary"
          }`}
        >
          all layers
        </button>
        {Object.entries(layerColors).map(([layer, color]) => (
          <button
            key={layer}
            onClick={() => setActiveLayer(layer as OntologyForceNode["layer"])}
            className={`rounded-md border px-2 py-1 text-[11px] ${
              activeLayer === layer ? "border-accent bg-accent/10 text-accent" : "border-border bg-surface text-text-secondary"
            }`}
          >
            <span className="mr-1 inline-block h-2 w-2 rounded-full" style={{ backgroundColor: color }} />
            {layer}
          </button>
        ))}
      </div>
      <svg ref={svgRef} className="mt-4 h-[430px] w-full overflow-hidden rounded-lg border border-border" role="img" />
      <div className="mt-3 grid gap-3 md:grid-cols-[0.7fr_1.3fr]">
        <div className="rounded-lg border border-border bg-surface p-3">
          <p className="text-xs font-semibold text-text-primary">Selected node</p>
          <p className="mt-1 text-xs leading-5 text-text-secondary">
            {selectedNode ? `${selectedNode.label} (${selectedNode.layer})` : "Click or drag a node during the recording."}
          </p>
        </div>
        <div className="rounded-lg border border-border bg-surface p-3">
          <p className="text-xs font-semibold text-text-primary">Operator move</p>
          <p className="mt-1 text-xs leading-5 text-text-secondary">
            Filter temporal, causal, source, or engine layers to show that the graph is not a generic mind map.
            It is a layered execution structure for ingestion, memory, reasoning, and benchmark answers.
          </p>
        </div>
      </div>
    </div>
  );
}

function ExtractionPipelineVisual() {
  return (
    <div className="rounded-lg border border-border bg-background p-5">
      <div className="flex flex-col justify-between gap-3 md:flex-row md:items-center">
        <div>
          <p className="text-sm font-semibold text-text-primary">Animated Extraction Pipeline</p>
          <p className="mt-1 max-w-3xl text-xs leading-5 text-text-secondary">
            The demo shows a realistic route: a source pack is pre-digested, a configuration is generated,
            extraction can run in Databricks or Colab, then the graph engine writes Neo4j, Graphiti, Cozo,
            Cloud SQL audit records, and benchmark outputs.
          </p>
        </div>
        <span className="rounded-md border border-violet-500/30 bg-violet-500/10 px-2 py-1 text-[11px] text-violet-200">
          Databricks + Colab ready
        </span>
      </div>
      <div className="relative mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-7">
        {extractionPipeline.map((step, index) => {
          const Icon = step.icon;
          return (
            <div
              key={step.stage}
              className="dialectica-pipeline-card relative rounded-lg border border-border bg-surface p-4"
              style={{ animationDelay: `${index * 0.18}s` }}
            >
              {index < extractionPipeline.length - 1 && <span className="dialectica-pipeline-beam hidden xl:block" />}
              <div className="rounded-md bg-accent/10 p-2 text-accent">
                <Icon size={16} />
              </div>
              <p className="mt-3 text-sm font-semibold text-text-primary">{step.stage}</p>
              <p className="mt-2 text-xs leading-5 text-text-secondary">{step.detail}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function BenchmarkComparisonVisual() {
  return (
    <div className="rounded-lg border border-border bg-background p-5">
      <div className="flex flex-col justify-between gap-3 md:flex-row md:items-center">
        <div>
          <p className="text-sm font-semibold text-text-primary">Structure Benchmark</p>
          <p className="mt-1 max-w-3xl text-xs leading-5 text-text-secondary">
            Dialectica is evaluated against ordinary LLM summarization. The point is not just a prettier
            answer. The point is provenance, causality, leverage, and reviewable structure.
          </p>
        </div>
        <span className="rounded-md bg-emerald-500/10 px-2 py-1 text-[11px] text-emerald-200">
          baseline vs graph
        </span>
      </div>
      <div className="mt-5 grid gap-4 lg:grid-cols-2">
        {benchmarkComparison.map((item) => (
          <div key={item.metric} className="rounded-lg border border-border bg-surface p-4">
            <div className="flex items-center justify-between gap-3">
              <p className="text-sm font-semibold text-text-primary">{item.metric}</p>
              <p className="text-xs text-accent">+{item.dialectica - item.baseline} pts</p>
            </div>
            <div className="mt-3 space-y-2">
              <div>
                <div className="flex justify-between text-[11px] text-text-secondary">
                  <span>Plain LLM</span>
                  <span>{item.baseline}</span>
                </div>
                <div className="mt-1 h-2 overflow-hidden rounded-full bg-background">
                  <div className="dialectica-benchmark-bar bg-warning/80" style={{ width: `${item.baseline}%` }} />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-[11px] text-text-secondary">
                  <span>Dialectica graph</span>
                  <span>{item.dialectica}</span>
                </div>
                <div className="mt-1 h-2 overflow-hidden rounded-full bg-background">
                  <div className="dialectica-benchmark-bar bg-accent" style={{ width: `${item.dialectica}%` }} />
                </div>
              </div>
            </div>
            <p className="mt-3 text-xs leading-5 text-text-secondary">{item.why}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function PraxisRelayVisual() {
  return (
    <div className="rounded-lg border border-border bg-background p-5">
      <div className="flex flex-col justify-between gap-3 md:flex-row md:items-center">
        <div>
          <p className="text-sm font-semibold text-text-primary">Animated PRAXIS Knowledge Relay</p>
          <p className="mt-1 max-w-3xl text-xs leading-5 text-text-secondary">
            The graph is not the final screen. It becomes the substrate for PRAXIS tools: analysis, drafting,
            review, negotiation planning, and benchmarked decision support.
          </p>
        </div>
        <span className="rounded-md border border-accent/30 bg-accent/10 px-2 py-1 text-[11px] text-accent">
          graph stored once, used everywhere
        </span>
      </div>
      <div className="relative mt-5 grid gap-3 md:grid-cols-5">
        {praxisRelaySteps.map((step, index) => {
          const Icon = step.icon;
          return (
            <div
              key={step.label}
              className="dialectica-pipeline-card relative rounded-lg border border-border bg-surface p-4"
              style={{ animationDelay: `${index * 0.16}s` }}
            >
              {index < praxisRelaySteps.length - 1 && <span className="dialectica-pipeline-beam hidden md:block" />}
              <div className="flex items-center gap-3">
                <div className="rounded-md bg-accent/10 p-2 text-accent">
                  <Icon size={17} />
                </div>
                <div>
                  <p className="text-sm font-semibold text-text-primary">{step.label}</p>
                  <p className="mt-1 text-[11px] leading-4 text-text-secondary">{step.detail}</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
      <div className="mt-5 grid gap-3 md:grid-cols-4">
        {["provenance_trace", "timeline", "review_queue", "draft_packet"].map((item, index) => (
          <code
            key={item}
            className="dialectica-token rounded-md border border-border bg-surface px-3 py-2 text-[11px] text-accent"
            style={{ animationDelay: `${index * 0.18}s` }}
          >
            {item}
          </code>
        ))}
      </div>
    </div>
  );
}

type ActionState = {
  status: "idle" | "loading" | "ok" | "error";
  label?: string;
  data?: Record<string, unknown>;
  message?: string;
};

function authHeaders(apiKey: string) {
  return {
    "Content-Type": "application/json",
    ...(apiKey ? { "X-API-Key": apiKey } : {}),
  };
}

async function readPayload(response: Response): Promise<Record<string, unknown>> {
  try {
    return (await response.json()) as Record<string, unknown>;
  } catch {
    return {};
  }
}

function messageFromPayload(payload: Record<string, unknown>, fallback: string) {
  if (typeof payload.error === "string") return payload.error;
  if (typeof payload.detail === "string") return payload.detail;
  if (payload.detail) return JSON.stringify(payload.detail);
  return fallback;
}

function JsonPanel({ state, empty }: { state: ActionState; empty: string }) {
  if (state.status === "idle") {
    return <p className="text-sm leading-6 text-text-secondary">{empty}</p>;
  }
  if (state.status === "loading") {
    return <p className="text-sm text-accent">Running...</p>;
  }
  if (state.status === "error") {
    return (
      <div>
        <p className="text-sm font-semibold text-warning">Action failed</p>
        <p className="mt-1 text-xs leading-5 text-text-secondary">{state.message}</p>
      </div>
    );
  }
  return (
    <pre className="max-h-[320px] overflow-auto rounded-lg border border-border bg-background p-4 text-xs leading-5 text-text-secondary">
      <code>{JSON.stringify(state.data, null, 2)}</code>
    </pre>
  );
}

export default function SyriaDemoConsole() {
  const [apiKey, setApiKey] = useState("");
  const [searchQuery, setSearchQuery] = useState("Syria");
  const [actorId, setActorId] = useState("");
  const [selectedCaseId, setSelectedCaseId] = useState("syria");
  const [selectedLens, setSelectedLens] = useState("policy-statecraft");
  const [executionTarget, setExecutionTarget] = useState("databricks");
  const [healthState, setHealthState] = useState<ActionState>({ status: "idle" });
  const [ingestState, setIngestState] = useState<ActionState>({ status: "idle" });
  const [searchState, setSearchState] = useState<ActionState>({ status: "idle" });
  const [runsState, setRunsState] = useState<ActionState>({ status: "idle" });
  const [reasoningState, setReasoningState] = useState<ActionState>({ status: "idle" });
  const [operatorNotice, setOperatorNotice] = useState("");

  const apiUrl = useMemo(() => getApiUrl(), []);
  const selectedCase = useMemo(
    () => demoCaseConfigs.find((item) => item.id === selectedCaseId) ?? demoCaseConfigs[0],
    [selectedCaseId],
  );
  const generatedConfig = useMemo(
    () => ({
      dialectica_config_version: "2026-05-demo",
      case_id: selectedCase.caseId,
      workspace_id: selectedCase.workspaceId,
      source_pack: selectedCase.sourcePack,
      source_type: selectedCase.sourceType,
      execution_target: executionTarget,
      ontology_lens: selectedLens,
      canonical_objects: selectedCase.canonicalObjects,
      graph_layers: ["source_evidence", "neo4j_operational", "graphiti_temporal", "cozo_reasoning", "databricks_benchmark"],
      required_provenance: ["source_ids", "confidence", "created_at", "valid_from", "valid_to", "evidence_span"],
      query_plan: [
        selectedCase.defaultQuery,
        "What changed since the last run?",
        "Which claims are weakly sourced?",
        "What does the graph-grounded answer prove that a baseline LLM cannot trace?",
      ],
      outputs: ["graph_objects", "edge_list", "review_queue", "benchmark_report", "colab_analysis_pack"],
      api_base_url: apiUrl,
    }),
    [apiUrl, executionTarget, selectedCase, selectedLens],
  );
  const generatedConfigText = useMemo(() => JSON.stringify(generatedConfig, null, 2), [generatedConfig]);

  useEffect(() => {
    const saved = window.localStorage.getItem("dialectica_api_key") ?? "";
    setApiKey(saved);
  }, []);

  function saveApiKey() {
    window.localStorage.setItem("dialectica_api_key", apiKey.trim());
    setOperatorNotice(apiKey.trim() ? "API key saved in this browser." : "API key cleared.");
  }

  async function copyGeneratedConfig() {
    await navigator.clipboard.writeText(generatedConfigText);
    setOperatorNotice(`${selectedCase.label} config copied.`);
  }

  async function checkHealth() {
    setHealthState({ status: "loading" });
    try {
      const response = await fetch(`${apiUrl}/health`, { cache: "no-store" });
      const payload = await readPayload(response);
      setHealthState(response.ok ? { status: "ok", data: { ...payload, httpStatus: response.status } } : {
        status: "error",
        message: messageFromPayload(payload, "Health check failed."),
      });
    } catch (error) {
      setHealthState({ status: "error", message: error instanceof Error ? error.message : "Health check failed." });
    }
  }

  async function ingestCase() {
    setIngestState({ status: "loading" });
    try {
      const response = await fetch(`${apiUrl}/ingest/text`, {
        method: "POST",
        headers: authHeaders(apiKey),
        body: JSON.stringify({
          workspace_id: WORKSPACE_ID,
          source_title: "Syria transition live demo source pack",
          source_type: "public-current-affairs-brief",
          objective: OBJECTIVE,
          ontology_profile: "policy-analysis",
          text: SYRIA_TEXT,
        }),
      });
      const payload = await readPayload(response);
      if (!response.ok) {
        setIngestState({ status: "error", message: messageFromPayload(payload, "Ingestion failed.") });
        return;
      }
      setIngestState({ status: "ok", data: payload });
      await Promise.all([searchGraph(), loadRuns()]);
    } catch (error) {
      setIngestState({ status: "error", message: error instanceof Error ? error.message : "Ingestion failed." });
    }
  }

  async function searchGraph() {
    setSearchState({ status: "loading" });
    try {
      const params = new URLSearchParams({ q: searchQuery.trim() || "Syria", workspace_id: WORKSPACE_ID, limit: "16" });
      const response = await fetch(`${apiUrl}/graph/search?${params.toString()}`, {
        cache: "no-store",
        headers: authHeaders(apiKey),
      });
      const payload = await readPayload(response);
      if (!response.ok) {
        setSearchState({ status: "error", message: messageFromPayload(payload, "Search failed.") });
        return;
      }
      setSearchState({ status: "ok", data: payload });
    } catch (error) {
      setSearchState({ status: "error", message: error instanceof Error ? error.message : "Search failed." });
    }
  }

  async function loadRuns() {
    setRunsState({ status: "loading" });
    try {
      const params = new URLSearchParams({ workspace_id: WORKSPACE_ID, limit: "8" });
      const response = await fetch(`${apiUrl}/pipeline/runs?${params.toString()}`, {
        cache: "no-store",
        headers: authHeaders(apiKey),
      });
      const payload = await readPayload(response);
      if (!response.ok) {
        setRunsState({ status: "error", message: messageFromPayload(payload, "Run history failed.") });
        return;
      }
      setRunsState({ status: "ok", data: payload });
    } catch (error) {
      setRunsState({ status: "error", message: error instanceof Error ? error.message : "Run history failed." });
    }
  }

  async function reasonActor() {
    if (!actorId.trim()) {
      setReasoningState({ status: "error", message: "Paste an actor id from search results first." });
      return;
    }
    setReasoningState({ status: "loading" });
    try {
      const params = new URLSearchParams({ workspace_id: WORKSPACE_ID });
      const response = await fetch(`${apiUrl}/reasoning/actor/${encodeURIComponent(actorId.trim())}?${params.toString()}`, {
        cache: "no-store",
        headers: authHeaders(apiKey),
      });
      const payload = await readPayload(response);
      if (!response.ok) {
        setReasoningState({ status: "error", message: messageFromPayload(payload, "Actor reasoning failed.") });
        return;
      }
      setReasoningState({ status: "ok", data: payload });
    } catch (error) {
      setReasoningState({ status: "error", message: error instanceof Error ? error.message : "Actor reasoning failed." });
    }
  }

  return (
    <div className="space-y-6 p-6">
      <section className="rounded-lg border border-border bg-surface p-5">
        <div className="flex flex-col justify-between gap-4 xl:flex-row xl:items-start">
          <div>
            <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-accent">
              <Globe2 size={15} />
              Dialectica situation graph cockpit
            </div>
            <h1 className="mt-3 text-3xl font-semibold text-text-primary">Dialectica Situation Graph Demo</h1>
            <p className="mt-3 max-w-4xl text-sm leading-6 text-text-secondary">
              One page for the recording: Dialectica as the reusable graph reasoning backbone, with Syria
              policy/statecraft and book conflict analysis as concrete situation-building examples. The same
              page shows ontology selection, semantic layers, source-grounded ingestion, graph search,
              reasoning, benchmarks, configuration handoff, Databricks, and Colab-style analysis.
            </p>
          </div>
          <div className="rounded-lg border border-border bg-background p-4 text-xs leading-5 text-text-secondary">
            <p className="font-semibold text-text-primary">Live endpoints</p>
            <p className="mt-2">API: <code className="text-accent">{apiUrl}</code></p>
            <p>Workspace: <code className="text-accent">{WORKSPACE_ID}</code></p>
            <p>Case: <code className="text-accent">{CASE_ID}</code></p>
          </div>
        </div>
        <div className="mt-5 grid gap-3 lg:grid-cols-[0.95fr_1.05fr]">
          <div className="rounded-lg border border-border bg-background p-4">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <p className="text-sm font-semibold text-text-primary">Recording cockpit</p>
              <span className="rounded-md bg-emerald-500/10 px-2 py-1 text-[11px] text-emerald-200">
                deployed + API wired
              </span>
            </div>
            <div className="mt-3 grid gap-2 sm:grid-cols-2">
              {demoReadinessChecks.map((item) => (
                <div key={item.label} className="rounded-md bg-surface p-3">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 size={14} className="text-emerald-300" />
                    <p className="text-xs font-semibold text-text-primary">{item.label}</p>
                  </div>
                  <p className="mt-2 text-[11px] leading-5 text-text-secondary">{item.detail}</p>
                </div>
              ))}
            </div>
          </div>
          <div className="rounded-lg border border-border bg-background p-4">
            <p className="text-sm font-semibold text-text-primary">Jump to the parts that sell the product</p>
            <div className="mt-3 flex flex-wrap gap-2">
              {demoJumpLinks.map((link) => (
                <a
                  key={link.href}
                  href={link.href}
                  className="rounded-md border border-border bg-surface px-3 py-2 text-xs text-text-secondary transition-colors hover:border-border-hover hover:text-text-primary"
                >
                  {link.label}
                </a>
              ))}
            </div>
            <div className="mt-4 rounded-md border border-border bg-surface p-3">
              <p className="text-xs font-semibold text-text-primary">Current demo case</p>
              <p className="mt-1 text-xs leading-5 text-text-secondary">
                {selectedCase.label} · {selectedLens} · {executionTarget}
              </p>
              {operatorNotice && <p className="mt-2 text-[11px] text-accent">{operatorNotice}</p>}
            </div>
          </div>
        </div>
      </section>

      <section className="rounded-lg border border-border bg-surface p-5">
        <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
          <Route size={18} className="text-accent" />
          How To Read The Demo
        </h2>
        <p className="mt-2 max-w-4xl text-sm leading-6 text-text-secondary">
          The page is organized as a situation-building workflow. Start with the visual backbone, then inspect
          the ontology, build a config, read/check/structure documents, query the graph, and benchmark the answer.
        </p>
        <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          {pageMap.map((item) => (
            <div key={item.title} className="rounded-lg border border-border bg-background p-4">
              <p className="text-sm font-semibold text-text-primary">{item.title}</p>
              <p className="mt-2 text-xs leading-5 text-text-secondary">{item.detail}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.08fr_0.92fr]">
        <div className="rounded-lg border border-border bg-surface p-5">
          <div className="flex flex-col justify-between gap-3 lg:flex-row lg:items-center">
            <div>
              <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
                <Globe2 size={18} className="text-accent" />
                Real Situation Board
              </h2>
              <p className="mt-2 max-w-3xl text-sm leading-6 text-text-secondary">
                This side is the Syria working case. It keeps real reporting separate from interpretation:
                every node has a phase, source family, relation shape, and a reason it matters.
              </p>
            </div>
            <span className="rounded-md border border-border bg-background px-3 py-2 text-xs text-accent">
              source-backed case graph
            </span>
          </div>
          <div className="mt-5 grid gap-3 md:grid-cols-2">
            {realSituationBoard.map((item, index) => (
              <div
                key={item.node}
                className="dialectica-pipeline-card rounded-lg border border-border bg-background p-4"
                style={{ animationDelay: `${index * 0.08}s` }}
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="text-sm font-semibold text-text-primary">{item.node}</p>
                  <span className="rounded-md bg-accent/10 px-2 py-1 text-[10px] text-accent">{item.period}</span>
                </div>
                <p className="mt-2 text-[11px] font-semibold uppercase tracking-wide text-text-secondary">
                  {item.phase}
                </p>
                <code className="mt-3 block rounded-md bg-surface px-2 py-1 text-[11px] leading-5 text-accent">
                  {item.structure}
                </code>
                <p className="mt-3 text-xs leading-5 text-text-secondary">{item.edge}</p>
                <p className="mt-3 rounded-md border border-border bg-surface px-2 py-1 text-[11px] text-text-secondary">
                  Source family: {item.source}
                </p>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-lg border border-border bg-surface p-5">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
            <Brain size={18} className="text-accent" />
            Didactic Mirror
          </h2>
          <p className="mt-2 text-sm leading-6 text-text-secondary">
            This side explains what the AI system is doing. The LLM is not the final memory. It proposes
            source-bound structure, then the graph engines preserve and test that structure.
          </p>
          <div className="mt-4 space-y-3">
            {didacticMirrorSteps.map((step) => (
              <div key={step.step} className="rounded-lg border border-border bg-background p-4">
                <div className="flex items-center gap-3">
                  <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-accent/10 text-xs font-semibold text-accent">
                    {step.step.replace(".", "")}
                  </span>
                  <p className="text-sm font-semibold text-text-primary">{step.title}</p>
                </div>
                <p className="mt-2 text-xs leading-5 text-text-secondary">{step.detail}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="graph-backbone" className="scroll-mt-6 grid gap-6 xl:grid-cols-[1.35fr_0.65fr]">
        <MultiGraphBackboneVisual />
        <div className="rounded-lg border border-border bg-surface p-5">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
            <Layers size={18} className="text-accent" />
            Multi-Graph Stack
          </h2>
          <p className="mt-2 text-sm leading-6 text-text-secondary">
            A serious policy/conflict tool needs more than one graph. Dialectica keeps the operational
            graph, temporal memory, evidence graph, reasoning mirror, analytics tables, and API surfaces
            synchronized around the same object IDs.
          </p>
          <div className="mt-4 space-y-3">
            {engineStack.map((engine) => {
              const Icon = engine.icon;
              return (
                <div key={engine.name} className="flex items-start gap-3 rounded-lg border border-border bg-background p-3">
                  <div className="mt-0.5 rounded-md bg-accent/10 p-2 text-accent">
                    <Icon size={16} />
                  </div>
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <p className="text-sm font-semibold text-text-primary">{engine.name}</p>
                      <span className="rounded-md bg-surface px-2 py-0.5 text-[10px] text-text-secondary">
                        {engine.status}
                      </span>
                    </div>
                    <p className="mt-1 text-xs leading-5 text-text-secondary">{engine.role}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      <section className="rounded-lg border border-border bg-surface p-5">
        <div className="flex flex-col justify-between gap-3 lg:flex-row lg:items-center">
          <div>
            <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
              <Layers size={18} className="text-accent" />
              Critical Layer Graph
            </h2>
            <p className="mt-2 max-w-4xl text-sm leading-6 text-text-secondary">
              These layers are the backbone of the product. They are not decoration: every ontology, answer,
              benchmark, and visualization is required to pass through evidence, temporal episodes, causal
              mechanisms, and statecraft/conflict structure.
            </p>
          </div>
          <span className="rounded-md border border-border bg-background px-3 py-2 text-xs text-accent">
            layer invariants before AI prose
          </span>
        </div>
        <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          {criticalLayerGraph.map((item) => (
            <div key={item.layer} className="rounded-lg border border-border bg-background p-4">
              <p className="text-sm font-semibold text-text-primary">{item.layer}</p>
              <div className="mt-3 flex flex-wrap gap-2">
                {item.requiredObjects.map((object) => (
                  <span key={object} className="rounded-md bg-accent/10 px-2 py-1 text-[11px] text-accent">
                    {object}
                  </span>
                ))}
              </div>
              <p className="mt-3 text-xs leading-5 text-text-secondary">{item.invariant}</p>
              <code className="mt-3 block rounded-md bg-surface px-2 py-1 text-[11px] leading-5 text-accent">
                {item.query}
              </code>
            </div>
          ))}
        </div>
      </section>

      <DynamicOntologyVisual />
      <D3OntologyGraph />

      <section className="grid gap-6 xl:grid-cols-[1fr_1fr]">
        <div className="rounded-lg border border-border bg-surface p-5">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
            <Shield size={18} className="text-accent" />
            Statecraft Ontology
          </h2>
          <p className="mt-2 text-sm leading-6 text-text-secondary">
            Statecraft is not one node type. It is a layered ontology for political process, external leverage,
            security architecture, humanitarian governance, legitimacy, and constraints.
          </p>
          <div className="mt-4 space-y-3">
            {statecraftOntology.map((item) => (
              <div key={item.category} className="rounded-lg border border-border bg-background p-4">
                <p className="text-sm font-semibold text-text-primary">{item.category}</p>
                <p className="mt-2 text-xs leading-5 text-text-secondary">{item.question}</p>
                <div className="mt-3 flex flex-wrap gap-2">
                  {item.objects.map((object) => (
                    <span key={object} className="rounded-md bg-accent/10 px-2 py-1 text-[11px] text-accent">
                      {object}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-lg border border-border bg-surface p-5">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
            <GitBranch size={18} className="text-accent" />
            Conflict Structure Ontology
          </h2>
          <p className="mt-2 text-sm leading-6 text-text-secondary">
            Conflict resolution needs a different lens: roles, interests, constraints, trust, commitments,
            process design, narratives, escalation, and evidence-backed causal claims.
          </p>
          <div className="mt-4 space-y-3">
            {conflictOntology.map((item) => (
              <div key={item.layer} className="rounded-lg border border-border bg-background p-4">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="text-sm font-semibold text-text-primary">{item.layer}</p>
                  <code className="rounded-md bg-surface px-2 py-1 text-[11px] text-accent">{item.structure}</code>
                </div>
                <p className="mt-2 text-xs leading-5 text-text-secondary">{item.example}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
        <div className="rounded-lg border border-border bg-surface p-5">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
            <BarChart3 size={18} className="text-accent" />
            Economic Development and Sanctions Ontology
          </h2>
          <p className="mt-2 text-sm leading-6 text-text-secondary">
            For Syria, economic recovery is not just macroeconomics. The ontology links sanctions relief,
            reconstruction finance, compliance risk, trade corridors, service delivery, organized crime,
            and legitimacy so a user can ask precise policy questions.
          </p>
          <div className="mt-4 space-y-3">
            {economicSanctionsOntology.map((item) => (
              <div key={item.category} className="rounded-lg border border-border bg-background p-4">
                <p className="text-sm font-semibold text-text-primary">{item.category}</p>
                <p className="mt-2 text-xs leading-5 text-text-secondary">{item.question}</p>
                <div className="mt-3 flex flex-wrap gap-2">
                  {item.objects.map((object) => (
                    <span key={object} className="rounded-md bg-accent/10 px-2 py-1 text-[11px] text-accent">
                      {object}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-lg border border-border bg-surface p-5">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
            <GitBranch size={18} className="text-accent" />
            Source-Backed Edges
          </h2>
          <p className="mt-2 text-sm leading-6 text-text-secondary">
            The demo should look like a real app because it treats news and research as graph evidence.
            These are the kinds of edges the pipeline creates before the operator accepts or edits them.
          </p>
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            {mediaBackedEdges.map((item) => (
              <div key={item.edge} className="rounded-lg border border-border bg-background p-4">
                <p className="text-[11px] font-semibold uppercase tracking-wide text-accent">{item.source}</p>
                <code className="mt-2 block rounded-md bg-surface px-2 py-1 text-[11px] leading-5 text-text-primary">
                  {item.edge}
                </code>
                <p className="mt-3 text-xs leading-5 text-text-secondary">{item.why}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="rounded-lg border border-border bg-surface p-5">
        <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
          <Workflow size={18} className="text-accent" />
          Sanctions Causal Mechanisms
        </h2>
        <p className="mt-2 max-w-4xl text-sm leading-6 text-text-secondary">
          A sanctions ontology has to model mechanisms, not slogans. Dialectica distinguishes legal
          authorization, bank behavior, political conditionality, and indirect conflict effects so users can
          reason about what is enacted, not enacted, delayed, risky, or beneficial.
        </p>
        <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          {sanctionsCausalMechanisms.map((item) => (
            <div key={item.mechanism} className="rounded-lg border border-border bg-background p-4">
              <p className="text-sm font-semibold text-text-primary">{item.mechanism}</p>
              <code className="mt-3 block rounded-md bg-surface px-2 py-1 text-[11px] leading-5 text-accent">
                {item.chain}
              </code>
              <p className="mt-3 text-xs leading-5 text-text-secondary">{item.example}</p>
              <p className="mt-3 rounded-md border border-border bg-surface px-2 py-1 text-[11px] leading-5 text-text-secondary">
                Deterministic check: {item.deterministicCheck}
              </p>
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-lg border border-border bg-surface p-5">
        <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
          <Timer size={18} className="text-accent" />
          Temporal and Causality Layers
        </h2>
        <p className="mt-2 max-w-4xl text-sm leading-6 text-text-secondary">
          Dialectica separates chronology from causality. A source can be read today, describe a valid period
          last month, belong to a phase, and support a causal claim with its own confidence.
        </p>
        <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          {temporalCausalLayers.map((item) => (
            <div key={item.name} className="rounded-lg border border-border bg-background p-4">
              <p className="text-sm font-semibold text-text-primary">{item.name}</p>
              <p className="mt-2 text-xs leading-5 text-text-secondary">{item.purpose}</p>
              <code className="mt-3 block rounded-md bg-surface px-2 py-1 text-[11px] leading-5 text-accent">
                {item.graph}
              </code>
            </div>
          ))}
        </div>
      </section>

      <section id="temporal-episodes" className="scroll-mt-6 rounded-lg border border-border bg-surface p-5">
        <div className="flex flex-col justify-between gap-3 lg:flex-row lg:items-center">
          <div>
            <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
              <Timer size={18} className="text-accent" />
              Temporal Episode Graphs
            </h2>
            <p className="mt-2 max-w-4xl text-sm leading-6 text-text-secondary">
              Episodes are created as graph objects. That means a Syria reporting window and a War and Peace
              scene sequence can be queried the same way: what changed, which actors were affected, which
              claims became valid, and which causal claims remain interpretive.
            </p>
          </div>
          <span className="rounded-md border border-border bg-background px-3 py-2 text-xs text-accent">
            Episode &gt; Event &gt; Claim &gt; Edge
          </span>
        </div>
        <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {temporalEpisodeExamples.map((item) => (
            <div key={`${item.case}-${item.episode}`} className="rounded-lg border border-border bg-background p-4">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <p className="text-sm font-semibold text-text-primary">{item.episode}</p>
                <span className="rounded-md bg-accent/10 px-2 py-1 text-[10px] text-accent">{item.case}</span>
              </div>
              <p className="mt-2 text-[11px] font-semibold uppercase tracking-wide text-text-secondary">
                {item.window}
              </p>
              <code className="mt-3 block rounded-md bg-surface px-2 py-1 text-[11px] leading-5 text-accent">
                {item.graph}
              </code>
              <div className="mt-3 flex flex-wrap gap-2">
                {item.nodes.map((node) => (
                  <span key={node} className="rounded-md border border-border bg-surface px-2 py-1 text-[11px] text-text-secondary">
                    {node}
                  </span>
                ))}
              </div>
              <p className="mt-3 text-xs leading-5 text-text-secondary">Query: {item.question}</p>
            </div>
          ))}
        </div>
      </section>

      <ExtractionPipelineVisual />

      <section id="config-builder" className="scroll-mt-6 grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
        <div className="rounded-lg border border-border bg-surface p-5">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
            <FileJson size={18} className="text-accent" />
            Configuration Builder
          </h2>
          <p className="mt-2 text-sm leading-6 text-text-secondary">
            This is the concrete handoff between the demo page and the engine. Pick a situation,
            an expert ontology lens, and a runtime target. Dialectica turns that into a config that
            Databricks, Colab, local dev, or the Cloud Run API can execute.
          </p>

          <p className="mt-5 text-xs font-semibold uppercase tracking-wide text-text-secondary">Situation</p>
          <div className="mt-2 grid gap-2 md:grid-cols-2">
            {demoCaseConfigs.map((item) => {
              const Icon = item.icon;
              const active = item.id === selectedCase.id;
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    setSelectedCaseId(item.id);
                    setSelectedLens(item.lenses[0]);
                    setSearchQuery(item.id === "syria" ? "Syria" : item.id === "war-peace" ? "Pierre" : "Romeo");
                  }}
                  className={`rounded-lg border p-4 text-left transition-colors ${
                    active ? "border-accent bg-accent/10" : "border-border bg-background hover:border-border-hover"
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <Icon size={16} className={active ? "text-accent" : "text-text-secondary"} />
                    <p className="text-sm font-semibold text-text-primary">{item.label}</p>
                  </div>
                  <p className="mt-2 text-xs leading-5 text-text-secondary">{item.sourcePack}</p>
                </button>
              );
            })}
          </div>

          <p className="mt-5 text-xs font-semibold uppercase tracking-wide text-text-secondary">Expert lens</p>
          <div className="mt-2 flex flex-wrap gap-2">
            {selectedCase.lenses.map((lens) => (
              <button
                key={lens}
                onClick={() => setSelectedLens(lens)}
                className={`rounded-md border px-3 py-2 text-xs transition-colors ${
                  lens === selectedLens
                    ? "border-accent bg-accent/10 text-accent"
                    : "border-border bg-background text-text-secondary hover:border-border-hover"
                }`}
              >
                {lens}
              </button>
            ))}
          </div>

          <p className="mt-5 text-xs font-semibold uppercase tracking-wide text-text-secondary">Runtime target</p>
          <div className="mt-2 grid gap-2 md:grid-cols-4">
            {["databricks", "colab", "cloud-run-api", "local-dev"].map((target) => (
              <button
                key={target}
                onClick={() => setExecutionTarget(target)}
                className={`rounded-md border px-3 py-2 text-xs transition-colors ${
                  target === executionTarget
                    ? "border-accent bg-accent/10 text-accent"
                    : "border-border bg-background text-text-secondary hover:border-border-hover"
                }`}
              >
                {target}
              </button>
            ))}
          </div>

          <div className="mt-5 grid gap-3 md:grid-cols-3">
            <a
              href={selectedCase.configUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-secondary inline-flex items-center justify-center gap-2"
            >
              <ExternalLink size={15} />
              Open config
            </a>
            <button onClick={copyGeneratedConfig} className="btn-secondary inline-flex items-center justify-center gap-2">
              <Clipboard size={15} />
              Copy live config
            </button>
            <Link href="/graphops" className="btn-primary inline-flex items-center justify-center gap-2">
              <Workflow size={15} />
              Run in GraphOps
            </Link>
          </div>
        </div>

        <div className="rounded-lg border border-border bg-surface p-5">
          <div className="flex flex-col justify-between gap-3 md:flex-row md:items-center">
            <div>
              <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
                <FileCode size={18} className="text-accent" />
                Generated Engine Config
              </h2>
              <p className="mt-1 text-sm text-text-secondary">
                The same contract can feed Databricks jobs, a Colab notebook, a Cloud Run API call, or local tests.
              </p>
            </div>
            <span className="rounded-md bg-accent/10 px-2 py-1 text-[11px] text-accent">
              {selectedCase.label}
            </span>
          </div>
          <pre className="mt-4 max-h-[520px] overflow-auto rounded-lg border border-border bg-background p-4 text-xs leading-5 text-text-secondary">
            <code>{generatedConfigText}</code>
          </pre>
        </div>
      </section>

      <BenchmarkComparisonVisual />

      <section className="grid gap-6 xl:grid-cols-[0.8fr_1.2fr]">
        <div className="rounded-lg border border-border bg-surface p-5">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
            <FileText size={18} className="text-accent" />
            Document Builder Workflow
          </h2>
          <p className="mt-2 text-sm leading-6 text-text-secondary">
            This is the actual operator flow: read sources, check quality, structure the graph, ask expert
            questions, and benchmark whether the graph improved the answer.
          </p>
          <div className="mt-4 space-y-3">
            {documentBuildWorkflow.map((item, index) => (
              <div key={item.action} className="rounded-lg border border-border bg-background p-4">
                <p className="text-xs font-semibold text-accent">Step {index + 1}</p>
                <p className="mt-1 text-sm font-semibold text-text-primary">{item.action}</p>
                <p className="mt-2 text-xs leading-5 text-text-secondary">{item.detail}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-lg border border-border bg-surface p-5">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
            <BarChart3 size={18} className="text-accent" />
            Benchmark Question Generator
          </h2>
          <p className="mt-2 text-sm leading-6 text-text-secondary">
            The benchmark tool generates hard questions from the ontology and evaluates two answers:
            a baseline LLM response and a graph-grounded response. The score checks source coverage,
            causal precision, leverage correctness, uncertainty handling, and reviewability.
          </p>
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            {benchmarkQuestionPlan.map((item) => (
              <div key={item.topic} className="rounded-lg border border-border bg-background p-4">
                <p className="text-sm font-semibold text-text-primary">{item.topic}</p>
                <p className="mt-2 text-xs leading-5 text-text-secondary">{item.generatedQuestion}</p>
                <p className="mt-3 rounded-md bg-surface px-2 py-1 text-[11px] leading-5 text-accent">
                  Evaluates: {item.evaluates}
                </p>
              </div>
            ))}
          </div>
          <div className="mt-5 rounded-lg border border-border bg-background p-4">
            <p className="text-sm font-semibold text-text-primary">Exact scoring rubric</p>
            <div className="mt-3 space-y-3">
              {benchmarkRubricDetails.map((item) => (
                <div key={item.criterion} className="rounded-md bg-surface p-3">
                  <p className="text-xs font-semibold text-accent">{item.criterion}</p>
                  <p className="mt-2 text-[11px] leading-5 text-text-secondary">
                    Baseline failure: {item.baselineFailure}
                  </p>
                  <p className="mt-1 text-[11px] leading-5 text-text-secondary">
                    Graph answer should: {item.graphExpectation}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="rounded-lg border border-border bg-surface p-5">
        <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
          <BookOpen size={18} className="text-accent" />
          Two Concrete Situation Blueprints
        </h2>
        <p className="mt-2 max-w-4xl text-sm leading-6 text-text-secondary">
          The demo has to prove generality without becoming vague. These two cases show how Dialectica
          captures reality through expert lenses: one geopolitical policy process, one book conflict system.
        </p>
        <div className="mt-5 grid gap-4 xl:grid-cols-2">
          {caseBlueprints.map((caseItem) => (
            <div key={caseItem.title} className="rounded-lg border border-border bg-background p-5">
              <p className="text-sm font-semibold text-text-primary">{caseItem.title}</p>
              <p className="mt-2 text-xs leading-5 text-text-secondary">{caseItem.objective}</p>
              <p className="mt-4 text-[11px] font-semibold uppercase tracking-wide text-accent">Expert questions</p>
              <div className="mt-2 space-y-2">
                {caseItem.expertQuestions.map((question) => (
                  <p key={question} className="rounded-md bg-surface px-3 py-2 text-xs leading-5 text-text-secondary">
                    {question}
                  </p>
                ))}
              </div>
              <div className="mt-4 grid gap-3 md:grid-cols-2">
                <div>
                  <p className="text-[11px] font-semibold uppercase tracking-wide text-text-secondary">Ontology</p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {caseItem.ontology.map((item) => (
                      <span key={item} className="rounded-md bg-accent/10 px-2 py-1 text-[11px] text-accent">
                        {item}
                      </span>
                    ))}
                  </div>
                </div>
                <div>
                  <p className="text-[11px] font-semibold uppercase tracking-wide text-text-secondary">Relations</p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {caseItem.relations.map((item) => (
                      <span key={item} className="rounded-md bg-surface px-2 py-1 text-[11px] text-text-secondary">
                        {item}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-lg border border-border bg-surface p-5">
        <div className="flex flex-col justify-between gap-3 lg:flex-row lg:items-center">
          <div>
            <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
              <BookOpen size={18} className="text-accent" />
              Gutenberg Book Graphs
            </h2>
            <p className="mt-2 max-w-4xl text-sm leading-6 text-text-secondary">
              Public-domain books are perfect stress tests: long text, many actors, repeated names,
              temporal scenes, hidden commitments, inferred causality, and abstract themes that need
              evidence rather than summary.
            </p>
          </div>
          <span className="rounded-md border border-border bg-background px-3 py-2 text-xs text-accent">
            source text &gt; scene graph &gt; conflict ontology
          </span>
        </div>
        <div className="mt-5 grid gap-4 xl:grid-cols-2">
          {bookGutenbergUseCases.map((item) => (
            <div key={item.book} className="rounded-lg border border-border bg-background p-5">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <p className="text-sm font-semibold text-text-primary">{item.book}</p>
                <span className="rounded-md bg-accent/10 px-2 py-1 text-[11px] text-accent">{item.source}</span>
              </div>
              <p className="mt-3 text-xs leading-5 text-text-secondary">{item.focus}</p>
              <p className="mt-4 text-[11px] font-semibold uppercase tracking-wide text-accent">What gets captured</p>
              <div className="mt-2 space-y-2">
                {item.captures.map((capture) => (
                  <p key={capture} className="rounded-md bg-surface px-3 py-2 text-xs leading-5 text-text-secondary">
                    {capture}
                  </p>
                ))}
              </div>
              <p className="mt-4 text-[11px] font-semibold uppercase tracking-wide text-accent">Queryable questions</p>
              <div className="mt-2 flex flex-wrap gap-2">
                {item.queries.map((query) => (
                  <span key={query} className="rounded-md border border-border bg-surface px-2 py-1 text-[11px] text-text-secondary">
                    {query}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-lg border border-border bg-surface p-5">
        <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
          <Network size={18} className="text-accent" />
          War and Peace Conflictual Relations
        </h2>
        <p className="mt-2 max-w-4xl text-sm leading-6 text-text-secondary">
          In War and Peace, the graph has to hold personal conflict, family pressure, historical actors,
          battlefield episodes, philosophical claims about causality, and the way war changes private choices.
        </p>
        <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {warPeaceRelationExamples.map((item) => (
            <div key={item.relation} className="rounded-lg border border-border bg-background p-4">
              <code className="block rounded-md bg-surface px-2 py-1 text-[11px] leading-5 text-accent">
                {item.relation}
              </code>
              <p className="mt-3 text-xs font-semibold text-text-primary">{item.ontology}</p>
              <p className="mt-2 text-xs leading-5 text-text-secondary">{item.why}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-lg border border-border bg-surface p-5">
        <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
          <FileCode size={18} className="text-accent" />
          Colab Analysis Handoff
        </h2>
        <p className="mt-2 max-w-4xl text-sm leading-6 text-text-secondary">
          The generated config is not decoration. It is the portable contract a notebook can inspect:
          ontology coverage, weak claims, source spans, benchmark scores, and graph export quality.
        </p>
        <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          {colabNotebookSteps.map((step, index) => (
            <div
              key={step.name}
              className="dialectica-pipeline-card rounded-lg border border-border bg-background p-4"
              style={{ animationDelay: `${index * 0.2}s` }}
            >
              <p className="text-xs font-semibold text-accent">Notebook cell {index + 1}</p>
              <p className="mt-2 text-sm font-semibold text-text-primary">{step.name}</p>
              <code className="mt-3 block rounded-md bg-surface px-2 py-2 text-[11px] leading-5 text-text-secondary">
                {step.code}
              </code>
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-lg border border-border bg-surface p-5">
        <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
          <Database size={18} className="text-accent" />
          Concrete Graph Layers
        </h2>
        <p className="mt-2 max-w-4xl text-sm leading-6 text-text-secondary">
          Each layer exists for a different job. Neo4j answers connected situation questions, Graphiti
          preserves temporal/provenance memory, Cozo answers logic-style reasoning questions, Databricks
          scales extraction and benchmarks, and the API turns all of it into product controls.
        </p>
        <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {graphBackboneLayers.map((layer) => (
            <div key={layer.name} className={`rounded-lg border p-4 ${layer.color}`}>
              <div className="flex flex-wrap items-center justify-between gap-2">
                <p className="text-sm font-semibold">{layer.name}</p>
                <span className="rounded-md bg-black/20 px-2 py-1 text-[10px]">{layer.engine}</span>
              </div>
              <code className="mt-3 block rounded-md bg-black/20 px-2 py-1 text-[11px] leading-5">
                {layer.nodes}
              </code>
              <p className="mt-3 text-xs leading-5">{layer.purpose}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-lg border border-border bg-surface p-5">
        <div className="flex flex-col justify-between gap-3 lg:flex-row lg:items-center">
          <div>
            <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
              <ServerCog size={18} className="text-accent" />
              App Backbone Contract
            </h2>
            <p className="mt-2 max-w-4xl text-sm leading-6 text-text-secondary">
              Dialectica should feel magical in the UI but boring in the backend: stable IDs, typed objects,
              deterministic graph rules, explicit provenance, and AI only where judgment or extraction is useful.
            </p>
          </div>
          <span className="rounded-md border border-border bg-background px-3 py-2 text-xs text-accent">
            deterministic core + AI augmentation
          </span>
        </div>
        <div className="mt-5 grid gap-3 md:grid-cols-2">
          {backboneContracts.map((item) => (
            <div key={item.layer} className="rounded-lg border border-border bg-background p-4">
              <p className="text-sm font-semibold text-text-primary">{item.layer}</p>
              <div className="mt-3 grid gap-3 md:grid-cols-2">
                <div className="rounded-md bg-surface p-3">
                  <p className="text-[11px] font-semibold uppercase tracking-wide text-accent">Deterministic</p>
                  <p className="mt-2 text-xs leading-5 text-text-secondary">{item.deterministic}</p>
                </div>
                <div className="rounded-md bg-surface p-3">
                  <p className="text-[11px] font-semibold uppercase tracking-wide text-accent">AI-augmented</p>
                  <p className="mt-2 text-xs leading-5 text-text-secondary">{item.aiAugmented}</p>
                </div>
              </div>
              <code className="mt-3 block rounded-md border border-border bg-surface px-2 py-1 text-[11px] leading-5 text-accent">
                Query: {item.query}
              </code>
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-lg border border-border bg-surface p-5">
        <div className="flex flex-col justify-between gap-3 lg:flex-row lg:items-center">
          <div>
            <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
              <Workflow size={18} className="text-accent" />
              Multiple Graphs for Policy and Conflict Resolution
            </h2>
            <p className="mt-2 max-w-4xl text-sm leading-6 text-text-secondary">
              The point of the Syria demo is not the country label. It is the ability to build a situation:
              one source pack becomes several semantic layers, each optimized for a different decision problem
              while preserving shared provenance and canonical relations.
            </p>
          </div>
          <span className="rounded-md border border-border bg-background px-3 py-2 text-xs text-accent">
            one case, many lenses
          </span>
        </div>
        <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          {policyConflictLayers.map((layer) => (
            <div key={layer.title} className="rounded-lg border border-border bg-background p-4">
              <div className="flex items-center gap-2">
                <Route size={15} className="text-accent" />
                <p className="text-sm font-semibold text-text-primary">{layer.title}</p>
              </div>
              <p className="mt-3 text-xs leading-5 text-text-secondary">{layer.question}</p>
              <code className="mt-3 block rounded-md bg-surface px-2 py-1 text-[11px] leading-5 text-accent">
                {layer.semanticLayer}
              </code>
              <p className="mt-3 text-[11px] leading-5 text-text-secondary">{layer.output}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1fr_1fr]">
        <div className="rounded-lg border border-border bg-surface p-5">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
            <Network size={18} className="text-accent" />
            Dialectica Backbone
          </h2>
          <p className="mt-2 text-sm leading-6 text-text-secondary">
            Syria is only the demo case. Dialectica is the live API and operator layer that turns any serious
            document set into a queryable semantic graph with provenance, temporal memory, reasoning, and
            benchmarkable answers.
          </p>
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            {backboneSurfaces.map((surface) => (
              <div key={surface.title} className="rounded-lg border border-border bg-background p-4">
                <p className="text-sm font-semibold text-text-primary">{surface.title}</p>
                <p className="mt-2 text-xs leading-5 text-text-secondary">{surface.detail}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-lg border border-border bg-surface p-5">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
            <Globe2 size={18} className="text-accent" />
            Other Situation Builders
          </h2>
          <p className="mt-2 text-sm leading-6 text-text-secondary">
            The same controls can run policy statecraft, mediation, field intelligence, books, legal argument,
            and organizational friction. Each option selects different lenses while preserving the same graph contract.
          </p>
          <div className="mt-4 space-y-3">
            {situationOptions.map((option) => (
              <div key={option.name} className="rounded-lg border border-border bg-background p-4">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="text-sm font-semibold text-text-primary">{option.name}</p>
                  <span className="rounded-md bg-accent/10 px-2 py-1 text-[11px] text-accent">{option.type}</span>
                </div>
                <p className="mt-2 text-xs leading-5 text-text-secondary">{option.objective}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="rounded-lg border border-border bg-surface p-5">
        <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
          <Layers size={18} className="text-accent" />
          Dynamic Ontologies Beyond Syria
        </h2>
        <p className="mt-2 max-w-4xl text-sm leading-6 text-text-secondary">
          The same engine can be useful across domains because every custom ontology is compiled back into
          canonical graph primitives. Users get specialized language without losing search, provenance,
          benchmark scoring, or reusable API queries.
        </p>
        <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {domainOntologyExamples.map((item) => (
            <div key={item.domain} className="rounded-lg border border-border bg-background p-4">
              <p className="text-sm font-semibold text-text-primary">{item.domain}</p>
              <p className="mt-2 text-xs leading-5 text-text-secondary">{item.example}</p>
              <code className="mt-3 block rounded-md bg-surface px-2 py-1 text-[11px] leading-5 text-accent">
                {item.lens}
              </code>
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-lg border border-border bg-surface p-5">
        <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
          <Brain size={18} className="text-accent" />
          45-Second Demo Script
        </h2>
        <div className="mt-4 rounded-lg border border-accent/30 bg-accent/10 p-4">
          <p className="text-xs font-semibold uppercase tracking-wide text-accent">4-second hook</p>
          <p className="mt-2 text-sm leading-6 text-text-primary">{fourSecondHook}</p>
        </div>
        <div className="mt-4 grid gap-3 lg:grid-cols-5">
          {fortyFiveSecondScript.map((step) => (
            <div key={step.time} className="rounded-lg border border-border bg-background p-4">
              <p className="text-xs font-semibold text-accent">{step.time}</p>
              <p className="mt-2 text-xs leading-5 text-text-secondary">{step.line}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[0.8fr_1.2fr]">
        <div className="rounded-lg border border-border bg-surface p-5">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
            <KeyRound size={18} className="text-accent" />
            Operator Key
          </h2>
          <p className="mt-2 text-sm leading-6 text-text-secondary">
            Live API actions use the backend admin key through the
            <code className="mx-1 text-accent">X-API-Key</code>
            header and store it only in this browser. The recording can still show the controls without
            exposing credentials.
          </p>
          <label className="mt-4 block text-xs font-medium uppercase tracking-wide text-text-secondary">API key</label>
          <input
            value={apiKey}
            onChange={(event) => setApiKey(event.target.value)}
            type="password"
            className="input-base mt-2 w-full"
            placeholder="Paste dialectica-admin-key"
          />
          <div className="mt-3 flex flex-wrap gap-2">
            <button onClick={saveApiKey} className="btn-secondary inline-flex items-center gap-2">
              <Shield size={15} />
              Save key
            </button>
            <Link href="/graphops" className="btn-secondary inline-flex items-center gap-2">
              Open GraphOps
              <ArrowRight size={15} />
            </Link>
          </div>
        </div>

        <div className="rounded-lg border border-border bg-surface p-5">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
            <Play size={18} className="text-accent" />
            Recording Click Path
          </h2>
          <div className="mt-4 grid gap-2 md:grid-cols-2">
            {demoClicks.map((item, index) => (
              <div key={item} className="rounded-lg border border-border bg-background p-3">
                <p className="text-xs font-semibold text-accent">Step {index + 1}</p>
                <p className="mt-1 text-sm leading-5 text-text-secondary">{item}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="live-controls" className="scroll-mt-6 rounded-lg border border-border bg-surface p-5">
        <div className="flex flex-col justify-between gap-3 lg:flex-row lg:items-center">
          <div>
            <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
              <Activity size={18} className="text-accent" />
              Live Controls
            </h2>
            <p className="mt-1 text-sm text-text-secondary">
              These buttons call the deployed backend directly. Nothing below is a hardcoded response.
            </p>
            <p className="mt-2 text-xs leading-5 text-text-secondary">
              Live ingestion uses the Syria source pack because it is the connected deployed case. Book and
              War and Peace selections generate runnable configs for Databricks, Colab, API, or local ingestion.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button onClick={checkHealth} className="btn-secondary inline-flex items-center gap-2">
              <Activity size={15} />
              Check health
            </button>
            <button onClick={ingestCase} className="btn-primary inline-flex items-center gap-2">
              <Database size={15} />
              Ingest Syria case
            </button>
            <button onClick={loadRuns} className="btn-secondary inline-flex items-center gap-2">
              <Timer size={15} />
              Load runs
            </button>
          </div>
        </div>

        <div className="mt-5 grid gap-4 xl:grid-cols-3">
          <div className="rounded-lg border border-border bg-background p-4">
            <p className="mb-3 flex items-center gap-2 text-sm font-semibold text-text-primary">
              <Activity size={15} className="text-accent" />
              Health
            </p>
            <JsonPanel state={healthState} empty="Click Check health before recording." />
          </div>
          <div className="rounded-lg border border-border bg-background p-4">
            <p className="mb-3 flex items-center gap-2 text-sm font-semibold text-text-primary">
              <Database size={15} className="text-accent" />
              Ingestion
            </p>
            <JsonPanel state={ingestState} empty="Click Ingest Syria case to write graph data." />
          </div>
          <div className="rounded-lg border border-border bg-background p-4">
            <p className="mb-3 flex items-center gap-2 text-sm font-semibold text-text-primary">
              <Timer size={15} className="text-accent" />
              Pipeline Runs
            </p>
            <JsonPanel state={runsState} empty="Click Load runs to show the audit trail." />
          </div>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
        <div className="rounded-lg border border-border bg-surface p-5">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
            <Search size={18} className="text-accent" />
            Graph Search
          </h2>
          <div className="mt-4 flex gap-2">
            <input
              value={searchQuery}
              onChange={(event) => setSearchQuery(event.target.value)}
              className="input-base flex-1"
              placeholder="Syria, SDF, Turkey, Israel, United Nations"
            />
            <button onClick={() => searchGraph()} className="btn-primary inline-flex items-center gap-2">
              <Search size={15} />
              Search
            </button>
          </div>
          <div className="mt-4">
            <JsonPanel state={searchState} empty="Search after ingestion, then copy an actor id for reasoning." />
          </div>
        </div>

        <div className="rounded-lg border border-border bg-surface p-5">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
            <Brain size={18} className="text-accent" />
            Actor Reasoning
          </h2>
          <p className="mt-2 text-sm leading-6 text-text-secondary">
            Use a returned actor id to produce the actor profile from the graph reasoning layer.
          </p>
          <div className="mt-4 flex gap-2">
            <input
              value={actorId}
              onChange={(event) => setActorId(event.target.value)}
              className="input-base flex-1"
              placeholder="actor id from search"
            />
            <button onClick={reasonActor} className="btn-primary inline-flex items-center gap-2">
              <Brain size={15} />
              Reason actor
            </button>
          </div>
          <div className="mt-4">
            <JsonPanel state={reasoningState} empty="Paste an actor id from graph search to show reasoning." />
          </div>
        </div>
      </section>

      <section id="case-brief" className="scroll-mt-6 grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
        <div className="rounded-lg border border-border bg-surface p-5">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
            <FileText size={18} className="text-accent" />
            Case Brief
          </h2>
          <p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-text-secondary">{SYRIA_TEXT}</p>
          <div className="mt-5 grid gap-3 md:grid-cols-2">
            {sources.map((source) => (
              <a
                key={source.url}
                href={source.url}
                target="_blank"
                rel="noopener noreferrer"
                className="rounded-lg border border-border bg-background p-4 transition-colors hover:border-border-hover"
              >
                <p className="text-sm font-semibold text-text-primary">{source.label}</p>
                <p className="mt-2 text-xs leading-5 text-text-secondary">{source.use}</p>
              </a>
            ))}
          </div>
        </div>

        <div className="rounded-lg border border-border bg-surface p-5">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
            <GitBranch size={18} className="text-accent" />
            Knowledge Structure
          </h2>
          <div className="mt-4 space-y-3">
            {knowledgeLayers.map((layer) => (
              <div key={layer.title} className="rounded-lg border border-border bg-background p-4">
                <p className="text-sm font-semibold text-text-primary">{layer.title}</p>
                <div className="mt-3 flex flex-wrap gap-2">
                  {layer.items.map((item) => (
                    <span key={item} className="rounded-md bg-surface px-2 py-1 text-[11px] text-text-secondary">
                      {item}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <PraxisRelayVisual />

      <section className="rounded-lg border border-border bg-surface p-5">
        <div className="flex flex-col justify-between gap-3 lg:flex-row lg:items-center">
          <div>
            <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
              <FileText size={18} className="text-accent" />
              Research Dossier To Graph
            </h2>
            <p className="mt-2 max-w-4xl text-sm leading-6 text-text-secondary">
              The demo now shows how specific article facts become graph objects, not just labels. Each
              source bit is transformed into typed nodes and edges that PRAXIS can reuse for analysis,
              drafting, red-team review, and planning.
            </p>
          </div>
          <span className="rounded-md border border-border bg-background px-3 py-2 text-xs text-accent">
            article fact &gt; object &gt; PRAXIS output
          </span>
        </div>
        <div className="mt-5 grid gap-3 xl:grid-cols-2">
          {researchDossier.map((item) => (
            <div key={item.source} className="rounded-lg border border-border bg-background p-4">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <p className="text-sm font-semibold text-text-primary">{item.source}</p>
                <span className="rounded-md bg-accent/10 px-2 py-1 text-[11px] text-accent">source bit</span>
              </div>
              <p className="mt-3 text-xs leading-5 text-text-secondary">{item.specificBit}</p>
              <code className="mt-3 block rounded-md bg-surface px-2 py-1 text-[11px] leading-5 text-accent">
                {item.graphPath}
              </code>
              <div className="mt-3 flex flex-wrap gap-2">
                {item.graphObjects.map((object) => (
                  <span key={object} className="rounded-md border border-border bg-surface px-2 py-1 text-[11px] text-text-secondary">
                    {object}
                  </span>
                ))}
              </div>
              <p className="mt-3 rounded-md border border-border bg-surface px-2 py-1 text-[11px] leading-5 text-text-secondary">
                PRAXIS: {item.praxisUse}
              </p>
            </div>
          ))}
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
        <div className="rounded-lg border border-border bg-surface p-5">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
            <FileCode size={18} className="text-accent" />
            Internal Documents As Graph Memory
          </h2>
          <p className="mt-2 text-sm leading-6 text-text-secondary">
            PRAXIS should not rely on a chat transcript. Internal documents become structured memory:
            source chunks, evidence spans, claims, commitments, risks, review owners, and drafting packets.
          </p>
          <div className="mt-4 space-y-3">
            {internalDocumentExamples.map((item) => (
              <div key={item.title} className="rounded-lg border border-border bg-background p-4">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="text-sm font-semibold text-text-primary">{item.title}</p>
                  <span className="rounded-md bg-surface px-2 py-1 text-[11px] text-text-secondary">{item.kind}</span>
                </div>
                <code className="mt-3 block rounded-md bg-surface px-2 py-1 text-[11px] leading-5 text-accent">
                  {item.storedAs}
                </code>
                <p className="mt-3 text-xs leading-5 text-text-secondary">Captures: {item.captures}</p>
                <p className="mt-3 rounded-md border border-border bg-surface px-2 py-1 text-[11px] leading-5 text-text-secondary">
                  Output: {item.praxisOutput}
                </p>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-lg border border-border bg-surface p-5">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
            <Brain size={18} className="text-accent" />
            PRAXIS Toolchain Served By The Graph
          </h2>
          <p className="mt-2 text-sm leading-6 text-text-secondary">
            Once source-backed objects are stored, PRAXIS tools can draft, analyze, critique, and plan from
            the same graph memory instead of re-reading documents from scratch.
          </p>
          <div className="mt-4 space-y-3">
            {praxisToolchain.map((item) => (
              <div key={item.tool} className="rounded-lg border border-border bg-background p-4">
                <p className="text-sm font-semibold text-text-primary">{item.tool}</p>
                <code className="mt-3 block rounded-md bg-surface px-2 py-1 text-[11px] leading-5 text-accent">
                  Input: {item.input}
                </code>
                <p className="mt-3 text-xs leading-5 text-text-secondary">{item.output}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1fr_1fr]">
        <div className="rounded-lg border border-border bg-surface p-5">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
            <GitBranch size={18} className="text-accent" />
            Syria Conflict Dynamic Capture
          </h2>
          <p className="mt-2 text-sm leading-6 text-text-secondary">
            This is what the conflict ontology actually captures: not generic country facts, but the
            mechanisms that change options, trust, violence risk, legitimacy, and mediation feasibility.
          </p>
          <div className="mt-4 space-y-3">
            {syriaConflictCapture.map((item) => (
              <div key={item.object} className="rounded-lg border border-border bg-background p-4">
                <p className="text-sm font-semibold text-text-primary">{item.object}</p>
                <p className="mt-2 text-xs leading-5 text-text-secondary">{item.captures}</p>
                <code className="mt-3 block rounded-md bg-surface px-2 py-1 text-[11px] leading-5 text-accent">
                  {item.graph}
                </code>
                <p className="mt-3 rounded-md border border-border bg-surface px-2 py-1 text-[11px] leading-5 text-text-secondary">
                  Query: {item.question}
                </p>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-lg border border-border bg-surface p-5">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
            <BarChart3 size={18} className="text-accent" />
            Syria Economic Sanctions Capture
          </h2>
          <p className="mt-2 text-sm leading-6 text-text-secondary">
            The sanctions ontology captures economic recovery as a graph of permissions, risk, capital
            flows, institutions, and legitimacy. That lets the app answer practical questions instead
            of producing a generic sanctions paragraph.
          </p>
          <div className="mt-4 space-y-3">
            {syriaEconomicCapture.map((item) => (
              <div key={item.object} className="rounded-lg border border-border bg-background p-4">
                <p className="text-sm font-semibold text-text-primary">{item.object}</p>
                <p className="mt-2 text-xs leading-5 text-text-secondary">{item.captures}</p>
                <code className="mt-3 block rounded-md bg-surface px-2 py-1 text-[11px] leading-5 text-accent">
                  {item.graph}
                </code>
                <p className="mt-3 rounded-md border border-border bg-surface px-2 py-1 text-[11px] leading-5 text-text-secondary">
                  Query: {item.question}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="rounded-lg border border-border bg-surface p-5">
        <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
          <Search size={18} className="text-accent" />
          Query Workbench Examples
        </h2>
        <p className="mt-2 max-w-4xl text-sm leading-6 text-text-secondary">
          These are the kinds of user questions the demo is teaching. The UI can show the prompt, the
          graph path, the deterministic retrieval plan, and the final graph-grounded answer shape.
        </p>
        <div className="mt-5 grid gap-3 md:grid-cols-2">
          {queryWorkbenchExamples.map((item) => (
            <div key={item.prompt} className="rounded-lg border border-border bg-background p-4">
              <p className="text-sm font-semibold text-text-primary">{item.prompt}</p>
              <code className="mt-3 block rounded-md bg-surface px-2 py-1 text-[11px] leading-5 text-accent">
                {item.graphQuery}
              </code>
              <p className="mt-3 text-xs leading-5 text-text-secondary">{item.answerShape}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
        <div className="rounded-lg border border-border bg-surface p-5">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
            <Activity size={18} className="text-accent" />
            Critical User Tracking Needs
          </h2>
          <p className="mt-2 text-sm leading-6 text-text-secondary">
            These are the product questions the graph backbone is built for. The interface should help users
            monitor changes, influence, evidence quality, and decision risk without forcing them to inspect raw data.
          </p>
          <div className="mt-4 space-y-3">
            {userTrackingNeeds.map((item) => (
              <div key={item.need} className="rounded-lg border border-border bg-background p-4">
                <p className="text-sm font-semibold text-text-primary">{item.need}</p>
                <p className="mt-2 text-xs leading-5 text-text-secondary">Tracks: {item.tracks}</p>
                <p className="mt-3 rounded-md bg-surface px-2 py-1 text-[11px] leading-5 text-accent">
                  {item.example}
                </p>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-lg border border-border bg-surface p-5">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
            <FileText size={18} className="text-accent" />
            Real Article Graphs
          </h2>
          <p className="mt-2 text-sm leading-6 text-text-secondary">
            A live source is parsed into graph objects, not pasted into a prompt. The app can show the user
            what meaning was extracted, what graph path was created, and which question that source now answers.
          </p>
          <div className="mt-4 space-y-3">
            {articleGraphExamples.map((item) => (
              <div key={item.source} className="rounded-lg border border-border bg-background p-4">
                <p className="text-sm font-semibold text-text-primary">{item.source}</p>
                <code className="mt-2 block rounded-md bg-surface px-2 py-1 text-[11px] leading-5 text-accent">
                  {item.sourceGraph}
                </code>
                <p className="mt-3 text-xs leading-5 text-text-secondary">{item.meaning}</p>
                <p className="mt-3 rounded-md border border-border bg-surface px-2 py-1 text-[11px] leading-5 text-text-secondary">
                  Query: {item.query}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1fr_1fr]">
        <div className="rounded-lg border border-border bg-surface p-5">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
            <Shield size={18} className="text-accent" />
            Syria Lenses
          </h2>
          <p className="mt-2 text-sm leading-6 text-text-secondary">
            The page focuses the Syria situation through specific analytic lenses so the demo feels like a
            real statecraft product instead of a generic graph viewer.
          </p>
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            {syriaLenses.map((lens) => (
              <div key={lens.name} className="rounded-lg border border-border bg-background p-4">
                <p className="text-sm font-semibold text-text-primary">{lens.name}</p>
                <p className="mt-2 text-xs leading-5 text-text-secondary">{lens.question}</p>
                <code className="mt-3 block rounded-md bg-surface px-2 py-1 text-[11px] leading-5 text-accent">
                  {lens.graph}
                </code>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-lg border border-border bg-surface p-5">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
            <GitBranch size={18} className="text-accent" />
            Canonical Relations
          </h2>
          <p className="mt-2 text-sm leading-6 text-text-secondary">
            Canonical names keep the graph queryable across cases. A Syria claim, a mediation promise, and a
            policy memo constraint can all use the same relation language.
          </p>
          <div className="mt-4 grid gap-2 md:grid-cols-2">
            {canonicalRelations.map((relation) => (
              <code key={relation} className="rounded-md border border-border bg-background px-3 py-2 text-[11px] text-accent">
                {relation}
              </code>
            ))}
          </div>
          <p className="mt-5 text-xs font-semibold uppercase tracking-wide text-text-secondary">Queryable examples</p>
          <div className="mt-3 space-y-2">
            {queryExamples.map((query) => (
              <code key={query} className="block rounded-md bg-background px-3 py-2 text-[11px] text-text-secondary">
                {query}
              </code>
            ))}
          </div>
        </div>
      </section>

      <section className="rounded-lg border border-border bg-surface p-5">
        <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
          <Network size={18} className="text-accent" />
          Pipeline Structure
        </h2>
        <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          {pipelineSteps.map((step) => (
            <div key={step.title} className="rounded-lg border border-border bg-background p-4">
              <div className="flex items-center gap-2">
                <CheckCircle2 size={15} className="text-success" />
                <p className="text-sm font-semibold text-text-primary">{step.title}</p>
              </div>
              <p className="mt-2 text-xs leading-5 text-text-secondary">{step.detail}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
