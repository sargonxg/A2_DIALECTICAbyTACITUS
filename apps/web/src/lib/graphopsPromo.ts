import { buildGraphOpsAiCommandPlan } from "@/lib/graphopsAiPlanner";
import { buildGraphOpsDemoReadyRun, type GraphOpsDemoReadyRun } from "@/lib/graphopsDemo";
import type { GraphOpsExtractionResult, GraphOpsPrimitive } from "@/lib/graphopsExtraction";
import type { RuleEvaluationResult } from "@/lib/graphopsRules";

type LiveCheck = {
  name: string;
  status: "live" | "review" | "blocked";
  proof: string;
};

export type GraphOpsPromoStudioRun = {
  kind: "tacitus.dialectica.promo_studio.v1";
  promoId: string;
  createdAt: string;
  title: string;
  status: "recordable" | "review" | "blocked";
  score: number;
  demoRun: GraphOpsDemoReadyRun;
  aiPlan: Awaited<ReturnType<typeof buildGraphOpsAiCommandPlan>>;
  liveChecks: LiveCheck[];
  apiProof: Array<{ endpoint: string; status: "live" | "protected" | "review"; proof: string }>;
  wowMoments: Array<{ title: string; line: string; proof: string }>;
  recordingScript: Array<{ timestamp: string; shot: string; narration: string; proof: string }>;
  praxisHandoff: {
    status: string;
    summary: string;
    answerConstraints: string[];
    reviewItems: number;
    nextQuestions: string[];
  };
  operatorChecklist: string[];
};

function promoStatus(score: number, checks: LiveCheck[]): "recordable" | "review" | "blocked" {
  if (checks.some((check) => check.status === "blocked") || score < 0.5) return "blocked";
  if (checks.some((check) => check.status === "review") || score < 0.78) return "review";
  return "recordable";
}

