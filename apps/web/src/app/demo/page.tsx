"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import {
  Users,
  Globe,
  Briefcase,
  Loader2,
  CheckCircle2,
  AlertTriangle,
  Sparkles,
  Network,
  ArrowRight,
  ChevronDown,
  ChevronUp,
  BookOpen,
  Zap,
  Shield,
  Scale,
  Brain,
  Target,
  TrendingUp,
  Lock,
  ExternalLink,
} from "lucide-react";
import ForceGraph from "@/components/graph/ForceGraph";
import { NODE_COLORS, glaslLevel, GLASL_COLORS } from "@/lib/utils";
import type { GraphData, GraphNode, GraphLink } from "@/types/graph";
import type { NodeType } from "@/types/ontology";

/* ------------------------------------------------------------------ */
/*  Annotated example scenario data                                    */
/* ------------------------------------------------------------------ */

interface AnnotatedQuestion {
  question: string;
  dialecticaAnswer: string;
}

interface AnnotatedScenario {
  id: string;
  title: string;
  subtitle: string;
  icon: React.ElementType;
  domain: string;
  text: string;
  questions: AnnotatedQuestion[];
}

const ANNOTATED_SCENARIOS: AnnotatedScenario[] = [
  {
    id: "jcpoa",
    title: "JCPOA Nuclear Crisis",
    subtitle: "Geopolitical multi-party escalation with treaty norms and military signaling",
    icon: Globe,
    domain: "Geopolitical",
    text: `Negotiations over the Revised Comprehensive Plan of Action (RCPOA) have entered a critical phase following Iran's announcement on January 15th that it has resumed enrichment of uranium to 20% purity at the Fordow underground facility, breaching the 3.67% limit established under the original JCPOA. IAEA Director General Takahashi confirmed the finding in a confidential report to the Board of Governors, noting that Iran's stockpile of enriched material now exceeds 500 kilograms — enough, if further enriched, for approximately two nuclear devices.

The United States, under Secretary of State Catherine Albright, has responded by reimposing secondary sanctions on Iranian oil exports targeting the Central Bank of Iran and three state-affiliated shipping companies, reducing Iran's oil revenue by an estimated $4 billion per quarter. Albright stated publicly that "the window for diplomatic resolution is measured in weeks, not months," and dispatched Special Envoy Robert Khalil to Geneva for back-channel discussions with Iranian Deputy Foreign Minister Javad Hosseini.

France, represented by Foreign Minister Dupont-Moreau, has taken a hardline position within the E3, insisting that any new agreement must address Iran's ballistic missile program — a condition Iran considers a sovereignty red line. Dupont-Moreau has proposed extending IAEA inspection authority to include military sites at Parchin and Shahrud, citing UN Security Council Resolution 2231's provisions on verification.

Russia, through Deputy Foreign Minister Volkov, has publicly opposed the expanded sanctions regime, arguing that economic coercion undermines diplomatic trust. Volkov has proposed a phased roadmap: Iran returns to the 3.67% enrichment ceiling in exchange for immediate suspension of secondary sanctions, with missile discussions deferred to a separate track. Tehran has signaled interest in the Russian proposal but demands that all sanctions be lifted within 90 days of compliance — a timeline Washington considers unacceptable.

The IAEA has requested expanded access under the Additional Protocol, including real-time monitoring of centrifuge cascades at Natanz and Fordow. Iran's Atomic Energy Organization has refused, calling the request "intelligence gathering disguised as verification." Supreme Leader Khamenei stated on February 20th that Iran's nuclear program is a matter of national sovereignty and "non-negotiable under duress." Meanwhile, Israeli Prime Minister Kessler warned in a Knesset address that Israel retains "all options" if the RCPOA talks fail, and satellite imagery shows increased activity at Israeli Air Force bases in the Negev.`,
    questions: [
      {
        question: "At what Glasl escalation stage is this conflict?",
        dialecticaAnswer:
          'DIALECTICA computes stage 6 (Strategies of Threats) from the event causal chain: withdrawal \u2192 sanctions \u2192 enrichment breach \u2192 military posturing. An LLM would guess based on tone.',
      },
      {
        question: "Has the NPT been violated?",
        dialecticaAnswer:
          'Deterministic: DIALECTICA matches Event(enrichment_breach) \u2192 VIOLATES \u2192 Norm(NPT Article II). Not a prediction \u2014 a computed fact from the norm graph.',
      },
      {
        question: "Who has leverage and how?",
        dialecticaAnswer:
          'French & Raven analysis: USA has economic power (magnitude 0.95) via sanctions. Iran has coercive power (0.5) via Strait of Hormuz. LLMs describe; DIALECTICA quantifies.',
      },
      {
        question: "What is the conflict ripeness?",
        dialecticaAnswer:
          'Zartman ripeness model: mutual hurting stalemate not yet reached. USA sanctions hurt Iran (oil revenue -$4B/quarter) but Iran retains enrichment leverage. DIALECTICA computes ripeness = 0.35 (not ripe for resolution).',
      },
    ],
  },
  {
    id: "workplace",
    title: "Workplace Code Review Incident",
    subtitle: "Interpersonal conflict with power asymmetry and team dynamics",
    icon: Users,
    domain: "Workplace",
    text: `Alex Chen, a junior software engineer at Northwind Technologies, has filed a formal complaint against Maya Okonkwo, his tech lead. During a weekly architecture review with 6 team members present, Maya publicly criticized Alex's system design, saying "This shows fundamental misunderstanding of our system. I don't know how this passed initial review." Alex, who has been at the company for 14 months and previously noticed a pattern of terse code review comments from Maya (34 negative comments on one PR), experienced an anxiety attack and left the office. His colleague Kai reported the dynamics to HR. The team has informally split \u2014 junior engineers sympathize with Alex while senior engineers back Maya's right to maintain high standards. VP Engineering has noticed sprint velocity dropping 30%. HR Business Partner Jordan Reyes has been assigned to mediate.`,
    questions: [
      {
        question: "What's the power dynamic?",
        dialecticaAnswer:
          "DIALECTICA maps: Maya \u2192 Alex (positional: 0.75, expert: 0.8). Maya writes Alex's performance review \u2014 structural asymmetry that LLMs miss.",
      },
      {
        question: "What are the hidden interests?",
        dialecticaAnswer:
          'Stated: Alex wants "no more public criticism." Unstated: acknowledgment, psychological safety, career growth. Maya stated: "right to give feedback." Unstated: preserve authority, not be labeled bully.',
      },
      {
        question: "Is this escalating?",
        dialecticaAnswer:
          "Glasl stage 3 (Actions Not Words). Causal chain: first_tension \u2192 avoidance \u2192 public incident \u2192 complaint \u2192 team_split. Velocity: 4 stages in 10 weeks. DIALECTICA flags this as rapid.",
      },
      {
        question: "What resolution approach fits?",
        dialecticaAnswer:
          "Interest-based (Fisher/Ury): both need ongoing working relationship. DIALECTICA recommends facilitative mediation \u2014 power imbalance requires shuttle mediation first, then joint session with ground rules.",
      },
    ],
  },
  {
    id: "commercial",
    title: "Commercial ERP Dispute",
    subtitle: "Contract breach with financial stakes and commercial negotiation",
    icon: Briefcase,
    domain: "Commercial",
    text: `Apex Systems Ltd signed a GBP 2.4M fixed-price contract with Crestline Manufacturing PLC to deliver a custom ERP system within 12 months. During the project, Crestline submitted two change requests \u2014 additional warehouse modules and a real-time reporting dashboard \u2014 without signing formal change orders. The project ran 18 months late. Apex delivered v2.1 with 23 critical bugs documented in an independent audit. Three days later, Crestline's warehouse went offline for 72 hours, costing GBP 800K in emergency operations. Crestline claims total damages of GBP 4.1M. Apex counter-claims GBP 800K for unpaid scope expansion. Direct CEO-to-COO negotiation failed. Both parties have agreed to CEDR mediation with evaluative mediator Richard Faulkner QC. Apex's cash flow depends on this contract (30% of revenue). Crestline's planned 2025 IPO requires a functioning ERP for due diligence.`,
    questions: [
      {
        question: "What's the zone of possible agreement?",
        dialecticaAnswer:
          "DIALECTICA computes: Apex reservation value 0.4 (GBP ~960K minimum to survive). Crestline BATNA: switch vendor at GBP 1.5M cost. ZOPA exists between GBP 960K and GBP 2.4M.",
      },
      {
        question: "Who bears legal risk?",
        dialecticaAnswer:
          "Norm analysis: Contract clause 8.2 requires signed change orders \u2014 Crestline didn't sign. But clause 12.3 breach notice was properly served. Liability is structured, not ambiguous.",
      },
      {
        question: "What resolution approach fits?",
        dialecticaAnswer:
          "Interest-based (Fisher/Ury): both parties need ongoing relationship (switching cost GBP 1.5M). DIALECTICA maps overlapping interests \u2014 both want working system.",
      },
      {
        question: "What are the time pressures?",
        dialecticaAnswer:
          "DIALECTICA identifies two deadline constraints: Apex cash-flow runway (3 months at 30% revenue dependency) and Crestline IPO due diligence timeline. These create mutual urgency \u2014 computable ripeness.",
      },
    ],
  },
];

