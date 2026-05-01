import type { GraphOpsBenchmarkResult } from "@/lib/graphopsBenchmark";
import type { GraphOpsExtractionResult } from "@/lib/graphopsExtraction";

export type WorkbenchBlockStatus = "ready" | "usable" | "partial" | "blocked" | "planned";

export type GraphOpsWorkbenchBlock = {
  id: string;
  stage: string;
  title: string;
  status: WorkbenchBlockStatus;
  score: number;
  proof: string;
  nextAction: string;
  apiSurface?: string;
};

export type GraphOpsWorkbenchStatus = {
  mode: "graphops_workbench_status";
  generatedAt: string;
  overallScore: number;
  nextEngineeringTarget: {
    title: string;
    rationale: string;
    successCriteria: string[];
  };
  blocks: GraphOpsWorkbenchBlock[];
  developerSurfaces: Array<{
    name: string;
    endpoint: string;
    role: string;
    status: WorkbenchBlockStatus;
  }>;
  researchAlignment: Array<{
    pattern: string;
    implementationTarget: string;
    status: WorkbenchBlockStatus;
  }>;
};

type WorkbenchInput = {
  extraction?: Partial<GraphOpsExtractionResult> | null;
  benchmark?: Partial<GraphOpsBenchmarkResult> | null;
  recentRunCount?: number;
  recentBenchmarkCount?: number;
  neo4jConfigured?: boolean;
  databricksConfigured?: boolean;
};

function clamp(value: number) {
  return Math.max(0, Math.min(1, Math.round(value * 100) / 100));
}

function statusFromScore(score: number, blocked = false): WorkbenchBlockStatus {
  if (blocked) return "blocked";
  if (score >= 0.9) return "ready";
  if (score >= 0.7) return "usable";
  if (score >= 0.35) return "partial";
  return "planned";
}

function count(extraction: WorkbenchInput["extraction"], type: string) {
  const counts = extraction?.counts as Record<string, number> | undefined;
  return counts?.[type] ?? 0;
}