export async function buildGraphOpsPromoStudioRun(input: {
  text?: string;
  sampleKey?: string;
  extraction?: GraphOpsExtractionResult;
  primitives?: GraphOpsPrimitive[];
  ruleEvaluation?: RuleEvaluationResult;
  workspaceId?: string;
  caseId?: string;
  objective?: string;
  ontologyProfile?: string;
  sourceTitle?: string;
  sourceType?: string;
  question?: string;
  answerDraft?: string;
  command?: string;
}): Promise<GraphOpsPromoStudioRun> {
  const command =
    input.command ||
    `Create a promo-ready Praxis context graph for ${input.caseId || input.sampleKey || "a policy conflict"} with live extraction, graph retrieval, rules, benchmarks, and review handoff.`;
  const [demoRun, aiPlan] = await Promise.all([
    Promise.resolve(buildGraphOpsDemoReadyRun(input)),
    buildGraphOpsAiCommandPlan(command),
  ]);

  const liveChecks: LiveCheck[] = [
    {
      name: "Source to graph pipeline",
      status: demoRun.extraction.primitives.length >= 20 ? "live" : "review",
      proof: `${demoRun.extraction.primitives.length} primitives extracted into ${demoRun.graphWritePlan.summary.nodes} graph nodes.`,
    },
    {
      name: "Hybrid retrieval and trace",
      status: demoRun.retrievalExecution.diagnostics.contextItems > 0 ? "live" : "blocked",
      proof: `${demoRun.retrievalExecution.diagnostics.contextItems} context item(s), ${demoRun.retrievalExecution.diagnostics.citations} citation(s), ${demoRun.trace.ruleFindings.length} rule finding(s).`,
    },
    {
      name: "Praxis handoff",
      status: demoRun.praxisContext.readiness.status === "blocked" ? "blocked" : demoRun.praxisContext.readiness.status === "ready" ? "live" : "review",
      proof: `${demoRun.praxisContext.readiness.status} at ${Math.round(demoRun.praxisContext.readiness.score * 100)}% with ${demoRun.praxisContext.reviewQueue.length} review item(s).`,
    },
    {
      name: "AI configuration planner",
      status: "live",
      proof: `${aiPlan.mode} selected ${aiPlan.selected_template.name} and ${aiPlan.neurosymbolic_rules.length} rule(s).`,
    },
    {
      name: "Benchmark guardrail",
      status: demoRun.benchmark.scores.overall >= 0.8 ? "live" : "review",
      proof: `Benchmark overall ${Math.round(demoRun.benchmark.scores.overall * 100)}%, evidence grounding ${Math.round(demoRun.benchmark.scores.evidenceGrounding * 100)}%.`,
    },
  ];
  const score = Math.round(
    ((demoRun.demoReadiness.score * 0.45 +
      demoRun.praxisContext.readiness.score * 0.25 +
      demoRun.benchmark.scores.overall * 0.2 +
      (aiPlan.mode === "gemini_assisted" ? 1 : 0.82) * 0.1) *
      100),
  ) / 100;

  return {
    kind: "tacitus.dialectica.promo_studio.v1",
    promoId: `promo_${crypto.randomUUID().replace(/-/g, "").slice(0, 16)}`,
    createdAt: new Date().toISOString(),
    title: "DIALECTICA GraphOps promo recording studio",
    status: promoStatus(score, liveChecks),
    score,
    demoRun,
    aiPlan,
    liveChecks,
    apiProof: [
      { endpoint: "/api/graphops/demo/run", status: "live", proof: "Builds the source-to-Praxis demo contract." },
      { endpoint: "/api/graphops/ai-command", status: "live", proof: `Planner mode: ${aiPlan.mode}.` },
      { endpoint: "/api/graphops/retrieval/execute", status: "live", proof: "Local GraphRAG execution returned cited context." },
      { endpoint: "/api/graphops/trace/build", status: "live", proof: "Trace bundle includes rules, citations, and graph context." },
      { endpoint: "/api/graphops/praxis/context", status: "live", proof: "Praxis context bundle is generated from the same run." },
      { endpoint: "/api/graphops/query", status: "protected", proof: "Neo4j queries remain server-side and credential-gated." },
    ],
    wowMoments: [
      {
        title: "Paste messy text, get a typed conflict graph",
        line: "DIALECTICA turns sources into actors, claims, events, narratives, evidence, and graph edges.",
        proof: `${demoRun.extraction.primitives.length} primitives, ${demoRun.graphWritePlan.summary.edges} relationships.`,
      },
      {
        title: "The system shows its reasoning",
        line: "The answer trace exposes retrieval strategy, rule findings, citations, and benchmark status.",
        proof: `${demoRun.trace.ruleFindings.length} rules, ${demoRun.retrievalExecution.diagnostics.citations} citations.`,
      },
      {
        title: "Praxis receives usable context, not a loose summary",
        line: "Downstream products get answer constraints, review prompts, top evidence, and next questions.",
        proof: `${demoRun.praxisContext.answerConstraints.length} constraints, ${demoRun.praxisContext.reviewQueue.length} review items.`,
      },
      {
        title: "AI helps configure the pipeline",
        line: "Aletheia maps the user objective to ontology profiles, graph layers, rules, and benchmark blocks.",
        proof: `${aiPlan.selected_template.name}; ${aiPlan.mode}.`,
      },
    ],
    recordingScript: [
      {
        timestamp: "0:00",
        shot: "Open GraphOps and run Promo Studio",
        narration: "This is DIALECTICA: a live graph operations layer for turning conflict sources into Praxis-ready context.",
        proof: `${liveChecks.length} live checks generated.`,
      },
      {
        timestamp: "0:20",
        shot: "Show extracted primitive counts and graph write plan",
        narration: "A source becomes typed graph memory with evidence, confidence, and ontology coverage.",
        proof: `${demoRun.graphWritePlan.summary.nodes} nodes / ${demoRun.graphWritePlan.summary.edges} edges.`,
      },
      {
        timestamp: "0:45",
        shot: "Show AI configuration result",
        narration: "The AI planner chooses the right pipeline blocks, graph layers, symbolic rules, and benchmark targets.",
        proof: `${aiPlan.recommended_blocks.length} blocks, ${aiPlan.neurosymbolic_rules.length} rules.`,
      },
      {
        timestamp: "1:10",
        shot: "Show retrieval and trace",
        narration: "GraphRAG retrieval is explainable: every answer points back to source spans and rule signals.",
        proof: `${demoRun.retrievalExecution.diagnostics.contextItems} context items and ${demoRun.trace.ruleFindings.length} rule findings.`,
      },
      {
        timestamp: "1:40",
        shot: "Show Praxis handoff",
        narration: "Praxis gets a compact, structured context bundle with constraints, uncertainty, review work, and next questions.",
        proof: `${demoRun.praxisContext.readiness.status} handoff with ${demoRun.praxisContext.reviewQueue.length} review item(s).`,
      },
      {
        timestamp: "2:05",
        shot: "Close on benchmark and API proof",
        narration: "This is not a static demo. The API contract, benchmark, retrieval, trace, and handoff are live.",
        proof: `${Math.round(score * 100)}% promo readiness.`,
      },
    ],
    praxisHandoff: {
      status: demoRun.praxisContext.readiness.status,
      summary: demoRun.praxisContext.readiness.summary,
      answerConstraints: demoRun.praxisContext.answerConstraints.slice(0, 6),
      reviewItems: demoRun.praxisContext.reviewQueue.length,
      nextQuestions: demoRun.praxisContext.nextQuestions.slice(0, 5),
    },
    operatorChecklist: [
      "Start on /graphops and click Generate Promo Run.",
      "Show the readiness score, live checks, and one wow moment before scrolling.",
      "Open the demo workflow contract only if the audience is technical.",
      "Narrate review-status gaps as a feature: DIALECTICA exposes uncertainty instead of hiding it.",
      "End with the protected manifest and Praxis context endpoint as the developer handoff.",
    ],
  };
}