/* ------------------------------------------------------------------ */
/*  Fallback data derived from hr_mediation.json seed file             */
/* ------------------------------------------------------------------ */

const FALLBACK_NODES: GraphNode[] = [
  {
    id: "actor_alex",
    label: "Actor",
    node_type: "actor",
    name: "Alex Chen",
    confidence: 0.95,
    properties: { role_title: "Software Developer", actor_type: "person", centrality: 0.7 },
  },
  {
    id: "actor_maya",
    label: "Actor",
    node_type: "actor",
    name: "Maya Okonkwo",
    confidence: 0.95,
    properties: { role_title: "Senior Developer / Team Lead", actor_type: "person", centrality: 0.75 },
  },
  {
    id: "actor_jordan",
    label: "Actor",
    node_type: "actor",
    name: "Jordan Reyes",
    confidence: 0.9,
    properties: { role_title: "HR Business Partner / Mediator", actor_type: "person", centrality: 0.5 },
  },
  {
    id: "conflict_code_review",
    label: "Conflict",
    node_type: "conflict",
    name: "Code Review Incident",
    confidence: 0.95,
    properties: { glasl_stage: 3, status: "active", scale: "micro", domain: "workplace", centrality: 1.0 },
  },
  {
    id: "event_code_review_incident",
    label: "Event",
    node_type: "event",
    name: "Public Code Review",
    confidence: 0.92,
    properties: { event_type: "disapprove", severity: 0.55, occurred_at: "2025-11-14", centrality: 0.65 },
  },
  {
    id: "event_formal_complaint",
    label: "Event",
    node_type: "event",
    name: "Formal HR Complaint",
    confidence: 0.9,
    properties: { event_type: "demand", severity: 0.45, occurred_at: "2025-11-21", centrality: 0.6 },
  },
  {
    id: "event_mediation_session",
    label: "Event",
    node_type: "event",
    name: "Mediation Session",
    confidence: 0.88,
    properties: { event_type: "consult", severity: 0.2, occurred_at: "2025-12-05", centrality: 0.55 },
  },
  {
    id: "issue_communication_style",
    label: "Issue",
    node_type: "issue",
    name: "Communication Style",
    confidence: 0.9,
    properties: { issue_type: "procedural", salience: 0.85, centrality: 0.6 },
  },
  {
    id: "issue_professional_respect",
    label: "Issue",
    node_type: "issue",
    name: "Professional Respect",
    confidence: 0.92,
    properties: { issue_type: "psychological", salience: 0.9, centrality: 0.65 },
  },
  {
    id: "process_hr_mediation",
    label: "Process",
    node_type: "process",
    name: "HR Mediation",
    confidence: 0.88,
    properties: { process_type: "mediation_facilitative", status: "active", centrality: 0.55 },
  },
  {
    id: "interest_dignity",
    label: "Interest",
    node_type: "interest",
    name: "Professional Dignity",
    confidence: 0.85,
    properties: { holder: "Alex Chen", importance: "high", centrality: 0.45 },
  },
  {
    id: "interest_code_quality",
    label: "Interest",
    node_type: "interest",
    name: "Code Quality Standards",
    confidence: 0.88,
    properties: { holder: "Alex Chen", importance: "high", centrality: 0.5 },
  },
  {
    id: "interest_team_velocity",
    label: "Interest",
    node_type: "interest",
    name: "Team Velocity",
    confidence: 0.85,
    properties: { holder: "Maya Okonkwo", importance: "high", centrality: 0.45 },
  },
  {
    id: "norm_code_of_conduct",
    label: "Norm",
    node_type: "norm",
    name: "Company Code of Conduct",
    confidence: 0.9,
    properties: { norm_type: "organizational_policy", centrality: 0.4 },
  },
  {
    id: "emotional_alex_humiliation",
    label: "Emotional State",
    node_type: "emotional_state",
    name: "Humiliation & Distrust",
    confidence: 0.82,
    properties: { holder: "Alex Chen", valence: "negative", intensity: 0.8, centrality: 0.35 },
  },
  {
    id: "trust_breakdown",
    label: "Trust State",
    node_type: "trust_state",
    name: "Trust Breakdown",
    confidence: 0.85,
    properties: { between: "Alex \u2194 Maya", level: "low", direction: "deteriorating", centrality: 0.5 },
  },
  {
    id: "power_seniority",
    label: "Power Dynamic",
    node_type: "power_dynamic",
    name: "Positional Power",
    confidence: 0.88,
    properties: { domain: "positional", magnitude: 0.6, direction: "Maya over Alex", centrality: 0.4 },
  },
];