export function buildGraphOpsWorkbenchStatus(input: WorkbenchInput): GraphOpsWorkbenchStatus {
  const extraction = input.extraction;
  const benchmark = input.benchmark;
  const quality = extraction?.quality as { score?: number; evidenceCoverage?: number } | undefined;
  const ruleEvaluation = extraction?.ruleEvaluation as
    | { summary?: { fired?: number; warning?: number; blocker?: number } }
    | undefined;
  const benchmarkOverall = benchmark?.scores?.overall ?? (input.recentBenchmarkCount ? 0.55 : 0.2);

  const ingestScore = clamp(extraction?.extractionRunId ? 1 : input.recentRunCount ? 0.75 : 0.35);
  const ontologyScore = clamp(
    extraction?.dynamicOntology ? 0.9 : count(extraction, "PreExtractionPlan") > 0 ? 0.72 : 0.4,
  );
  const temporalScore = clamp(
    count(extraction, "Episode") > 0
      ? Math.min(1, count(extraction, "Episode") / 4 + 0.35)
      : extraction?.preExtraction ? 0.45 : 0.25,
  );
  const structureScore = clamp((quality?.score ?? 0) / 100 || (count(extraction, "Claim") > 0 ? 0.65 : 0.25));
  const graphScore = clamp(input.neo4jConfigured ? 0.85 : extraction?.graphPreview ? 0.55 : 0.25);
  const reasonScore = clamp(ruleEvaluation?.summary ? 0.75 - (ruleEvaluation.summary.blocker ?? 0) * 0.2 : 0.35);
  const benchmarkScore = clamp(benchmarkOverall);
  const serveScore = clamp(
    (input.neo4jConfigured ? 0.35 : 0.1) +
      (input.databricksConfigured ? 0.25 : 0.1) +
      (benchmarkOverall >= 0.75 ? 0.25 : 0.05) +
      (extraction?.extractionRunId ? 0.15 : 0),
  );

  const blocks: GraphOpsWorkbenchBlock[] = [
    {
      id: "ingest",
      stage: "Ingest",
      title: "Source intake and run persistence",
      status: statusFromScore(ingestScore),
      score: ingestScore,
      proof: extraction?.extractionRunId
        ? `Active run ${extraction.extractionRunId}`
        : `${input.recentRunCount ?? 0} saved local run(s) available`,
      nextAction: "Add source packs, license/trust fields, and export controls for each run.",
      apiSurface: "/api/graphops/ingest",
    },
    {
      id: "ontology",
      stage: "Ontology",
      title: "Dynamic ontology and core primitive mapping",
      status: statusFromScore(ontologyScore),
      score: ontologyScore,
      proof: extraction?.dynamicOntology
        ? "Dynamic ontology plan attached to the extraction."
        : "Profiles exist; attach a fresh extraction to score exact coverage.",
      nextAction: "Add visual custom-type diffing and user approval for ontology changes.",
      apiSurface: "/api/graphops/ontology/create",
    },
    {
      id: "temporal",
      stage: "Temporal",
      title: "Episode segmentation and turning points",
      status: statusFromScore(temporalScore),
      score: temporalScore,
      proof: `${count(extraction, "Episode")} episode primitive(s) detected.`,
      nextAction: "Add editable episode boundaries, phase labels, and before/after validation tests.",
    },
    {
      id: "structure",
      stage: "Structure",
      title: "Typed primitive extraction with evidence",
      status: statusFromScore(structureScore),
      score: structureScore,
      proof: `${count(extraction, "Claim")} claims, ${count(extraction, "Actor")} actors, ${count(extraction, "EvidenceSpan")} evidence spans.`,
      nextAction: "Add targeted extraction retries for missing primitives and low-evidence claims.",
      apiSurface: "/api/graphops/ingest",
    },
    {
      id: "graph",
      stage: "Graph",
      title: "Neo4j graph memory and hybrid retrieval",
      status: statusFromScore(graphScore, !input.neo4jConfigured && graphScore < 0.4),
      score: graphScore,
      proof: input.neo4jConfigured ? "Neo4j environment is configured." : "Graph preview works; production writeback needs secrets.",
      nextAction: "Write BenchmarkRun, PipelineRun, and ReviewDecision nodes beside extracted primitives.",
      apiSurface: "/api/graphops/query",
    },
    {
      id: "reason",
      stage: "Reason",
      title: "Neurosymbolic rules and answer constraints",
      status: statusFromScore(reasonScore),
      score: reasonScore,
      proof: ruleEvaluation?.summary
        ? `${ruleEvaluation.summary.fired ?? 0} rule signal(s), ${ruleEvaluation.summary.warning ?? 0} warning(s).`
        : "Rule API exists; run a case extraction to score signals.",
      nextAction: "Turn rule signals into a review queue and answer-plan constraints.",
      apiSurface: "/api/graphops/rules/evaluate",
    },
    {
      id: "benchmark",
      stage: "Benchmark",
      title: "Local and Databricks benchmark loop",
      status: statusFromScore(benchmarkScore),
      score: benchmarkScore,
      proof: benchmark?.benchmarkId
        ? `Active benchmark ${benchmark.benchmarkId}`
        : `${input.recentBenchmarkCount ?? 0} saved benchmark run(s) available`,
      nextAction: "Add gold-case corpora and baseline-vs-graph answer judge prompts.",
      apiSurface: "/api/graphops/benchmarks/run",
    },
    {
      id: "serve",
      stage: "Serve",
      title: "Praxis and developer workbench contract",
      status: statusFromScore(serveScore),
      score: serveScore,
      proof: "Manifest, ingest, rules, benchmark, and workbench status endpoints are available.",
      nextAction: "Add scoped product auth, SDK examples, and embeddable workbench cards.",
      apiSurface: "/api/graphops/workbench/status",
    },
  ];

  const weakest = [...blocks].sort((a, b) => a.score - b.score)[0];
  const overallScore = clamp(blocks.reduce((sum, block) => sum + block.score, 0) / blocks.length);

  return {
    mode: "graphops_workbench_status",
    generatedAt: new Date().toISOString(),
    overallScore,
    nextEngineeringTarget: {
      title: weakest.title,
      rationale: weakest.nextAction,
      successCriteria: [
        "A user can see the block status without reading docs.",
        "The API returns the same block state for Praxis or another developer tool.",
        "The next action is tied to a measurable extraction, graph, rule, or benchmark signal.",
      ],
    },
    blocks,
    developerSurfaces: [
      { name: "Workbench status", endpoint: "/api/graphops/workbench/status", role: "Readiness, next target, and block map.", status: "usable" },
      { name: "Manifest", endpoint: "/api/graphops/manifest", role: "Stable product-to-product capability contract.", status: "usable" },
      { name: "Ingest", endpoint: "/api/graphops/ingest", role: "Create graph-ready primitives from text, samples, TXT, or PDF.", status: "usable" },
      { name: "Rules", endpoint: "/api/graphops/rules/evaluate", role: "Generate answer constraints and benchmark targets.", status: "usable" },
      { name: "Benchmarks", endpoint: "/api/graphops/benchmarks/run", role: "Score graph readiness and answer grounding.", status: "usable" },
      { name: "Hybrid graph query", endpoint: "/api/graphops/query", role: "Allowlisted Neo4j traversal for graph-grounded answers.", status: input.neo4jConfigured ? "usable" : "blocked" },
    ],
    researchAlignment: [
      { pattern: "Structured extraction with source grounding", implementationTarget: "EvidenceSpan-first primitive extraction and visual review.", status: "usable" },
      { pattern: "GraphRAG indexing and prompt tuning", implementationTarget: "Dynamic ontology plans, episodes, and targeted extraction retries.", status: "partial" },
      { pattern: "Hybrid vector, full-text, and graph retrieval", implementationTarget: "Neo4j hybrid retrievers plus Databricks vector indexes.", status: input.neo4jConfigured ? "partial" : "blocked" },
      { pattern: "Offline evaluation sets and production monitoring", implementationTarget: "Local benchmark API plus Databricks benchmark Delta tables.", status: "usable" },
      { pattern: "Human review and root-cause diagnostics", implementationTarget: "Rule signals, benchmark diagnostics, and review queues.", status: "partial" },
    ],
  };
}