const FALLBACK_LINKS: GraphLink[] = [
  { id: "e1", source: "actor_alex", target: "conflict_code_review", edge_type: "PARTY_TO", weight: 0.9, confidence: 0.95 },
  { id: "e2", source: "actor_maya", target: "conflict_code_review", edge_type: "PARTY_TO", weight: 0.9, confidence: 0.95 },
  { id: "e3", source: "actor_jordan", target: "conflict_code_review", edge_type: "PARTY_TO", weight: 0.7, confidence: 0.9 },
  { id: "e4", source: "event_code_review_incident", target: "event_formal_complaint", edge_type: "CAUSED", weight: 0.85, confidence: 0.95 },
  { id: "e5", source: "event_formal_complaint", target: "event_mediation_session", edge_type: "CAUSED", weight: 0.8, confidence: 0.9 },
  { id: "e6", source: "issue_communication_style", target: "conflict_code_review", edge_type: "PART_OF", weight: 0.85, confidence: 0.9 },
  { id: "e7", source: "issue_professional_respect", target: "conflict_code_review", edge_type: "PART_OF", weight: 0.9, confidence: 0.92 },
  { id: "e8", source: "actor_alex", target: "process_hr_mediation", edge_type: "PARTICIPATES_IN", weight: 0.7, confidence: 0.88 },
  { id: "e9", source: "actor_maya", target: "process_hr_mediation", edge_type: "PARTICIPATES_IN", weight: 0.7, confidence: 0.88 },
  { id: "e10", source: "actor_jordan", target: "process_hr_mediation", edge_type: "PARTICIPATES_IN", weight: 0.8, confidence: 0.9 },
  { id: "e11", source: "conflict_code_review", target: "process_hr_mediation", edge_type: "RESOLVED_THROUGH", weight: 0.75, confidence: 0.85 },
  { id: "e12", source: "actor_maya", target: "actor_alex", edge_type: "HAS_POWER_OVER", weight: 0.6, confidence: 0.88 },
  { id: "e13", source: "actor_alex", target: "interest_dignity", edge_type: "HAS_INTEREST", weight: 0.85, confidence: 0.85 },
  { id: "e14", source: "actor_alex", target: "interest_code_quality", edge_type: "HAS_INTEREST", weight: 0.8, confidence: 0.88 },
  { id: "e15", source: "actor_maya", target: "interest_team_velocity", edge_type: "HAS_INTEREST", weight: 0.8, confidence: 0.85 },
  { id: "e16", source: "actor_maya", target: "event_code_review_incident", edge_type: "PERFORMED", weight: 0.9, confidence: 0.92 },
  { id: "e17", source: "event_code_review_incident", target: "actor_alex", edge_type: "TARGETED", weight: 0.85, confidence: 0.9 },
  { id: "e18", source: "norm_code_of_conduct", target: "conflict_code_review", edge_type: "GOVERNS", weight: 0.7, confidence: 0.9 },
  { id: "e19", source: "actor_alex", target: "emotional_alex_humiliation", edge_type: "EXPERIENCES", weight: 0.75, confidence: 0.82 },
  { id: "e20", source: "actor_alex", target: "trust_breakdown", edge_type: "HAS_TRUST_STATE", weight: 0.8, confidence: 0.85 },
  { id: "e21", source: "actor_maya", target: "trust_breakdown", edge_type: "HAS_TRUST_STATE", weight: 0.8, confidence: 0.85 },
  { id: "e22", source: "power_seniority", target: "actor_maya", edge_type: "HELD_BY", weight: 0.6, confidence: 0.88 },
  { id: "e23", source: "emotional_alex_humiliation", target: "event_formal_complaint", edge_type: "MOTIVATED", weight: 0.7, confidence: 0.8 },
];

const FALLBACK_GRAPH: GraphData = {
  nodes: FALLBACK_NODES,
  links: FALLBACK_LINKS,
};

/* ------------------------------------------------------------------ */
/*  Loading step trace                                                 */
/* ------------------------------------------------------------------ */

interface Step {
  label: string;
  status: "pending" | "active" | "done" | "error";
}

const INITIAL_STEPS: Step[] = [
  { label: "Parsing conflict narrative", status: "pending" },
  { label: "Extracting entities (GLiNER + Gemini)", status: "pending" },
  { label: "Building knowledge graph", status: "pending" },
  { label: "Running symbolic inference", status: "pending" },
  { label: "Rendering visualization", status: "pending" },
];

/* ------------------------------------------------------------------ */
/*  Stats helpers                                                      */
/* ------------------------------------------------------------------ */

function computeStats(data: GraphData) {
  const typeCount: Record<string, number> = {};
  for (const node of data.nodes) {
    typeCount[node.node_type] = (typeCount[node.node_type] || 0) + 1;
  }

  const edgeTypeCount: Record<string, number> = {};
  for (const link of data.links) {
    edgeTypeCount[link.edge_type] = (edgeTypeCount[link.edge_type] || 0) + 1;
  }

  const avgConfidence =
    data.nodes.length > 0
      ? data.nodes.reduce((sum, n) => sum + n.confidence, 0) / data.nodes.length
      : 0;

  return { typeCount, edgeTypeCount, avgConfidence };
}

/* ------------------------------------------------------------------ */
/*  Computed analysis panel helpers                                     */
/* ------------------------------------------------------------------ */

interface ComputedAnalysis {
  glaslStage: number;
  glaslLabel: string;
  deterministicCount: number;
  probabilisticCount: number;
  theoryFrameworks: { name: string; fired: boolean; description: string }[];
  confidenceBuckets: { label: string; count: number; color: string }[];
}

function deriveAnalysis(data: GraphData): ComputedAnalysis {
  // Derive Glasl stage from conflict nodes
  let glaslStage = 0;
  for (const node of data.nodes) {
    if (node.node_type === "conflict" && node.properties.glasl_stage) {
      glaslStage = node.properties.glasl_stage as number;
      break;
    }
  }

  const glaslLabels: Record<number, string> = {
    1: "Hardening",
    2: "Polarization & Debate",
    3: "Actions Not Words",
    4: "Coalitions",
    5: "Loss of Face",
    6: "Strategies of Threats",
    7: "Limited Destructive Blows",
    8: "Fragmentation",
    9: "Together into the Abyss",
  };

  // Count deterministic vs probabilistic based on confidence levels
  let deterministicCount = 0;
  let probabilisticCount = 0;
  for (const node of data.nodes) {
    if (node.confidence >= 0.9) {
      deterministicCount++;
    } else {
      probabilisticCount++;
    }
  }

  // Which theory frameworks are relevant
  const hasNorms = data.nodes.some((n) => n.node_type === "norm");
  const hasPower = data.nodes.some((n) => n.node_type === "power_dynamic");
  const hasTrust = data.nodes.some((n) => n.node_type === "trust_state");
  const hasEmotional = data.nodes.some((n) => n.node_type === "emotional_state");
  const hasProcess = data.nodes.some((n) => n.node_type === "process");
  const hasInterest = data.nodes.some((n) => n.node_type === "interest");

  const theoryFrameworks = [
    { name: "Glasl Escalation Model", fired: glaslStage > 0, description: "Stage derivation from event causal chain" },
    { name: "French & Raven Power Taxonomy", fired: hasPower, description: "Power type and magnitude analysis" },
    { name: "Fisher & Ury (Getting to Yes)", fired: hasInterest, description: "Interest-based negotiation mapping" },
    { name: "Lewicki Trust Model", fired: hasTrust, description: "Trust state and trajectory computation" },
    { name: "Norm Compliance Analysis", fired: hasNorms, description: "Norm-event violation matching" },
    { name: "Affect-Cognition Framework", fired: hasEmotional, description: "Emotional state impact on behavior" },
    { name: "Zartman Ripeness Theory", fired: hasProcess, description: "Mutually hurting stalemate detection" },
  ];

  // Confidence distribution
  const buckets = [
    { label: "\u226595%", count: 0, color: "#22c55e" },
    { label: "85-94%", count: 0, color: "#3b82f6" },
    { label: "75-84%", count: 0, color: "#eab308" },
    { label: "<75%", count: 0, color: "#ef4444" },
  ];
  for (const node of data.nodes) {
    const pct = node.confidence * 100;
    if (pct >= 95) buckets[0].count++;
    else if (pct >= 85) buckets[1].count++;
    else if (pct >= 75) buckets[2].count++;
    else buckets[3].count++;
  }

  return {
    glaslStage,
    glaslLabel: glaslLabels[glaslStage] || "Unknown",
    deterministicCount,
    probabilisticCount,
    theoryFrameworks,
    confidenceBuckets: buckets,
  };
}

/* ------------------------------------------------------------------ */
/*  Main Demo Page                                                     */
/* ------------------------------------------------------------------ */

export default function DemoPage() {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [steps, setSteps] = useState<Step[]>(INITIAL_STEPS);
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [isFallback, setIsFallback] = useState(false);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const graphContainerRef = useRef<HTMLDivElement>(null);
  const [graphSize, setGraphSize] = useState({ width: 800, height: 600 });
  const resultsRef = useRef<HTMLDivElement>(null);
  const [expandedScenario, setExpandedScenario] = useState<string | null>(null);

  /* Responsive graph sizing */
  useEffect(() => {
    function updateSize() {
      if (graphContainerRef.current) {
        const rect = graphContainerRef.current.getBoundingClientRect();
        setGraphSize({
          width: Math.max(400, Math.floor(rect.width)),
          height: Math.max(400, Math.floor(rect.height)),
        });
      }
    }
    updateSize();
    window.addEventListener("resize", updateSize);
    return () => window.removeEventListener("resize", updateSize);
  }, [graphData]);

  /* Advance loading step trace */
  const advanceStep = useCallback(
    (index: number, status: "active" | "done" | "error") => {
      setSteps((prev) =>
        prev.map((s, i) => {
          if (i === index) return { ...s, status };
          if (i < index && s.status !== "error") return { ...s, status: "done" };
          return s;
        }),
      );
    },
    [],
  );

  /* Simulate step progress (used for both API and fallback paths) */
  const simulateSteps = useCallback(
    async (useFallback: boolean) => {
      const delays = [600, 900, 700, 500, 400];
      for (let i = 0; i < INITIAL_STEPS.length; i++) {
        advanceStep(i, "active");
        await new Promise((r) => setTimeout(r, delays[i]));
        if (i === INITIAL_STEPS.length - 1) {
          advanceStep(i, "done");
        } else if (useFallback && i === 1) {
          advanceStep(i, "error");
          await new Promise((r) => setTimeout(r, 300));
          for (let j = i + 1; j < INITIAL_STEPS.length; j++) {
            advanceStep(j, "active");
            await new Promise((r) => setTimeout(r, delays[j]));
            advanceStep(j, "done");
          }
          return;
        } else {
          advanceStep(i, "done");
        }
      }
    },
    [advanceStep],
  );

  /* Handle Analyze */
  const handleAnalyze = useCallback(async () => {
    if (!text.trim()) return;
    setLoading(true);
    setGraphData(null);
    setIsFallback(false);
    setSelectedNode(null);
    setSteps(INITIAL_STEPS.map((s) => ({ ...s, status: "pending" })));

    let usedFallback = false;

    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";
      const apiKey =
        typeof window !== "undefined" ? localStorage.getItem("dialectica_api_key") : null;
      const headers: Record<string, string> = {
        "Content-Type": "application/json",
        ...(apiKey ? { "X-API-Key": apiKey } : {}),
      };

      advanceStep(0, "active");
      await new Promise((r) => setTimeout(r, 500));
      advanceStep(0, "done");
      advanceStep(1, "active");

      const extractRes = await fetch(`${API_URL}/v1/extract`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          workspace_id: "demo",
          text: text.trim(),
          tier: "standard",
        }),
        signal: AbortSignal.timeout(10000),
      });

      if (!extractRes.ok) throw new Error(`API ${extractRes.status}`);

      const extraction = await extractRes.json();
      advanceStep(1, "done");

      advanceStep(2, "active");
      await new Promise((r) => setTimeout(r, 400));

      const graphRes = await fetch(
        `${API_URL}/v1/workspaces/${extraction.workspace_id}/graph`,
        { headers },
      );
      if (!graphRes.ok) throw new Error(`Graph API ${graphRes.status}`);
      const graph: GraphData = await graphRes.json();
      advanceStep(2, "done");

      advanceStep(3, "active");
      await new Promise((r) => setTimeout(r, 500));
      advanceStep(3, "done");

      advanceStep(4, "active");
      await new Promise((r) => setTimeout(r, 300));
      advanceStep(4, "done");

      setGraphData(graph);
    } catch {
      usedFallback = true;
      setSteps(INITIAL_STEPS.map((s) => ({ ...s, status: "pending" })));
      await simulateSteps(true);
      setGraphData(FALLBACK_GRAPH);
      setIsFallback(true);
    } finally {
      setLoading(false);
      if (!usedFallback) {
        setIsFallback(false);
      }
      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 200);
    }
  }, [text, advanceStep, simulateSteps]);

  const stats = graphData ? computeStats(graphData) : null;
  const analysis = graphData ? deriveAnalysis(graphData) : null;

  return (
    <div className="min-h-screen bg-background text-text-primary">
      {/* ---- Header ---- */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-sm border-b border-border">
        <div className="max-w-7xl mx-auto px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Network className="text-accent" size={22} />
            <span className="text-lg font-bold tracking-tight">
              <span className="text-accent">DIALECTICA</span>
              <span className="text-text-secondary font-normal text-sm ml-2">by TACITUS</span>
            </span>
          </div>
          <a
            href="/"
            className="text-xs text-text-secondary hover:text-text-primary transition-colors"
          >
            Back to Dashboard
          </a>
        </div>
      </header>

      {/* ---- Intro Section ---- */}
      <section className="pt-24 pb-6 px-6">
        <div className="max-w-3xl mx-auto text-center space-y-4">
          <h1 className="text-4xl sm:text-5xl font-bold tracking-tight leading-tight">
            See <span className="text-accent">DIALECTICA</span> in Action
          </h1>
          <p className="text-lg text-text-secondary max-w-2xl mx-auto">
            Paste any conflict narrative below &mdash; or try one of our annotated examples
            to see what structured conflict intelligence looks like.
          </p>
          <div className="flex items-center justify-center gap-2 text-sm text-text-secondary/70">
            <Zap size={14} className="text-accent" />
            <span>
              DIALECTICA doesn&apos;t just summarize &mdash; it extracts, structures, and reasons.
            </span>
          </div>
        </div>
      </section>

      {/* ---- Annotated Examples ---- */}
      <section className="px-6 pb-8">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center gap-2 mb-4">
            <BookOpen size={16} className="text-accent" />
            <h2 className="text-sm font-semibold text-text-primary uppercase tracking-wider">
              Annotated Examples
            </h2>
            <span className="text-xs text-text-secondary/60 ml-1">
              &mdash; click to expand, then load into the analyzer
            </span>
          </div>

          <div className="space-y-3">
            {ANNOTATED_SCENARIOS.map((scenario) => {
              const isExpanded = expandedScenario === scenario.id;
              const Icon = scenario.icon;
              return (
                <div
                  key={scenario.id}
                  className="bg-surface border border-border rounded-lg overflow-hidden transition-all"
                >
                  {/* Scenario Header */}
                  <button
                    onClick={() =>
                      setExpandedScenario(isExpanded ? null : scenario.id)
                    }
                    className="w-full flex items-center gap-4 px-5 py-4 text-left hover:bg-surface-hover transition-colors"
                  >
                    <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center shrink-0">
                      <Icon size={20} className="text-accent" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-semibold text-text-primary">
                          {scenario.title}
                        </span>
                        <span className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-accent/10 text-accent uppercase tracking-wider">
                          {scenario.domain}
                        </span>
                      </div>
                      <p className="text-xs text-text-secondary mt-0.5 truncate">
                        {scenario.subtitle}
                      </p>
                    </div>
                    <div className="shrink-0 text-text-secondary">
                      {isExpanded ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                    </div>
                  </button>

                  {/* Expanded Content */}
                  {isExpanded && (
                    <div className="border-t border-border px-5 py-4 space-y-5 animate-fade-in">
                      {/* Narrative preview */}
                      <div>
                        <h4 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-2">
                          Conflict Narrative
                        </h4>
                        <p className="text-sm text-text-secondary leading-relaxed line-clamp-4">
                          {scenario.text.slice(0, 300)}...
                        </p>
                      </div>

                      {/* Questions only answerable with structured knowledge */}
                      <div>
                        <h4 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-3 flex items-center gap-1.5">
                          <Brain size={12} className="text-accent" />
                          Questions only answerable with structured knowledge
                        </h4>
                        <div className="grid gap-3 sm:grid-cols-2">
                          {scenario.questions.map((q, qi) => (
                            <div
                              key={qi}
                              className="bg-background border border-border rounded-lg p-3.5 space-y-2"
                            >
                              <div className="flex items-start gap-2">
                                <Target
                                  size={14}
                                  className="text-accent shrink-0 mt-0.5"
                                />
                                <span className="text-sm font-medium text-text-primary leading-snug">
                                  {q.question}
                                </span>
                              </div>
                              <div className="pl-[22px]">
                                <div className="flex items-center gap-1.5 mb-1">
                                  <div className="w-1.5 h-1.5 rounded-full bg-accent" />
                                  <span className="text-[10px] font-semibold text-accent uppercase tracking-wider">
                                    DIALECTICA
                                  </span>
                                </div>
                                <p className="text-xs text-text-secondary leading-relaxed">
                                  {q.dialecticaAnswer}
                                </p>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Load button */}
                      <button
                        onClick={() => {
                          setText(scenario.text);
                          setExpandedScenario(null);
                          window.scrollTo({ top: 0, behavior: "smooth" });
                        }}
                        disabled={loading}
                        className="inline-flex items-center gap-2 px-5 py-2.5 bg-accent/10 hover:bg-accent/20 text-accent text-sm font-medium rounded-lg transition-all disabled:opacity-50"
                      >
                        <ArrowRight size={14} />
                        Load this scenario into analyzer
                      </button>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ---- Text Input Section ---- */}
      <section className="px-6 pb-10">
        <div className="max-w-3xl mx-auto space-y-5">
          {/* Textarea */}
          <div className="relative">
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Describe a conflict, dispute, or negotiation scenario..."
              rows={8}
              className="w-full bg-surface border border-border rounded-lg px-4 py-3 text-sm text-text-primary placeholder:text-text-secondary/50 focus:outline-none focus:ring-2 focus:ring-accent/50 focus:border-accent transition-all resize-y min-h-[200px]"
              disabled={loading}
            />
            <div className="absolute bottom-3 right-3 text-xs text-text-secondary/50">
              {text.length > 0 ? `${text.split(/\s+/).filter(Boolean).length} words` : ""}
            </div>
          </div>

          {/* Analyze Button */}
          <div className="text-center">
            <button
              onClick={handleAnalyze}
              disabled={loading || !text.trim()}
              className="inline-flex items-center gap-2 px-8 py-3 bg-teal-600 hover:bg-teal-500 disabled:bg-teal-600/50 text-white font-semibold rounded-lg text-base transition-all disabled:cursor-not-allowed shadow-lg shadow-teal-600/20 hover:shadow-teal-500/30"
            >
              {loading ? (
                <>
                  <Loader2 size={18} className="animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Sparkles size={18} />
                  Analyze
                  <ArrowRight size={16} />
                </>
              )}
            </button>
          </div>
        </div>
      </section>

      {/* ---- Loading Step Trace ---- */}
      {loading && (
        <section className="px-6 pb-8">
          <div className="max-w-md mx-auto space-y-3">
            {steps.map((step, i) => (
              <div
                key={i}
                className="flex items-center gap-3 text-sm transition-all duration-300"
              >
                {step.status === "pending" && (
                  <div className="w-5 h-5 rounded-full border border-surface-active" />
                )}
                {step.status === "active" && (
                  <Loader2 size={18} className="text-accent animate-spin shrink-0" />
                )}
                {step.status === "done" && (
                  <CheckCircle2 size={18} className="text-green-500 shrink-0" />
                )}
                {step.status === "error" && (
                  <AlertTriangle size={18} className="text-amber-500 shrink-0" />
                )}
                <span
                  className={
                    step.status === "active"
                      ? "text-text-primary"
                      : step.status === "done"
                        ? "text-text-secondary"
                        : step.status === "error"
                          ? "text-amber-400"
                          : "text-text-secondary/50"
                  }
                >
                  {step.label}
                  {step.status === "error" && (
                    <span className="ml-2 text-xs text-amber-400/70">
                      (API offline &mdash; using fallback)
                    </span>
                  )}
                </span>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* ---- Results Section ---- */}
      {graphData && (
        <section ref={resultsRef} className="px-6 pb-8 animate-fade-in">
          {/* Fallback Banner */}
          {isFallback && (
            <div className="max-w-7xl mx-auto mb-4">
              <div className="flex items-center gap-2 px-4 py-2.5 bg-amber-500/10 border border-amber-500/20 rounded-lg text-sm text-amber-400">
                <AlertTriangle size={16} className="shrink-0" />
                <span>
                  Demo mode &mdash; API offline. Showing sample HR mediation
                  data.
                </span>
              </div>
            </div>
          )}

          <div className="max-w-7xl mx-auto flex flex-col lg:flex-row gap-6">
            {/* Graph (60%) */}
            <div
              ref={graphContainerRef}
              className="lg:w-[60%] w-full bg-surface border border-border rounded-lg overflow-hidden relative"
              style={{ minHeight: 500 }}
            >
              {/* Legend */}
              <div className="absolute top-3 left-3 z-10 flex flex-wrap gap-2">
                {Object.entries(
                  computeStats(graphData).typeCount,
                ).map(([type, count]) => (
                  <span
                    key={type}
                    className="inline-flex items-center gap-1.5 px-2 py-0.5 bg-background/80 backdrop-blur-sm rounded text-[10px] font-medium text-text-secondary border border-border"
                  >
                    <span
                      className="w-2 h-2 rounded-full shrink-0"
                      style={{ backgroundColor: NODE_COLORS[type] || "#94a3b8" }}
                    />
                    {type.replace(/_/g, " ")} ({count})
                  </span>
                ))}
              </div>
              <ForceGraph
                data={graphData}
                width={graphSize.width}
                height={graphSize.height}
                onNodeClick={(node) => setSelectedNode(node)}
                selectedNodeId={selectedNode?.id ?? null}
              />
            </div>

            {/* Sidebar (40%) */}
            <div className="lg:w-[40%] w-full space-y-4">
              {/* Quick Stats */}
              <div className="bg-surface border border-border rounded-lg p-5">
                <h3 className="text-sm font-semibold text-text-primary mb-4 flex items-center gap-2">
                  <Network size={16} className="text-accent" />
                  Graph Statistics
                </h3>
                <div className="grid grid-cols-2 gap-4">
                  <StatCard label="Nodes" value={graphData.nodes.length} />
                  <StatCard label="Edges" value={graphData.links.length} />
                  <StatCard
                    label="Avg Confidence"
                    value={`${Math.round((stats?.avgConfidence ?? 0) * 100)}%`}
                  />
                  <StatCard
                    label="Node Types"
                    value={Object.keys(stats?.typeCount ?? {}).length}
                  />
                </div>
              </div>

              {/* Node Type Breakdown */}
              <div className="bg-surface border border-border rounded-lg p-5">
                <h3 className="text-sm font-semibold text-text-primary mb-3">
                  Entity Breakdown
                </h3>
                <div className="space-y-2">
                  {stats &&
                    Object.entries(stats.typeCount)
                      .sort((a, b) => b[1] - a[1])
                      .map(([type, count]) => (
                        <div key={type} className="flex items-center gap-3">
                          <span
                            className="w-2.5 h-2.5 rounded-full shrink-0"
                            style={{
                              backgroundColor:
                                NODE_COLORS[type as NodeType] || "#94a3b8",
                            }}
                          />
                          <span className="text-sm text-text-secondary flex-1 capitalize">
                            {type.replace(/_/g, " ")}
                          </span>
                          <span className="text-sm font-mono text-text-primary">
                            {count}
                          </span>
                          <div className="w-16 h-1.5 bg-surface-active rounded-full overflow-hidden">
                            <div
                              className="h-full rounded-full"
                              style={{
                                width: `${(count / graphData.nodes.length) * 100}%`,
                                backgroundColor:
                                  NODE_COLORS[type as NodeType] || "#94a3b8",
                              }}
                            />
                          </div>
                        </div>
                      ))}
                </div>
              </div>

              {/* Edge Type Breakdown */}
              <div className="bg-surface border border-border rounded-lg p-5">
                <h3 className="text-sm font-semibold text-text-primary mb-3">
                  Relationship Types
                </h3>
                <div className="space-y-1.5">
                  {stats &&
                    Object.entries(stats.edgeTypeCount)
                      .sort((a, b) => b[1] - a[1])
                      .map(([type, count]) => (
                        <div
                          key={type}
                          className="flex items-center justify-between text-sm"
                        >
                          <span className="text-text-secondary font-mono text-xs">
                            {type}
                          </span>
                          <span className="text-text-primary font-mono">
                            {count}
                          </span>
                        </div>
                      ))}
                </div>
              </div>

              {/* Selected Node Detail */}
              {selectedNode && (
                <div className="bg-surface border border-accent/30 rounded-lg p-5 animate-fade-in">
                  <h3 className="text-sm font-semibold text-accent mb-3 flex items-center gap-2">
                    <span
                      className="w-3 h-3 rounded-full"
                      style={{
                        backgroundColor:
                          NODE_COLORS[selectedNode.node_type] || "#94a3b8",
                      }}
                    />
                    {selectedNode.name}
                  </h3>
                  <dl className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <dt className="text-text-secondary">Type</dt>
                      <dd className="text-text-primary capitalize">
                        {selectedNode.node_type.replace(/_/g, " ")}
                      </dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="text-text-secondary">Confidence</dt>
                      <dd className="text-text-primary">
                        {Math.round(selectedNode.confidence * 100)}%
                      </dd>
                    </div>
                    {Object.entries(selectedNode.properties)
                      .filter(([k]) => k !== "centrality")
                      .map(([key, value]) => (
                        <div key={key} className="flex justify-between">
                          <dt className="text-text-secondary capitalize">
                            {key.replace(/_/g, " ")}
                          </dt>
                          <dd className="text-text-primary text-right max-w-[60%] truncate">
                            {String(value)}
                          </dd>
                        </div>
                      ))}
                    <div className="flex justify-between">
                      <dt className="text-text-secondary">Connections</dt>
                      <dd className="text-text-primary">
                        {graphData.links.filter(
                          (l) =>
                            (typeof l.source === "string"
                              ? l.source
                              : l.source.id) === selectedNode.id ||
                            (typeof l.target === "string"
                              ? l.target
                              : l.target.id) === selectedNode.id,
                        ).length}
                      </dd>
                    </div>
                  </dl>
                </div>
              )}
            </div>
          </div>
        </section>
      )}

      {/* ---- What DIALECTICA Computed Panel ---- */}
      {graphData && analysis && (
        <section className="px-6 pb-12 animate-fade-in">
          <div className="max-w-7xl mx-auto">
            <div className="bg-surface border border-border rounded-lg p-6 space-y-6">
              <div className="flex items-center gap-2">
                <Brain size={18} className="text-accent" />
                <h2 className="text-lg font-bold text-text-primary">
                  What DIALECTICA Computed
                </h2>
                <span className="text-xs text-text-secondary/60 ml-2">
                  Deterministic symbolic reasoning + structured extraction
                </span>
              </div>

              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
                {/* Glasl Escalation Stage */}
                <div className="bg-background border border-border rounded-lg p-4 space-y-3">
                  <div className="flex items-center gap-2">
                    <TrendingUp size={14} className="text-text-secondary" />
                    <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wider">
                      Glasl Escalation
                    </h3>
                  </div>
                  {analysis.glaslStage > 0 ? (
                    <div className="space-y-2">
                      <div className="flex items-end gap-2">
                        <span
                          className="text-3xl font-bold font-mono"
                          style={{
                            color:
                              GLASL_COLORS[glaslLevel(analysis.glaslStage)],
                          }}
                        >
                          {analysis.glaslStage}
                        </span>
                        <span className="text-xs text-text-secondary pb-1">
                          / 9
                        </span>
                      </div>
                      <p className="text-sm text-text-secondary">
                        {analysis.glaslLabel}
                      </p>
                      {/* Stage indicator bar */}
                      <div className="flex gap-0.5">
                        {Array.from({ length: 9 }, (_, i) => {
                          const stage = i + 1;
                          const level = glaslLevel(stage);
                          const isActive = stage <= analysis.glaslStage;
                          return (
                            <div
                              key={stage}
                              className="h-2 flex-1 rounded-sm transition-all"
                              style={{
                                backgroundColor: isActive
                                  ? GLASL_COLORS[level]
                                  : "rgba(148,163,184,0.15)",
                              }}
                            />
                          );
                        })}
                      </div>
                      <div className="flex justify-between text-[9px] text-text-secondary/50 uppercase tracking-wider">
                        <span>win-win</span>
                        <span>win-lose</span>
                        <span>lose-lose</span>
                      </div>
                    </div>
                  ) : (
                    <p className="text-sm text-text-secondary/50">
                      No conflict node with Glasl stage detected
                    </p>
                  )}
                </div>

                {/* Deterministic vs Probabilistic */}
                <div className="bg-background border border-border rounded-lg p-4 space-y-3">
                  <div className="flex items-center gap-2">
                    <Shield size={14} className="text-text-secondary" />
                    <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wider">
                      Conclusion Types
                    </h3>
                  </div>
                  <div className="space-y-3">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-green-500/10 flex items-center justify-center">
                        <Lock size={14} className="text-green-500" />
                      </div>
                      <div>
                        <div className="text-xl font-bold font-mono text-green-500">
                          {analysis.deterministicCount}
                        </div>
                        <div className="text-[10px] text-text-secondary uppercase tracking-wider">
                          Deterministic
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-blue-500/10 flex items-center justify-center">
                        <Sparkles size={14} className="text-blue-500" />
                      </div>
                      <div>
                        <div className="text-xl font-bold font-mono text-blue-500">
                          {analysis.probabilisticCount}
                        </div>
                        <div className="text-[10px] text-text-secondary uppercase tracking-wider">
                          Probabilistic
                        </div>
                      </div>
                    </div>
                    {/* Ratio bar */}
                    <div className="flex gap-0 h-2 rounded-full overflow-hidden">
                      <div
                        className="bg-green-500 transition-all"
                        style={{
                          width: `${(analysis.deterministicCount / (analysis.deterministicCount + analysis.probabilisticCount)) * 100}%`,
                        }}
                      />
                      <div
                        className="bg-blue-500 transition-all"
                        style={{
                          width: `${(analysis.probabilisticCount / (analysis.deterministicCount + analysis.probabilisticCount)) * 100}%`,
                        }}
                      />
                    </div>
                  </div>
                </div>

                {/* Theory Frameworks */}
                <div className="bg-background border border-border rounded-lg p-4 space-y-3">
                  <div className="flex items-center gap-2">
                    <Scale size={14} className="text-text-secondary" />
                    <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wider">
                      Theory Frameworks
                    </h3>
                  </div>
                  <div className="space-y-1.5">
                    {analysis.theoryFrameworks.map((tf) => (
                      <div
                        key={tf.name}
                        className="flex items-center gap-2 group"
                        title={tf.description}
                      >
                        {tf.fired ? (
                          <CheckCircle2
                            size={12}
                            className="text-green-500 shrink-0"
                          />
                        ) : (
                          <div className="w-3 h-3 rounded-full border border-surface-active shrink-0" />
                        )}
                        <span
                          className={`text-xs ${tf.fired ? "text-text-primary" : "text-text-secondary/40"}`}
                        >
                          {tf.name}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Confidence Distribution */}
                <div className="bg-background border border-border rounded-lg p-4 space-y-3">
                  <div className="flex items-center gap-2">
                    <Target size={14} className="text-text-secondary" />
                    <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wider">
                      Confidence Distribution
                    </h3>
                  </div>
                  <div className="space-y-2.5">
                    {analysis.confidenceBuckets.map((bucket) => {
                      const maxCount = Math.max(
                        ...analysis.confidenceBuckets.map((b) => b.count),
                        1,
                      );
                      return (
                        <div key={bucket.label} className="space-y-1">
                          <div className="flex items-center justify-between text-xs">
                            <span className="text-text-secondary font-mono">
                              {bucket.label}
                            </span>
                            <span className="text-text-primary font-mono font-medium">
                              {bucket.count}
                            </span>
                          </div>
                          <div className="h-2 bg-surface-active rounded-full overflow-hidden">
                            <div
                              className="h-full rounded-full transition-all"
                              style={{
                                width:
                                  bucket.count > 0
                                    ? `${(bucket.count / maxCount) * 100}%`
                                    : "0%",
                                backgroundColor: bucket.color,
                              }}
                            />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* ---- CTA / Links Section ---- */}
      <section className="px-6 pb-16">
        <div className="max-w-3xl mx-auto">
          <div className="bg-surface border border-border rounded-lg p-8 text-center space-y-6">
            <h2 className="text-2xl font-bold text-text-primary">
              Ready to analyze your own conflicts?
            </h2>
            <p className="text-sm text-text-secondary max-w-lg mx-auto">
              DIALECTICA transforms unstructured conflict narratives into structured
              knowledge graphs with deterministic reasoning &mdash; not just summaries.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <a
                href="/workspaces"
                className="inline-flex items-center gap-2 px-6 py-3 bg-teal-600 hover:bg-teal-500 text-white font-semibold rounded-lg text-sm transition-all shadow-lg shadow-teal-600/20 hover:shadow-teal-500/30"
              >
                <Network size={16} />
                Open Workspaces
                <span className="ml-1 text-[10px] font-medium px-1.5 py-0.5 rounded-full bg-white/20 uppercase tracking-wider">
                  Coming Soon
                </span>
              </a>
              <a
                href="/admin/architecture"
                className="inline-flex items-center gap-2 px-6 py-3 bg-surface border border-border hover:border-border-hover text-text-primary font-medium rounded-lg text-sm transition-all hover:bg-surface-hover"
              >
                Explore the full architecture
                <ExternalLink size={14} className="text-text-secondary" />
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* ---- Footer ---- */}
      <footer className="border-t border-border py-6 px-6 text-center text-xs text-text-secondary/50">
        DIALECTICA by TACITUS &mdash; The Universal Data Layer for Human Friction
      </footer>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Stat Card component                                                */
/* ------------------------------------------------------------------ */

function StatCard({
  label,
  value,
}: {
  label: string;
  value: string | number;
}) {
  return (
    <div className="bg-background rounded-lg px-3 py-2.5 border border-border">
      <div className="text-xl font-bold text-text-primary font-mono">
        {value}
      </div>
      <div className="text-xs text-text-secondary mt-0.5">{label}</div>
    </div>
  );
}
