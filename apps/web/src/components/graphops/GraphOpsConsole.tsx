"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import {
  Activity,
  ArrowRight,
  BookOpen,
  Brain,
  CheckCircle2,
  Database,
  GitBranch,
  Goal,
  KeyRound,
  Layers,
  Lock,
  Network,
  Package,
  Play,
  Shield,
  Sparkles,
  Upload,
  Workflow,
} from "lucide-react";
import ForceGraph from "@/components/graph/ForceGraph";
import {
  analystFlow,
  benchmarkPlan,
  benchmarkBlockCatalog,
  benchmarkRunCards,
  benchmarkScenarios,
  conflictOntologyExtensions,
  conflictUseCases,
  ahaWorkflows,
  agenticTools,
  ambitionRoadmap,
  aiCommandExamples,
  databricksJobs,
  databricksNeo4jExplanation,
  dynamicOntologyEngine,
  dynamicOntologyTables,
  embeddableSurfaces,
  demoGraph,
  graphLayerBlueprints,
  graphCategories,
  graphOpsPipeline,
  ingestionTreeTemplate,
  liveDeltaTables,
  neo4jStatus,
  neurosymbolicRuleCatalog,
  ontologyContracts,
  ontologyEdges,
  ontologyNodes,
  operatorDeliverables,
  ontologyProfileOptions,
  ontologyTiers,
  orchestrationEvents,
  precompiledNeeds,
  qualityGates,
  researchSignals,
  sampleCypherQueries,
  situationPortalBlueprint,
  safetyBoundaries,
  sourcePacks,
  nextSprintPriorities,
  pipelineConfigurationExamples,
  pipelineBlockCatalog,
  pipelineStageGuide,
  topTenBuildPriorities,
  workspaceProjectTemplates,
  configurationQualityChecklist,
} from "@/data/graphops";

const layerCards = [
  {
    name: "Source Graph",
    icon: BookOpen,
    detail: "Document, chapter, paragraph, chunk, quote, license, source reliability.",
  },
  {
    name: "Situation Graph",
    icon: Network,
    detail: "Actors, conflicts, events, issues, interests, norms, processes, outcomes.",
  },
  {
    name: "Reasoning Graph",
    icon: Brain,
    detail: "Symbolic rule outputs, inferred facts, contradictions, confidence, review status.",
  },
  {
    name: "Activity Graph",
    icon: Activity,
    detail: "Users, projects, workspaces, analyst decisions, approvals, and corrections.",
  },
  {
    name: "Signal Graph",
    icon: Sparkles,
    detail: "Databricks features, review queues, centrality, link candidates, quality scores.",
  },
];

const stageStyles: Record<string, string> = {
  Ingest: "border-blue-500/30 bg-blue-500/10 text-blue-200",
  Ontology: "border-violet-500/30 bg-violet-500/10 text-violet-200",
  Temporal: "border-amber-500/30 bg-amber-500/10 text-amber-200",
  Structure: "border-emerald-500/30 bg-emerald-500/10 text-emerald-200",
  Graph: "border-cyan-500/30 bg-cyan-500/10 text-cyan-200",
  Reason: "border-fuchsia-500/30 bg-fuchsia-500/10 text-fuchsia-200",
  Act: "border-rose-500/30 bg-rose-500/10 text-rose-200",
  Benchmark: "border-slate-400/30 bg-slate-400/10 text-slate-200",
};

function stageClass(stage: string) {
  return stageStyles[stage] ?? "border-border bg-background text-text-secondary";
}

const bookStarts = [
  {
    title: "Romeo and Juliet",
    id: "1513",
    why: "Family conflict, escalation, alliance, emotional intensity, mediation failure.",
  },
  {
    title: "War and Peace",
    id: "2600",
    why: "Macro conflict, elite networks, military events, alliances, causal chains.",
  },
  {
    title: "Crime and Punishment",
    id: "2554",
    why: "Moral conflict, narratives, norm violation, guilt, trust, confession dynamics.",
  },
  {
    title: "The Federalist Papers",
    id: "1404",
    why: "Institutional conflict, political norms, interests, public narratives.",
  },
];

type QueryState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "ok"; records: unknown[]; cypher: string }
  | { status: "error"; message: string; cypher?: string };

type DatabricksState =
  | { status: "loading" }
  | { status: "ready"; mode: string; message?: string; jobs: typeof databricksJobs }
  | { status: "error"; message: string };

type TableState =
  | { status: "loading" }
  | { status: "ready"; mode: string; message?: string; tables: typeof liveDeltaTables }
  | { status: "error"; message: string; tables: typeof liveDeltaTables };

type IngestState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "ok"; result: Record<string, unknown> }
  | { status: "error"; message: string };

type AgentRunState =
  | { status: "idle" }
  | { status: "loading"; agent: string }
  | { status: "ok"; result: Record<string, unknown> }
  | { status: "error"; message: string };

type PipelineState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "ok"; result: Record<string, unknown> }
  | { status: "error"; message: string };

type AiCommandState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "ok"; result: Record<string, unknown> }
  | { status: "error"; message: string };

export default function GraphOpsConsole() {
  const [activeQuery, setActiveQuery] = useState(sampleCypherQueries[0].title);
  const [activeScenarioId, setActiveScenarioId] = useState(benchmarkScenarios[0].id);
  const [activeProfileId, setActiveProfileId] = useState(ontologyProfileOptions[0].id);
  const [activeNeedId, setActiveNeedId] = useState(precompiledNeeds[0].id);
  const [activeTemplateId, setActiveTemplateId] = useState(workspaceProjectTemplates[0].id);
  const [activeUseCaseName, setActiveUseCaseName] = useState(conflictUseCases[0].name);
  const [activeSourcePackId, setActiveSourcePackId] = useState(sourcePacks[0].id);
  const [workspaceId, setWorkspaceId] = useState("books-romeo-juliet");
  const [caseId, setCaseId] = useState("romeo-juliet-conflict");
  const [objective, setObjective] = useState(precompiledNeeds[0].objective);
  const [sourceText, setSourceText] = useState("");
  const [writeGraph, setWriteGraph] = useState(false);
  const [sendToDatabricks, setSendToDatabricks] = useState(false);
  const [triggerWorkflowAfterIngest, setTriggerWorkflowAfterIngest] = useState(false);
  const [databricksWorkflowKey, setDatabricksWorkflowKey] = useState("book-demo");
  const [pipelineBackendMode, setPipelineBackendMode] = useState("databricks-neo4j");
  const [pipelineStageToDatabricks, setPipelineStageToDatabricks] = useState(true);
  const [pipelineTemporal, setPipelineTemporal] = useState(true);
  const [pipelineKnowledge, setPipelineKnowledge] = useState(true);
  const [pipelineBenchmarks, setPipelineBenchmarks] = useState(true);
  const [aiCommand, setAiCommand] = useState(aiCommandExamples[0].command);
  const [queryState, setQueryState] = useState<QueryState>({ status: "idle" });
  const [databricksState, setDatabricksState] = useState<DatabricksState>({ status: "loading" });
  const [tableState, setTableState] = useState<TableState>({ status: "loading" });
  const [ingestState, setIngestState] = useState<IngestState>({ status: "idle" });
  const [agentRunState, setAgentRunState] = useState<AgentRunState>({ status: "idle" });
  const [pipelineState, setPipelineState] = useState<PipelineState>({ status: "idle" });
  const [aiCommandState, setAiCommandState] = useState<AiCommandState>({ status: "idle" });
  const databricksJobsUrl =
    process.env.NEXT_PUBLIC_DATABRICKS_JOBS_URL ||
    "https://dbc-69e04818-40fb.cloud.databricks.com/jobs?o=7474658425841042";

  const query = useMemo(
    () => sampleCypherQueries.find((item) => item.title === activeQuery) ?? sampleCypherQueries[0],
    [activeQuery],
  );
  const activeScenario = useMemo(
    () => benchmarkScenarios.find((item) => item.id === activeScenarioId) ?? benchmarkScenarios[0],
    [activeScenarioId],
  );
  const activeProfile = useMemo(
    () => ontologyProfileOptions.find((item) => item.id === activeProfileId) ?? ontologyProfileOptions[0],
    [activeProfileId],
  );
  const activeNeed = useMemo(
    () => precompiledNeeds.find((item) => item.id === activeNeedId) ?? precompiledNeeds[0],
    [activeNeedId],
  );
  const activeTemplate = useMemo(
    () => workspaceProjectTemplates.find((item) => item.id === activeTemplateId) ?? workspaceProjectTemplates[0],
    [activeTemplateId],
  );
  const activeUseCase = useMemo(
    () => conflictUseCases.find((item) => item.name === activeUseCaseName) ?? conflictUseCases[0],
    [activeUseCaseName],
  );
  const activeSourcePack = useMemo(
    () => sourcePacks.find((item) => item.id === activeSourcePackId) ?? sourcePacks[0],
    [activeSourcePackId],
  );
  const workflowOptions = useMemo(
    () => databricksJobs.filter((job) => "actionKey" in job && job.actionKey),
    [],
  );

  async function refreshDatabricksJobs() {
    setDatabricksState({ status: "loading" });
    try {
      const response = await fetch("/api/graphops/databricks/jobs", { cache: "no-store" });
      const payload = await response.json();
      setDatabricksState({
        status: "ready",
        mode: payload.mode ?? "unknown",
        message: payload.message,
        jobs: payload.jobs ?? databricksJobs,
      });
    } catch (error) {
      setDatabricksState({
        status: "error",
        message: error instanceof Error ? error.message : "Could not load Databricks status.",
      });
    }
  }

  async function refreshDeltaTables() {
    setTableState({ status: "loading" });
    try {
      const response = await fetch("/api/graphops/databricks/tables", { cache: "no-store" });
      const payload = await response.json();
      setTableState({
        status: "ready",
        mode: payload.mode ?? "unknown",
        message: payload.message,
        tables: payload.tables ?? liveDeltaTables,
      });
    } catch (error) {
      setTableState({
        status: "error",
        message: error instanceof Error ? error.message : "Could not load Delta table status.",
        tables: liveDeltaTables,
      });
    }
  }

  useEffect(() => {
    refreshDatabricksJobs();
    refreshDeltaTables();
  }, []);

  async function runDatabricksJob(key: string) {
    const response = await fetch("/api/graphops/databricks/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ key }),
    });
    const payload = await response.json();
    if (!response.ok) {
      setDatabricksState({
        status: "error",
        message: payload?.error ?? "Could not trigger Databricks job.",
      });
      return;
    }
    await refreshDatabricksJobs();
  }

  async function runQuery() {
    setQueryState({ status: "loading" });
    try {
      const response = await fetch("/api/graphops/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ queryId: query.title, workspaceId }),
      });
      const payload = await response.json();
      if (!response.ok) {
        setQueryState({
          status: "error",
          message: payload?.error ?? "Query failed",
          cypher: payload?.cypher ?? query.cypher,
        });
        return;
      }
      setQueryState({
        status: "ok",
        records: payload.records ?? [],
        cypher: payload.cypher ?? query.cypher,
      });
    } catch (error) {
      setQueryState({
        status: "error",
        message: error instanceof Error ? error.message : "Query failed",
        cypher: query.cypher,
      });
    }
  }

  function applyNeed(needId: string) {
    const need = precompiledNeeds.find((item) => item.id === needId) ?? precompiledNeeds[0];
    setActiveNeedId(need.id);
    setWorkspaceId(need.workspaceId);
    setCaseId(need.caseId);
    setObjective(need.objective);
    const profile = ontologyProfileOptions.find((item) => item.id === need.profile);
    if (profile) setActiveProfileId(profile.id);
  }

  async function createPipelinePlan() {
    setPipelineState({ status: "loading" });
    try {
      const response = await fetch("/api/graphops/pipelines/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          templateId: activeTemplate.id,
          workspaceId,
          caseId,
          caseName: caseId,
          objective,
          ontologyProfile: activeProfile.id,
          backendMode: pipelineBackendMode,
          includeTemporal: pipelineTemporal,
          includeAbstractKnowledge: pipelineKnowledge,
          includeBenchmarks: pipelineBenchmarks,
          stageToDatabricks: pipelineStageToDatabricks,
        }),
      });
      const payload = await response.json();
      if (!response.ok) {
        setPipelineState({ status: "error", message: payload?.error ?? "Could not create pipeline plan." });
        return;
      }
      setPipelineState({ status: "ok", result: payload });
    } catch (error) {
      setPipelineState({
        status: "error",
        message: error instanceof Error ? error.message : "Could not create pipeline plan.",
      });
    }
  }

  async function runAiCommand() {
    setAiCommandState({ status: "loading" });
    try {
      const response = await fetch("/api/graphops/ai-command", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: aiCommand, workspaceId, caseId, objective }),
      });
      const payload = await response.json();
      if (!response.ok) {
        setAiCommandState({ status: "error", message: payload?.error ?? "AI command failed." });
        return;
      }
      setAiCommandState({ status: "ok", result: payload });
      const selected = payload?.selected_template as { id?: string; defaultObjective?: string; recommendedProfile?: string; workspacePrefix?: string } | undefined;
      if (selected?.id) {
        setActiveTemplateId(selected.id);
        if (selected.defaultObjective) setObjective(selected.defaultObjective);
        const profile = ontologyProfileOptions.find((item) => item.id === selected.recommendedProfile);
        if (profile) setActiveProfileId(profile.id);
        if (selected.workspacePrefix) {
          setWorkspaceId(`${selected.workspacePrefix}-${caseId}`.replace(/[^A-Za-z0-9_.-]/g, "-").toLowerCase());
        }
      }
    } catch (error) {
      setAiCommandState({
        status: "error",
        message: error instanceof Error ? error.message : "AI command failed.",
      });
    }
  }

  async function runIngest(sample = false) {
    setIngestState({ status: "loading" });
    try {
      const response = await fetch("/api/graphops/ingest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          workspaceId,
          caseId,
          objective,
          ontologyProfile: activeProfile.id,
          sampleKey: sample ? activeNeed.sampleKey : "",
          text: sample ? "" : sourceText,
          sourceTitle: sample ? activeNeed.label : "GraphOps pasted text",
          writeGraph,
          sendToDatabricks,
          databricksWorkflowKey: triggerWorkflowAfterIngest ? databricksWorkflowKey : "",
        }),
      });
      const payload = await response.json();
      if (!response.ok) {
        setIngestState({ status: "error", message: payload?.error ?? "Ingestion failed." });
        return;
      }
      setIngestState({ status: "ok", result: payload });
    } catch (error) {
      setIngestState({
        status: "error",
        message: error instanceof Error ? error.message : "Ingestion failed.",
      });
    }
  }

  async function runFileIngest(file: File | null) {
    if (!file) return;
    setIngestState({ status: "loading" });
    const form = new FormData();
    form.set("file", file);
    form.set("workspaceId", workspaceId);
    form.set("caseId", caseId);
    form.set("objective", objective);
    form.set("ontologyProfile", activeProfile.id);
    form.set("writeGraph", String(writeGraph));
    form.set("sendToDatabricks", String(sendToDatabricks));
    form.set("databricksWorkflowKey", triggerWorkflowAfterIngest ? databricksWorkflowKey : "");
    try {
      const response = await fetch("/api/graphops/ingest", {
        method: "POST",
        body: form,
      });
      const payload = await response.json();
      if (!response.ok) {
        setIngestState({ status: "error", message: payload?.error ?? "File ingestion failed." });
        return;
      }
      setIngestState({ status: "ok", result: payload });
    } catch (error) {
      setIngestState({
        status: "error",
        message: error instanceof Error ? error.message : "File ingestion failed.",
      });
    }
  }

  async function runAgent(agentName: string, execute = false) {
    setAgentRunState({ status: "loading", agent: agentName });
    try {
      const response = await fetch("/api/graphops/agents/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          agent: agentName,
          execute,
          workspaceId,
          caseId,
          objective,
        }),
      });
      const payload = await response.json();
      if (!response.ok) {
        setAgentRunState({ status: "error", message: payload?.error ?? "Agent run failed." });
        return;
      }
      setAgentRunState({ status: "ok", result: payload });
      if (execute) await refreshDatabricksJobs();
    } catch (error) {
      setAgentRunState({
        status: "error",
        message: error instanceof Error ? error.message : "Agent run failed.",
      });
    }
  }

  return (
    <div className="space-y-8">
      <section className="grid gap-6 xl:grid-cols-[minmax(0,1.25fr)_minmax(420px,0.75fr)]">
        <div className="space-y-6">
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <span className="inline-flex items-center gap-1 rounded-md border border-emerald-500/30 bg-emerald-500/10 px-2 py-1 font-medium text-emerald-300">
              <Lock size={12} />
              Password protected ops
            </span>
            <span className="inline-flex items-center gap-1 rounded-md border border-blue-500/30 bg-blue-500/10 px-2 py-1 font-medium text-blue-300">
              <Database size={12} />
              Neo4j Aura primary graph
            </span>
            <span className="inline-flex items-center gap-1 rounded-md border border-violet-500/30 bg-violet-500/10 px-2 py-1 font-medium text-violet-300">
              <Workflow size={12} />
              Databricks operational loop
            </span>
          </div>

          <div>
            <h1 className="text-3xl font-bold tracking-tight text-text-primary md:text-4xl">
              TACITUS graph operations console
            </h1>
            <p className="mt-3 max-w-3xl text-sm leading-6 text-text-secondary">
              DIALECTICA is the backbone graph for TACITUS: it turns books, reports,
              transcripts, and case files into ontology-validated Neo4j graphs, then
              uses Databricks to compute graph quality, review queues, and predictive
              signals. The goal is not to store text. The goal is to make conflict
              computable, inspectable, and correctable.
            </p>
          </div>

          <div className="grid gap-3 sm:grid-cols-4">
            {[
              ["15", "ontology nodes"],
              ["20", "edge types"],
              ["5", "graph layers"],
              ["$100", "experiment budget"],
            ].map(([value, label]) => (
              <div key={label} className="rounded-lg border border-border bg-surface p-4">
                <p className="text-2xl font-bold text-text-primary">{value}</p>
                <p className="mt-1 text-xs uppercase tracking-wide text-text-secondary">{label}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-lg border border-border bg-surface p-3">
          <div className="mb-3 flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-text-primary">Live graph preview</p>
              <p className="text-xs text-text-secondary">Sample situation graph shaped for Neo4j</p>
            </div>
            <Network size={18} className="text-accent" />
          </div>
          <div className="overflow-hidden rounded-lg border border-border bg-background">
            <ForceGraph data={demoGraph} width={520} height={360} />
          </div>
        </div>
      </section>

      <section className="rounded-lg border border-border bg-surface p-5">
        <div className="flex flex-col justify-between gap-4 xl:flex-row xl:items-start">
          <div>
            <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
              <Goal size={18} className="text-accent" />
              Understand a conflict
            </h2>
            <p className="mt-2 max-w-4xl text-sm leading-6 text-text-secondary">
              The operator flow starts with a mission, not with a model. DIALECTICA
              asks what the user needs to understand, chooses the right ontology
              profile, structures the sources, builds Neo4j memory, then tests
              whether graph-grounded answers are better than ordinary LLM answers.
            </p>
          </div>
          <div className="rounded-lg border border-accent/30 bg-accent/10 px-4 py-3 text-xs leading-5 text-accent xl:max-w-md">
            Current live proof: open books are chunked in Databricks, ontology candidates
            are extracted with AI Functions, dynamic quality tables are computed, and
            the protected console can trigger workflows and query graph state.
          </div>
        </div>

        <div className="mt-5 grid gap-3 xl:grid-cols-6">
          {analystFlow.map((item) => (
            <div key={item.step} className="rounded-lg border border-border bg-background p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-accent">{item.step}</p>
              <p className="mt-2 text-sm font-semibold text-text-primary">{item.operatorQuestion}</p>
              <p className="mt-3 text-xs leading-5 text-text-secondary">{item.systemAction}</p>
              <p className="mt-3 rounded-md bg-surface px-2 py-1 text-[11px] leading-5 text-text-secondary">
                {item.graphOutput}
              </p>
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-lg border border-border bg-surface p-5">
        <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
          <CheckCircle2 size={18} className="text-accent" />
          Top 10 build priorities
        </h2>
        <p className="mt-2 max-w-4xl text-sm leading-6 text-text-secondary">
          This is the immediate product backlog for making DIALECTICA a usable
          neurosymbolic control plane: upload sources, run Databricks, write Neo4j,
          launch agents, review claims, and benchmark graph-grounded answers.
        </p>
        <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-5">
          {topTenBuildPriorities.map((priority, index) => (
            <div key={priority.item} className="rounded-lg border border-border bg-background p-4">
              <div className="flex items-start justify-between gap-3">
                <p className="text-sm font-semibold text-text-primary">{index + 1}. {priority.item}</p>
                <span className="rounded-md bg-accent/10 px-2 py-1 text-[10px] text-accent">
                  {priority.status}
                </span>
              </div>
              <p className="mt-2 text-xs leading-5 text-text-secondary">{priority.why}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-lg border border-border bg-surface p-5">
        <div className="flex flex-col justify-between gap-4 xl:flex-row xl:items-start">
          <div>
            <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
              <Sparkles size={18} className="text-accent" />
              AI configuration command
            </h2>
            <p className="mt-2 max-w-4xl text-sm leading-6 text-text-secondary">
              Describe what the user needs to build. Aletheia selects a workspace
              type, ontology focus, graph layers, neurosymbolic rules, and benchmark
              blocks before the pipeline is created. If Gemini is configured server-side,
              the same endpoint adds model-generated ontology and episode suggestions;
              otherwise it uses deterministic TACITUS planning rules.
            </p>
          </div>
          <div className="rounded-lg border border-violet-500/30 bg-violet-500/10 px-4 py-3 text-xs leading-5 text-violet-200 xl:max-w-md">
            Rule: AI can propose ontology and graph changes, but every custom concept
            must map back to TACITUS primitives and every answer must preserve provenance.
          </div>
        </div>

        <div className="mt-5 grid gap-5 xl:grid-cols-[minmax(0,1fr)_420px]">
          <div className="space-y-3">
            <textarea
              value={aiCommand}
              onChange={(event) => setAiCommand(event.target.value)}
              className="input-base min-h-[120px] w-full"
              placeholder="Example: Build a labor mediation graph for a union-employer conflict with meeting notes, contract clauses, and local media."
            />
            <div className="flex flex-wrap gap-2">
              {aiCommandExamples.map((example) => (
                <button
                  key={example.command}
                  onClick={() => setAiCommand(example.command)}
                  className="rounded-md border border-border bg-background px-3 py-2 text-left text-[11px] leading-4 text-text-secondary hover:text-accent"
                >
                  {example.command}
                </button>
              ))}
            </div>
            <button onClick={runAiCommand} className="btn-primary inline-flex items-center gap-2">
              <Brain size={15} />
              Generate configuration
            </button>
          </div>

          <div className="rounded-lg border border-border bg-background p-4">
            {aiCommandState.status === "idle" && (
              <div>
                <p className="text-sm font-semibold text-text-primary">What this produces</p>
                <div className="mt-3 space-y-2">
                  {configurationQualityChecklist.slice(0, 5).map((item) => (
                    <p key={item} className="text-xs leading-5 text-text-secondary">- {item}</p>
                  ))}
                </div>
              </div>
            )}
            {aiCommandState.status === "loading" && (
              <p className="text-sm text-accent">Generating pipeline configuration...</p>
            )}
            {aiCommandState.status === "error" && (
              <p className="text-sm text-warning">{aiCommandState.message}</p>
            )}
            {aiCommandState.status === "ok" && (
              <div>
                <p className="text-sm font-semibold text-text-primary">
                  {String(((aiCommandState.result.selected_template as { name?: string })?.name) ?? "Configuration")}
                </p>
                <p className="mt-1 text-xs text-accent">
                  mode: {String(aiCommandState.result.mode)}
                </p>
                <div className="mt-3 space-y-2">
                  {((aiCommandState.result.neurosymbolic_rules as Array<{ id: string; name: string; category: string }>) ?? [])
                    .slice(0, 4)
                    .map((rule) => (
                      <div key={rule.id} className="rounded-md bg-surface px-3 py-2">
                        <p className="text-xs font-semibold text-text-primary">{rule.name}</p>
                        <p className="text-[11px] text-accent">{rule.category}</p>
                      </div>
                    ))}
                </div>
                <pre className="mt-3 max-h-[220px] overflow-auto rounded-md bg-surface p-3 text-[11px] leading-5 text-text-secondary">
                  <code>{JSON.stringify(aiCommandState.result, null, 2)}</code>
                </pre>
              </div>
            )}
          </div>
        </div>
      </section>

      <section className="rounded-lg border border-border bg-surface p-5">
        <div className="flex flex-col justify-between gap-4 xl:flex-row xl:items-start">
          <div>
            <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
              <Workflow size={18} className="text-accent" />
              Workspace pipeline builder
            </h2>
            <p className="mt-2 max-w-4xl text-sm leading-6 text-text-secondary">
              A project is a workspace. A workspace can be a book, mediation file,
              policy dispute, argument corpus, or field situation. DIALECTICA turns
              that workspace into a block pipeline: ingest sources, generate a dynamic
              ontology, segment temporal episodes, write graph memory, run agents,
              and benchmark the result.
            </p>
          </div>
          <div className="rounded-lg border border-accent/30 bg-accent/10 px-4 py-3 text-xs leading-5 text-accent xl:max-w-md">
            {dynamicOntologyEngine.name}: {dynamicOntologyEngine.coreRule}
          </div>
        </div>

        <div className="mt-5 grid gap-3 md:grid-cols-4 xl:grid-cols-8">
          {pipelineStageGuide.map((item) => (
            <div key={item.stage} className={`rounded-lg border p-3 ${stageClass(item.stage)}`}>
              <p className="text-sm font-semibold">{item.stage}</p>
              <p className="mt-2 text-[11px] leading-5 opacity-90">{item.purpose}</p>
            </div>
          ))}
        </div>

        <div className="mt-5 grid gap-6 xl:grid-cols-[380px_minmax(0,1fr)]">
          <div className="space-y-3">
            {workspaceProjectTemplates.map((template) => (
              <button
                key={template.id}
                onClick={() => {
                  setActiveTemplateId(template.id);
                  setWorkspaceId(`${template.workspacePrefix}-${caseId}`.replace(/[^A-Za-z0-9_.-]/g, "-").toLowerCase());
                  setObjective(template.defaultObjective);
                  const profile = ontologyProfileOptions.find((item) => item.id === template.recommendedProfile);
                  if (profile) setActiveProfileId(profile.id);
                }}
                className={`w-full rounded-lg border px-3 py-3 text-left transition-colors ${
                  template.id === activeTemplate.id
                    ? "border-accent bg-accent/10"
                    : "border-border bg-background hover:border-border-hover"
                }`}
              >
                <p className="text-sm font-semibold text-text-primary">{template.name}</p>
                <p className="mt-1 text-xs leading-5 text-text-secondary">{template.description}</p>
                <p className="mt-2 text-[11px] text-accent">{template.sourceExamples}</p>
              </button>
            ))}
          </div>

          <div className="space-y-4">
            <div className="grid gap-3 md:grid-cols-3">
              <label className="block">
                <span className="text-xs font-medium uppercase tracking-wide text-text-secondary">Backend mode</span>
                <select value={pipelineBackendMode} onChange={(event) => setPipelineBackendMode(event.target.value)} className="input-base mt-2 w-full">
                  <option value="databricks-neo4j">Databricks + Neo4j</option>
                  <option value="local-python">Local Python + files</option>
                  <option value="neo4j-only">Neo4j-only</option>
                  <option value="falkordb">FalkorDB experimental</option>
                </select>
              </label>
              <label className="block">
                <span className="text-xs font-medium uppercase tracking-wide text-text-secondary">Workspace</span>
                <input value={workspaceId} onChange={(event) => setWorkspaceId(event.target.value)} className="input-base mt-2 w-full" />
              </label>
              <label className="block">
                <span className="text-xs font-medium uppercase tracking-wide text-text-secondary">Case</span>
                <input value={caseId} onChange={(event) => setCaseId(event.target.value)} className="input-base mt-2 w-full" />
              </label>
            </div>

            <div className="grid gap-3 md:grid-cols-4">
              {[
                ["Temporal episodes", pipelineTemporal, setPipelineTemporal],
                ["Abstract knowledge graph", pipelineKnowledge, setPipelineKnowledge],
                ["Benchmark blocks", pipelineBenchmarks, setPipelineBenchmarks],
                ["Stage plan to Databricks", pipelineStageToDatabricks, setPipelineStageToDatabricks],
              ].map(([label, checked, setter]) => (
                <label key={String(label)} className="rounded-lg border border-border bg-background p-3 text-xs text-text-secondary">
                  <input
                    type="checkbox"
                    checked={Boolean(checked)}
                    onChange={(event) => (setter as (value: boolean) => void)(event.target.checked)}
                    className="mr-2"
                  />
                  {String(label)}
                </label>
              ))}
            </div>

            <button onClick={createPipelinePlan} className="btn-primary inline-flex items-center gap-2">
              <Play size={15} />
              Create pipeline plan
            </button>

            {pipelineState.status === "loading" && (
              <div className="rounded-lg border border-accent/30 bg-accent/10 p-3 text-sm text-accent">
                Building workspace pipeline artifact...
              </div>
            )}
            {pipelineState.status === "error" && (
              <div className="rounded-lg border border-warning/30 bg-warning/10 p-3 text-sm text-warning">
                {pipelineState.message}
              </div>
            )}
            {pipelineState.status === "ok" && (
              <div className="grid gap-4 xl:grid-cols-[0.9fr_1.1fr]">
                <div className="rounded-lg border border-border bg-background p-4">
                  <p className="text-sm font-semibold text-text-primary">
                    {String(((pipelineState.result.artifact as Record<string, unknown>)?.pipeline_id) ?? "Pipeline")}
                  </p>
                  <p className="mt-2 text-xs text-text-secondary">
                    {String(((pipelineState.result.artifact as Record<string, unknown>)?.backend_mode) ?? "")}
                  </p>
                  <p className="mt-3 text-xs leading-5 text-accent">
                    {String(((pipelineState.result.databricks as { message?: string })?.message) ?? "Plan created locally.")}
                  </p>
                  <div className="mt-3 space-y-2">
                    {(((pipelineState.result.artifact as { blocks?: Array<{ order: number; name: string; status: string }> })?.blocks) ?? []).map((block) => (
                      <div key={`${block.order}-${block.name}`} className="rounded-md bg-surface px-3 py-2">
                        <p className="text-xs font-semibold text-text-primary">{block.order}. {block.name}</p>
                        <p className="text-[11px] text-text-secondary">{block.status}</p>
                      </div>
                    ))}
                  </div>
                </div>
                <pre className="max-h-[460px] overflow-auto rounded-lg border border-border bg-background p-4 text-xs leading-5 text-text-secondary">
                  <code>{JSON.stringify(pipelineState.result, null, 2)}</code>
                </pre>
              </div>
            )}
          </div>
        </div>

        <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-5">
          {pipelineBlockCatalog.map((block) => (
            <div key={block.id} className={`rounded-lg border p-4 ${stageClass(block.stage)}`}>
              <div className="flex items-start justify-between gap-3">
                <p className="text-sm font-semibold">{block.name}</p>
                <span className="rounded-md bg-black/20 px-2 py-1 text-[10px]">{block.status}</span>
              </div>
              <p className="mt-1 text-[11px] uppercase tracking-wide opacity-80">{block.stage} / {block.backend}</p>
              <p className="mt-2 text-xs leading-5 opacity-90">{block.description}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-lg border border-border bg-surface p-5">
        <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
          <Layers size={18} className="text-accent" />
          Pipeline configuration examples
        </h2>
        <p className="mt-2 max-w-4xl text-sm leading-6 text-text-secondary">
          These are not generic RAG flows. Each configuration defines the user,
          objective, sources, ontology focus, temporal episodes, graph outputs, and
          benchmark target before any extraction happens.
        </p>
        <div className="mt-5 grid gap-4 xl:grid-cols-2">
          {pipelineConfigurationExamples.map((example) => (
            <div key={example.id} className="rounded-lg border border-border bg-background p-4">
              <div className="flex flex-col justify-between gap-3 md:flex-row md:items-start">
                <div>
                  <p className="text-sm font-semibold text-text-primary">{example.title}</p>
                  <p className="mt-1 text-xs text-accent">{example.user}</p>
                </div>
                <span className="rounded-md bg-accent/10 px-2 py-1 text-[10px] text-accent">
                  {example.benchmark}
                </span>
              </div>
              <p className="mt-3 text-xs leading-5 text-text-secondary">{example.objective}</p>
              <div className="mt-3 grid gap-3 md:grid-cols-2">
                <div>
                  <p className="text-[11px] font-semibold uppercase tracking-wide text-text-secondary">Sources</p>
                  <p className="mt-1 text-xs leading-5 text-text-primary">{example.sources.join(", ")}</p>
                </div>
                <div>
                  <p className="text-[11px] font-semibold uppercase tracking-wide text-text-secondary">Ontology focus</p>
                  <p className="mt-1 text-xs leading-5 text-text-primary">{example.ontologyFocus.join(", ")}</p>
                </div>
                <div>
                  <p className="text-[11px] font-semibold uppercase tracking-wide text-text-secondary">Episodes</p>
                  <p className="mt-1 text-xs leading-5 text-text-primary">{example.episodes.join(" -> ")}</p>
                </div>
                <div>
                  <p className="text-[11px] font-semibold uppercase tracking-wide text-text-secondary">Graph outputs</p>
                  <p className="mt-1 text-xs leading-5 text-text-primary">{example.graphOutputs.join(", ")}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-lg border border-border bg-surface p-5">
        <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
          <Brain size={18} className="text-accent" />
          Dynamic ontology and benchmark blocks
        </h2>
        <p className="mt-2 max-w-4xl text-sm leading-6 text-text-secondary">
          {dynamicOntologyEngine.shortName} creates case-specific ontology extensions
          while keeping them grounded in TACITUS core primitives. Benchmark blocks
          make each pipeline testable instead of merely impressive.
        </p>
        <div className="mt-5 grid gap-4 xl:grid-cols-[0.85fr_1.15fr]">
          <div className="rounded-lg border border-border bg-background p-4">
            <p className="text-sm font-semibold text-text-primary">{dynamicOntologyEngine.name}</p>
            <p className="mt-2 text-xs leading-5 text-text-secondary">{dynamicOntologyEngine.purpose}</p>
            <div className="mt-3 grid gap-2 md:grid-cols-2">
              {dynamicOntologyEngine.outputs.map((output) => (
                <span key={output} className="rounded-md bg-surface px-2 py-1 text-[11px] text-accent">
                  {output}
                </span>
              ))}
            </div>
          </div>
          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
            {benchmarkBlockCatalog.map((block) => (
              <div key={block.id} className="rounded-lg border border-border bg-background p-4">
                <p className="text-sm font-semibold text-text-primary">{block.name}</p>
                <p className="mt-2 text-xs leading-5 text-text-secondary">{block.metric}</p>
                <p className="mt-3 rounded-md bg-surface px-2 py-1 text-[11px] text-accent">{block.appliesTo}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <div className="rounded-lg border border-border bg-surface p-5">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
            <GitBranch size={18} className="text-accent" />
            Neurosymbolic rule blocks
          </h2>
          <p className="mt-2 text-sm leading-6 text-text-secondary">
            Rules sit between graph memory and LLM generation. They prevent the model
            from turning weak evidence, chronology, or inferred claims into confident
            prose. A rule can create review work, constrain answer wording, or propose
            a safer intervention path.
          </p>
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            {neurosymbolicRuleCatalog.map((rule) => (
              <div key={rule.id} className="rounded-lg border border-border bg-background p-4">
                <div className="flex items-start justify-between gap-3">
                  <p className="text-sm font-semibold text-text-primary">{rule.name}</p>
                  <span className="rounded-md bg-accent/10 px-2 py-1 text-[10px] text-accent">
                    {rule.category}
                  </span>
                </div>
                <p className="mt-2 text-xs leading-5 text-text-secondary">{rule.trigger}</p>
                <code className="mt-3 block rounded-md bg-surface px-2 py-2 text-[11px] leading-5 text-accent">
                  {rule.graphPattern}
                </code>
                <p className="mt-2 text-[11px] leading-5 text-text-secondary">{rule.output}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-lg border border-border bg-surface p-5">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
            <Network size={18} className="text-accent" />
            Graph layer blueprint
          </h2>
          <p className="mt-2 text-sm leading-6 text-text-secondary">
            DIALECTICA should build several graph layers, not one mixed knowledge
            graph. This keeps source evidence, situation facts, abstract methods,
            reasoning, and user activity separate but connected.
          </p>
          <div className="mt-4 space-y-3">
            {graphLayerBlueprints.map((layer) => (
              <div key={layer.layer} className="rounded-lg border border-border bg-background p-4">
                <p className="text-sm font-semibold text-text-primary">{layer.layer}</p>
                <p className="mt-2 text-xs leading-5 text-text-secondary">{layer.stores}</p>
                <p className="mt-2 rounded-md bg-surface px-2 py-1 text-[11px] leading-5 text-accent">
                  {layer.value}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="rounded-lg border border-border bg-surface p-5">
        <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
          <Sparkles size={18} className="text-accent" />
          Next sprint: pipeline configuration studio
        </h2>
        <p className="mt-2 max-w-4xl text-sm leading-6 text-text-secondary">
          For the next two days the work should concentrate on turning the console
          into a real pipeline studio: create a workspace, choose sources, generate
          Aletheia ontology, build graph layers, run agents, and benchmark outputs.
        </p>
        <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-5">
          {nextSprintPriorities.map((priority, index) => (
            <div key={priority.item} className="rounded-lg border border-border bg-background p-4">
              <div className="flex items-start justify-between gap-3">
                <p className="text-sm font-semibold text-text-primary">{index + 1}. {priority.item}</p>
              </div>
              <p className="mt-2 text-xs leading-5 text-text-secondary">{priority.why}</p>
              <p className="mt-3 rounded-md bg-accent/10 px-2 py-1 text-[11px] leading-5 text-accent">
                {priority.deliverable}
              </p>
            </div>
          ))}
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[0.8fr_1.2fr]">
        <div className="rounded-lg border border-border bg-surface p-5">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
            <Shield size={18} className="text-accent" />
            Mission mode
          </h2>
          <p className="mt-2 text-sm leading-6 text-text-secondary">
            The ontology changes with the job. A mediator, policy analyst, field
            analyst, researcher, and Praxis user need different primitives, risk
            language, and outputs.
          </p>
          <div className="mt-4 space-y-2">
            {conflictUseCases.map((useCase) => (
              <button
                key={useCase.name}
                onClick={() => setActiveUseCaseName(useCase.name)}
                className={`w-full rounded-lg border px-3 py-3 text-left transition-colors ${
                  useCase.name === activeUseCase.name
                    ? "border-accent bg-accent/10"
                    : "border-border bg-background hover:border-border-hover"
                }`}
              >
                <p className="text-sm font-semibold text-text-primary">{useCase.name}</p>
                <p className="mt-1 text-xs leading-5 text-text-secondary">{useCase.userNeed}</p>
              </button>
            ))}
          </div>
        </div>

        <div className="rounded-lg border border-border bg-surface p-5">
          <div className="grid gap-4 lg:grid-cols-2">
            <div className="rounded-lg border border-border bg-background p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-text-secondary">Ontology emphasis</p>
              <p className="mt-3 text-sm leading-6 text-text-primary">{activeUseCase.ontologyEmphasis}</p>
            </div>
            <div className="rounded-lg border border-accent/30 bg-accent/10 p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-accent">Aha moment</p>
              <p className="mt-3 text-sm leading-6 text-text-secondary">{activeUseCase.aha}</p>
            </div>
          </div>

          <h3 className="mt-5 text-sm font-semibold text-text-primary">Source pack</h3>
          <div className="mt-3 grid gap-3 lg:grid-cols-2">
            {sourcePacks.map((pack) => (
              <button
                key={pack.id}
                onClick={() => {
                  setActiveSourcePackId(pack.id);
                  setWorkspaceId(pack.id);
                }}
                className={`rounded-lg border px-3 py-3 text-left transition-colors ${
                  pack.id === activeSourcePack.id
                    ? "border-accent bg-accent/10"
                    : "border-border bg-background hover:border-border-hover"
                }`}
              >
                <p className="text-sm font-semibold text-text-primary">{pack.name}</p>
                <p className="mt-1 text-xs text-accent">{pack.profile}</p>
                <p className="mt-2 text-xs leading-5 text-text-secondary">{pack.why}</p>
              </button>
            ))}
          </div>
          <div className="mt-4 rounded-lg border border-border bg-background p-4">
            <p className="text-xs font-semibold uppercase tracking-wide text-text-secondary">Selected sources</p>
            <p className="mt-2 text-sm text-text-primary">{activeSourcePack.sources}</p>
            <p className="mt-2 text-xs text-text-secondary">Recommended run: {activeSourcePack.nextRun}</p>
          </div>
        </div>
      </section>

      <section className="rounded-lg border border-border bg-surface p-5">
        <div className="flex flex-col justify-between gap-4 xl:flex-row xl:items-start">
          <div>
            <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
              <Upload size={18} className="text-accent" />
              Ingest, structure, and build graph memory
            </h2>
            <p className="mt-2 max-w-4xl text-sm leading-6 text-text-secondary">
              Choose a need, select the ontology profile, upload TXT/PDF or paste
              text, then preview TACITUS primitives with source spans. If Neo4j
              secrets are configured, the same action can persist the case into the
              graph so users keep expanding it with new books and documents.
            </p>
          </div>
          <div className="rounded-lg border border-border bg-background px-4 py-3 text-xs leading-5 text-text-secondary xl:max-w-md">
            Current write mode: {writeGraph ? "attempt Neo4j write" : "preview only"}.
            {sendToDatabricks ? " Source staging to Databricks is enabled." : " Enable Databricks staging to send upload metadata to the lakehouse."}
          </div>
        </div>

        <div className="mt-5 grid gap-6 xl:grid-cols-[340px_minmax(0,1fr)]">
          <div className="space-y-3">
            {precompiledNeeds.map((need) => (
              <button
                key={need.id}
                onClick={() => applyNeed(need.id)}
                className={`w-full rounded-lg border px-3 py-3 text-left transition-colors ${
                  activeNeed.id === need.id
                    ? "border-accent bg-accent/10"
                    : "border-border bg-background hover:border-border-hover"
                }`}
              >
                <p className="text-sm font-semibold text-text-primary">{need.label}</p>
                <p className="mt-1 text-xs leading-5 text-text-secondary">{need.objective}</p>
                <p className="mt-2 text-[11px] text-accent">{need.defaultQuestion}</p>
              </button>
            ))}
          </div>

          <div className="space-y-4">
            <div className="grid gap-3 md:grid-cols-3">
              <label className="block">
                <span className="text-xs font-medium uppercase tracking-wide text-text-secondary">Workspace</span>
                <input value={workspaceId} onChange={(event) => setWorkspaceId(event.target.value)} className="input-base mt-2 w-full" />
              </label>
              <label className="block">
                <span className="text-xs font-medium uppercase tracking-wide text-text-secondary">Case</span>
                <input value={caseId} onChange={(event) => setCaseId(event.target.value)} className="input-base mt-2 w-full" />
              </label>
              <label className="block">
                <span className="text-xs font-medium uppercase tracking-wide text-text-secondary">Ontology</span>
                <select value={activeProfileId} onChange={(event) => setActiveProfileId(event.target.value)} className="input-base mt-2 w-full">
                  {ontologyProfileOptions.map((profile) => (
                    <option key={profile.id} value={profile.id}>{profile.label}</option>
                  ))}
                </select>
              </label>
            </div>

            <label className="block">
              <span className="text-xs font-medium uppercase tracking-wide text-text-secondary">Objective</span>
              <textarea value={objective} onChange={(event) => setObjective(event.target.value)} className="input-base mt-2 min-h-[80px] w-full" />
            </label>

            <label className="block">
              <span className="text-xs font-medium uppercase tracking-wide text-text-secondary">Paste text</span>
              <textarea
                value={sourceText}
                onChange={(event) => setSourceText(event.target.value)}
                placeholder="Paste a book passage, mediation notes, policy memo, transcript, or field report..."
                className="input-base mt-2 min-h-[140px] w-full"
              />
            </label>

            <div className="flex flex-wrap items-center gap-3">
              <button onClick={() => runIngest(false)} className="btn-primary inline-flex items-center gap-2">
                <Play size={15} />
                Structure pasted text
              </button>
              <button onClick={() => runIngest(true)} className="btn-secondary inline-flex items-center gap-2">
                Run selected sample
                <Sparkles size={15} />
              </button>
              <label className="btn-secondary inline-flex cursor-pointer items-center gap-2">
                Upload TXT/PDF
                <Upload size={15} />
                <input
                  type="file"
                  accept=".txt,.pdf,text/plain,application/pdf"
                  className="hidden"
                  onChange={(event) => runFileIngest(event.target.files?.[0] ?? null)}
                />
              </label>
              <label className="inline-flex items-center gap-2 text-xs text-text-secondary">
                <input
                  type="checkbox"
                  checked={writeGraph}
                  onChange={(event) => setWriteGraph(event.target.checked)}
                />
                Write to Neo4j when configured
              </label>
              <label className="inline-flex items-center gap-2 text-xs text-text-secondary">
                <input
                  type="checkbox"
                  checked={sendToDatabricks}
                  onChange={(event) => setSendToDatabricks(event.target.checked)}
                />
                Stage source JSON to Databricks
              </label>
              <label className="inline-flex items-center gap-2 text-xs text-text-secondary">
                <input
                  type="checkbox"
                  checked={triggerWorkflowAfterIngest}
                  onChange={(event) => setTriggerWorkflowAfterIngest(event.target.checked)}
                />
                Trigger workflow after ingest
              </label>
              <select
                value={databricksWorkflowKey}
                onChange={(event) => setDatabricksWorkflowKey(event.target.value)}
                className="input-base min-w-[220px]"
                disabled={!triggerWorkflowAfterIngest}
              >
                {workflowOptions.map((job) => (
                  <option key={job.jobId} value={job.actionKey}>
                    {job.name}
                  </option>
                ))}
              </select>
            </div>

            {ingestState.status === "loading" && (
              <div className="rounded-lg border border-accent/30 bg-accent/10 p-3 text-sm text-accent">
                Structuring document into TACITUS primitives...
              </div>
            )}
            {ingestState.status === "error" && (
              <div className="rounded-lg border border-warning/30 bg-warning/10 p-3 text-sm text-warning">
                {ingestState.message}
              </div>
            )}
            {ingestState.status === "ok" && (
              <div className="grid gap-4 xl:grid-cols-[0.8fr_1.2fr]">
                <div className="rounded-lg border border-border bg-background p-4">
                  <p className="text-sm font-semibold text-text-primary">Extraction result</p>
                  <p className="mt-2 text-xs text-text-secondary">
                    run {String(ingestState.result.extractionRunId)}
                  </p>
                  <p className="mt-2 text-xs text-accent">
                    {String((ingestState.result.graphWrite as { message?: string })?.message ?? "")}
                  </p>
                  {Boolean(ingestState.result.databricks) && (
                    <pre className="mt-3 max-h-[180px] overflow-auto rounded-md bg-surface p-3 text-[11px] leading-5 text-text-secondary">
                      <code>{JSON.stringify(ingestState.result.databricks, null, 2) ?? ""}</code>
                    </pre>
                  )}
                  <div className="mt-3 grid grid-cols-2 gap-2">
                    {Object.entries((ingestState.result.counts as Record<string, number>) ?? {}).map(([key, value]) => (
                      <div key={key} className="rounded-md bg-surface px-2 py-2">
                        <p className="text-[11px] text-text-secondary">{key}</p>
                        <p className="text-lg font-semibold text-text-primary">{value}</p>
                      </div>
                    ))}
                  </div>
                </div>
                <pre className="max-h-[360px] overflow-auto rounded-lg border border-border bg-background p-4 text-xs leading-5 text-text-secondary">
                  <code>{JSON.stringify((ingestState.result.primitives as unknown[]).slice(0, 10), null, 2)}</code>
                </pre>
              </div>
            )}
          </div>
        </div>

        <div className="mt-5 grid gap-3 md:grid-cols-3 xl:grid-cols-6">
          {ingestionTreeTemplate.map((item) => (
            <div key={item.level} className="rounded-lg border border-border bg-background p-4">
              <p className="text-sm font-semibold text-text-primary">{item.level}</p>
              <p className="mt-2 text-[11px] text-accent">{item.output}</p>
              <p className="mt-2 text-xs leading-5 text-text-secondary">{item.purpose}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-lg border border-border bg-surface p-5">
        <div className="mb-5 flex items-center justify-between gap-4">
          <div>
            <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
              <Workflow size={18} className="text-accent" />
              Ingestion to intelligence pipeline
            </h2>
            <p className="mt-1 text-sm text-text-secondary">
              The Databricks job is intentionally low-cost and manual-first; KGE/link
              prediction stays in a separate manual job.
            </p>
          </div>
          <Link href="/admin/graph" className="btn-secondary inline-flex items-center gap-2 text-xs">
            Graph Explorer
            <ArrowRight size={14} />
          </Link>
          <a
            href={databricksJobsUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-secondary inline-flex items-center gap-2 text-xs"
          >
            Databricks Jobs
            <ArrowRight size={14} />
          </a>
        </div>

        <div className="grid gap-3 lg:grid-cols-5">
          {graphOpsPipeline.map((step, index) => (
            <div key={step.name} className="relative rounded-lg border border-border bg-background p-4">
              <div className="mb-3 flex h-8 w-8 items-center justify-center rounded-md bg-accent/10 text-accent">
                {index + 1}
              </div>
              <p className="text-sm font-semibold text-text-primary">{step.name}</p>
              <p className="mt-2 text-xs leading-5 text-text-secondary">{step.detail}</p>
              <p className="mt-3 rounded-md bg-surface px-2 py-1 text-[11px] text-accent">{step.output}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-lg border border-border bg-surface p-5">
        <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
          <Layers size={18} className="text-accent" />
          Dynamic Ontology Intelligence
        </h2>
        <p className="mt-2 max-w-4xl text-sm leading-6 text-text-secondary">
          DIALECTICA now treats ontology as profile-driven. A literary conflict,
          workplace friction episode, political policy dispute, and mediation case
          share a stable core, but each profile emphasizes different expert concepts:
          source trust, temporal phase, claims needing verification, actors in a
          location, norms, interests, and process options.
        </p>
        <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          {dynamicOntologyTables.map((item) => (
            <div key={item.table} className="rounded-lg border border-border bg-background p-4">
              <code className="text-xs text-accent">{item.table}</code>
              <p className="mt-2 text-xs leading-5 text-text-secondary">{item.purpose}</p>
            </div>
          ))}
        </div>
        <div className="mt-5 rounded-lg border border-border bg-background p-4">
          <p className="text-sm font-semibold text-text-primary">Claim lifecycle</p>
          <div className="mt-3 grid gap-2 md:grid-cols-6">
            {["candidate", "extracted", "graph_validated", "human_verified", "rejected", "superseded"].map((state) => (
              <div key={state} className="rounded-md bg-surface px-3 py-2 text-center text-xs text-text-secondary">
                {state}
              </div>
            ))}
          </div>
          <p className="mt-3 text-xs leading-5 text-text-secondary">
            LLMs can propose facts, but TACITUS stores whether a fact is explicit,
            inferred, user-asserted, trusted-source-backed, sketchy, verified, or
            rejected. That distinction is what makes the system useful for experts.
          </p>
        </div>
      </section>

      <section className="rounded-lg border border-border bg-surface p-5">
        <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
          <Workflow size={18} className="text-accent" />
          Situation Portal Blueprint
        </h2>
        <p className="mt-2 max-w-4xl text-sm leading-6 text-text-secondary">
          This is the product shape: each situation becomes a portal where sources,
          users, projects, ontology candidates, Neo4j graph structure, Databricks
          quality signals, and benchmarked answers are visible in one place.
        </p>
        <div className="mt-5 overflow-x-auto">
          <table className="w-full min-w-[900px] border-collapse text-left text-xs">
            <thead>
              <tr className="border-b border-border text-text-secondary">
                <th className="px-3 py-2 font-semibold">Stage</th>
                <th className="px-3 py-2 font-semibold">Operator View</th>
                <th className="px-3 py-2 font-semibold">Neo4j Graph View</th>
                <th className="px-3 py-2 font-semibold">Databricks View</th>
              </tr>
            </thead>
            <tbody>
              {situationPortalBlueprint.map((row) => (
                <tr key={row.stage} className="border-b border-border/70">
                  <td className="px-3 py-3 font-semibold text-accent">{row.stage}</td>
                  <td className="px-3 py-3 leading-5 text-text-secondary">{row.operatorView}</td>
                  <td className="px-3 py-3 leading-5 text-text-secondary">{row.graphView}</td>
                  <td className="px-3 py-3 leading-5 text-text-secondary">{row.databricksView}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="mt-5 grid gap-3 md:grid-cols-4">
          {ambitionRoadmap.map((item) => (
            <div key={item.horizon} className="rounded-lg border border-border bg-background p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-accent">{item.horizon}</p>
              <p className="mt-2 text-sm font-semibold text-text-primary">{item.goal}</p>
              <p className="mt-2 text-xs leading-5 text-text-secondary">{item.proof}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-lg border border-border bg-surface p-5">
        <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
          <div>
            <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
              <Brain size={18} className="text-accent" />
              Answer Quality Lab
            </h2>
            <p className="mt-1 max-w-3xl text-sm text-text-secondary">
              Compare a traditional LLM answer against a DIALECTICA graph-grounded
              answer. The product goal is to make quality measurable: provenance,
              causal precision, typed graph overlap, and ambiguity handling.
            </p>
          </div>
          <button
            onClick={() => runDatabricksJob("benchmark")}
            className="btn-primary inline-flex items-center justify-center gap-2"
          >
            Run Databricks Benchmark
            <Play size={15} />
          </button>
        </div>

        <div className="mt-5 grid gap-4 lg:grid-cols-[280px_minmax(0,1fr)]">
          <div className="space-y-2">
            {benchmarkScenarios.map((scenario) => (
              <button
                key={scenario.id}
                onClick={() => setActiveScenarioId(scenario.id)}
                className={`w-full rounded-lg border px-3 py-3 text-left transition-colors ${
                  scenario.id === activeScenario.id
                    ? "border-accent bg-accent/10"
                    : "border-border bg-background hover:border-border-hover"
                }`}
              >
                <p className="text-sm font-semibold text-text-primary">{scenario.title}</p>
                <p className="mt-1 text-xs text-text-secondary">{scenario.domain}</p>
              </button>
            ))}
          </div>

          <div className="space-y-4">
            <div className="rounded-lg border border-border bg-background p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-text-secondary">Question</p>
              <p className="mt-2 text-sm text-text-primary">{activeScenario.question}</p>
              <p className="mt-3 text-xs leading-5 text-text-secondary">{activeScenario.input}</p>
            </div>

            <div className="grid gap-4 xl:grid-cols-2">
              <div className="rounded-lg border border-warning/30 bg-warning/10 p-4">
                <p className="text-sm font-semibold text-warning">Traditional LLM</p>
                <p className="mt-3 text-xs leading-5 text-text-secondary">{activeScenario.baselineAnswer}</p>
              </div>
              <div className="rounded-lg border border-accent/30 bg-accent/10 p-4">
                <p className="text-sm font-semibold text-accent">DIALECTICA Graph-Grounded</p>
                <p className="mt-3 text-xs leading-5 text-text-secondary">{activeScenario.dialecticaAnswer}</p>
              </div>
            </div>

            <div className="grid gap-3 md:grid-cols-4">
              {Object.entries(activeScenario.scores.dialectica).map(([metric, dialecticaScore]) => {
                const baselineScore =
                  activeScenario.scores.baseline[metric as keyof typeof activeScenario.scores.baseline];
                return (
                  <div key={metric} className="rounded-lg border border-border bg-background p-3">
                    <p className="text-xs font-semibold capitalize text-text-primary">{metric}</p>
                    <div className="mt-3 space-y-2">
                      <div>
                        <div className="flex justify-between text-[11px] text-text-secondary">
                          <span>LLM</span>
                          <span>{Math.round(baselineScore * 100)}%</span>
                        </div>
                        <div className="mt-1 h-1.5 rounded-full bg-surface">
                          <div className="h-1.5 rounded-full bg-warning" style={{ width: `${baselineScore * 100}%` }} />
                        </div>
                      </div>
                      <div>
                        <div className="flex justify-between text-[11px] text-text-secondary">
                          <span>DIALECTICA</span>
                          <span>{Math.round(dialecticaScore * 100)}%</span>
                        </div>
                        <div className="mt-1 h-1.5 rounded-full bg-surface">
                          <div className="h-1.5 rounded-full bg-accent" style={{ width: `${dialecticaScore * 100}%` }} />
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </section>

      <section className="rounded-lg border border-border bg-surface p-5">
        <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
          <div>
            <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
              <Database size={18} className="text-accent" />
              Live Databricks workspace
            </h2>
            <p className="mt-1 max-w-3xl text-sm text-text-secondary">
              These jobs are deployed in the Databricks workspace. The first demo has
              already run successfully and created Delta tables in
              <code className="mx-1 text-accent">dialectica.conflict_graphs</code>.
            </p>
          </div>
          <a
            href={databricksJobsUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-secondary inline-flex items-center justify-center gap-2"
          >
            Workflows
            <ArrowRight size={15} />
          </a>
          <button onClick={refreshDatabricksJobs} className="btn-secondary inline-flex items-center justify-center gap-2">
            Refresh
            <Activity size={15} />
          </button>
        </div>

        {databricksState.status === "ready" && databricksState.message && (
          <div className="mt-4 rounded-lg border border-warning/30 bg-warning/10 p-3 text-sm text-warning">
            {databricksState.message}
          </div>
        )}
        {databricksState.status === "error" && (
          <div className="mt-4 rounded-lg border border-warning/30 bg-warning/10 p-3 text-sm text-warning">
            {databricksState.message}
          </div>
        )}

        <div className="mt-5 grid gap-3 lg:grid-cols-6">
          {(tableState.status === "ready" ? tableState.tables : liveDeltaTables).map((table) => (
            <div key={table.table} className="rounded-lg border border-border bg-background p-3">
              <code className="text-[11px] text-accent">{table.table}</code>
              <p className="mt-2 text-2xl font-bold text-text-primary">{table.rows.toLocaleString()}</p>
              <p className="mt-1 text-[11px] leading-5 text-text-secondary">{table.role}</p>
            </div>
          ))}
        </div>
        {tableState.status === "ready" && tableState.message && (
          <p className="mt-2 text-xs text-warning">{tableState.message}</p>
        )}
        {tableState.status === "error" && (
          <p className="mt-2 text-xs text-warning">{tableState.message}</p>
        )}

        <div className="mt-5 grid gap-3 lg:grid-cols-4">
          {(databricksState.status === "ready" ? databricksState.jobs : databricksJobs).map((job) => (
            <div key={job.jobId} className="rounded-lg border border-border bg-background p-4">
              <div className="flex items-start justify-between gap-3">
                <p className="text-sm font-semibold text-text-primary">{job.name}</p>
                <span className="rounded-md bg-accent/10 px-2 py-1 text-[10px] text-accent">
                  {job.status}
                </span>
              </div>
              <p className="mt-2 font-mono text-[11px] text-text-secondary">job {job.jobId}</p>
              <p className="mt-3 text-xs leading-5 text-text-secondary">{job.purpose}</p>
              <p className="mt-3 rounded-md bg-surface px-2 py-1 text-[11px] leading-5 text-text-secondary">
                {job.output}
              </p>
              {"recentRuns" in job && Array.isArray(job.recentRuns) && job.recentRuns.length > 0 && (
                <p className="mt-3 text-[11px] text-success">
                  latest run: {String((job.recentRuns[0] as { state?: { result_state?: string } }).state?.result_state ?? "running")}
                </p>
              )}
              {job.actionKey && (
                <button
                  onClick={() => runDatabricksJob(job.actionKey)}
                  className="btn-ghost mt-3 w-full border border-border text-xs"
                >
                  Run workflow
                </button>
              )}
              {"runUrl" in job && typeof job.runUrl === "string" && (
                <a
                  href={job.runUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-2 inline-flex w-full items-center justify-center gap-2 rounded-md border border-border px-3 py-2 text-xs text-text-secondary hover:text-accent"
                >
                  Open latest run
                  <ArrowRight size={13} />
                </a>
              )}
            </div>
          ))}
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
        <div className="rounded-lg border border-border bg-surface p-5">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
            <CheckCircle2 size={18} className="text-accent" />
            Quality gates and review work
          </h2>
          <p className="mt-2 text-sm leading-6 text-text-secondary">
            A neurosymbolic system is only useful if uncertainty becomes visible work.
            These gates turn LLM output into accepted graph facts, rejected claims, or
            review tasks instead of hiding uncertainty in fluent prose.
          </p>
          <div className="mt-4 space-y-3">
            {qualityGates.map((gate) => (
              <div key={gate.gate} className="rounded-lg border border-border bg-background p-4">
                <div className="flex items-start justify-between gap-3">
                  <p className="text-sm font-semibold text-text-primary">{gate.gate}</p>
                  <span className="rounded-md bg-warning/10 px-2 py-1 text-[10px] text-warning">reviewable</span>
                </div>
                <p className="mt-2 text-xs leading-5 text-text-secondary">{gate.check}</p>
                <p className="mt-2 rounded-md bg-surface px-2 py-1 text-[11px] leading-5 text-accent">
                  {gate.failureAction}
                </p>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-lg border border-border bg-surface p-5">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
            <Workflow size={18} className="text-accent" />
            Event-driven control plane
          </h2>
          <p className="mt-2 text-sm leading-6 text-text-secondary">
            In production this becomes a Pub/Sub-style backbone: the frontend emits
            intent, Databricks runs repeatable jobs, Neo4j graph versions change, and
            TACITUS products consume updated situation memory.
          </p>
          <div className="mt-4 space-y-3">
            {orchestrationEvents.map((event) => (
              <div key={event.event} className="rounded-lg border border-border bg-background p-4">
                <code className="text-xs text-accent">{event.event}</code>
                <p className="mt-2 text-xs leading-5 text-text-secondary">{event.payload}</p>
                <p className="mt-2 text-[11px] text-text-primary">Consumer: {event.consumer}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="grid gap-4 lg:grid-cols-5">
        {layerCards.map((layer) => (
          <div key={layer.name} className="rounded-lg border border-border bg-surface p-4">
            <layer.icon size={18} className="text-accent" />
            <p className="mt-3 text-sm font-semibold text-text-primary">{layer.name}</p>
            <p className="mt-2 text-xs leading-5 text-text-secondary">{layer.detail}</p>
          </div>
        ))}
      </section>

      <section className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
        <div className="rounded-lg border border-border bg-surface p-5">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
            <Network size={18} className="text-accent" />
            Graph Categories
          </h2>
          <p className="mt-2 text-sm leading-6 text-text-secondary">
            A production situation portal needs several graph layers. These categories
            keep user identity, provenance, situation facts, temporal reasoning, and
            inferred claims separate but connected.
          </p>
          <div className="mt-4 space-y-3">
            {graphCategories.map((item) => (
              <div key={item.category} className="rounded-lg border border-border bg-background p-4">
                <div className="flex items-center justify-between gap-3">
                  <p className="text-sm font-semibold text-text-primary">{item.category}</p>
                  <span className="rounded-md bg-surface px-2 py-1 text-[11px] text-accent">
                    {item.nodes.length} labels
                  </span>
                </div>
                <p className="mt-2 text-xs leading-5 text-text-secondary">{item.question}</p>
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {item.nodes.map((node) => (
                    <span key={node} className="badge bg-accent/10 text-accent">
                      {node}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-lg border border-border bg-surface p-5">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
            <Layers size={18} className="text-accent" />
            Ontology Profile Generator
          </h2>
          <p className="mt-2 text-sm leading-6 text-text-secondary">
            The ontology should change with the user objective. Select a profile to see
            which graph categories, relationships, and expert questions TACITUS should
            prioritize before extraction and benchmarking.
          </p>
          <div className="mt-4 grid gap-2 sm:grid-cols-2">
            {ontologyProfileOptions.map((profile) => (
              <button
                key={profile.id}
                onClick={() => setActiveProfileId(profile.id)}
                className={`rounded-lg border px-3 py-3 text-left transition-colors ${
                  profile.id === activeProfile.id
                    ? "border-accent bg-accent/10"
                    : "border-border bg-background hover:border-border-hover"
                }`}
              >
                <p className="text-sm font-semibold text-text-primary">{profile.label}</p>
                <p className="mt-1 text-xs leading-5 text-text-secondary">{profile.objective}</p>
              </button>
            ))}
          </div>

          <div className="mt-5 grid gap-4 lg:grid-cols-2">
            <div className="rounded-lg border border-border bg-background p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-text-secondary">Required Nodes</p>
              <div className="mt-3 flex flex-wrap gap-1.5">
                {activeProfile.requiredNodes.map((node) => (
                  <span key={node} className="badge bg-accent/10 text-accent">{node}</span>
                ))}
              </div>
            </div>
            <div className="rounded-lg border border-border bg-background p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-text-secondary">Required Edges</p>
              <div className="mt-3 flex flex-wrap gap-1.5">
                {activeProfile.requiredEdges.map((edge) => (
                  <span key={edge} className="badge bg-surface text-text-secondary">{edge}</span>
                ))}
              </div>
            </div>
          </div>
          <div className="mt-4 rounded-lg border border-border bg-background p-4">
            <p className="text-xs font-semibold uppercase tracking-wide text-text-secondary">Questions this profile should answer</p>
            <div className="mt-3 space-y-2">
              {activeProfile.questions.map((question) => (
                <p key={question} className="rounded-md bg-surface px-3 py-2 text-xs text-text-secondary">
                  {question}
                </p>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
        <div className="rounded-lg border border-border bg-surface p-5">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
            <GitBranch size={18} className="text-accent" />
            Ontology contract by layer
          </h2>
          <p className="mt-2 text-sm leading-6 text-text-secondary">
            The core extractor is intentionally small and stable. Dynamic profiles,
            reasoning traces, claims, and product-specific concepts extend that core
            without pretending every label is equally live today.
          </p>
          <div className="mt-4 space-y-3">
            {ontologyContracts.map((contract) => (
              <div key={contract.tier} className="rounded-lg border border-border bg-background p-4">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <p className="text-sm font-semibold text-text-primary">{contract.tier}</p>
                  <span className="rounded-md bg-surface px-2 py-1 text-[10px] text-accent">
                    {contract.status}
                  </span>
                </div>
                <p className="mt-2 text-xs leading-5 text-text-secondary">Labels: {contract.labels}</p>
                <p className="mt-2 text-xs leading-5 text-text-secondary">Relationships: {contract.relationships}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-lg border border-border bg-surface p-5">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
            <Database size={18} className="text-accent" />
            Neo4j operational readiness
          </h2>
          <p className="mt-2 text-sm leading-6 text-text-secondary">
            Neo4j is the live graph memory. The app is wired for allowlisted queries
            and Databricks writeback, but production credentials should be rotated
            before enabling live graph writes from the previously exposed secret set.
          </p>
          <div className="mt-4 space-y-3">
            {neo4jStatus.map((item) => (
              <div key={item.item} className="rounded-lg border border-border bg-background p-4">
                <div className="flex items-center justify-between gap-3">
                  <p className="text-sm font-semibold text-text-primary">{item.item}</p>
                  <span className="rounded-md bg-accent/10 px-2 py-1 text-[10px] text-accent">
                    {item.state}
                  </span>
                </div>
                <p className="mt-2 text-xs leading-5 text-text-secondary">{item.detail}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="rounded-lg border border-border bg-surface p-5">
        <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
          <Workflow size={18} className="text-accent" />
          Agentic Toolchain
        </h2>
        <p className="mt-2 max-w-4xl text-sm leading-6 text-text-secondary">
          These are the embeddable TACITUS tools that can power Praxis or other
          products: source ingestion, ontology generation, claim verification,
          temporal analysis, graph search, and benchmark judging.
        </p>
        <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {agenticTools.map((tool) => (
            <div key={tool.name} className="rounded-lg border border-border bg-background p-4">
              <div className="flex items-center justify-between gap-3">
                <p className="text-sm font-semibold text-text-primary">{tool.name}</p>
                <span className="rounded-md bg-accent/10 px-2 py-1 text-[10px] text-accent">
                  {tool.runSurface}
                </span>
              </div>
              <p className="mt-3 text-xs leading-5 text-text-secondary">{tool.purpose}</p>
              <div className="mt-3 grid grid-cols-2 gap-2">
                <button
                  onClick={() => runAgent(tool.name, false)}
                  className="rounded-md border border-border px-2 py-2 text-xs text-text-secondary hover:text-accent"
                >
                  Plan
                </button>
                <button
                  onClick={() => runAgent(tool.name, true)}
                  className="rounded-md border border-border px-2 py-2 text-xs text-text-secondary hover:text-accent"
                >
                  Spawn
                </button>
              </div>
            </div>
          ))}
        </div>
        {agentRunState.status === "loading" && (
          <div className="mt-4 rounded-lg border border-accent/30 bg-accent/10 p-3 text-sm text-accent">
            Preparing {agentRunState.agent}...
          </div>
        )}
        {agentRunState.status === "error" && (
          <div className="mt-4 rounded-lg border border-warning/30 bg-warning/10 p-3 text-sm text-warning">
            {agentRunState.message}
          </div>
        )}
        {agentRunState.status === "ok" && (
          <pre className="mt-4 max-h-[320px] overflow-auto rounded-lg border border-border bg-background p-4 text-xs leading-5 text-text-secondary">
            <code>{JSON.stringify(agentRunState.result, null, 2)}</code>
          </pre>
        )}
      </section>

      <section className="rounded-lg border border-border bg-surface p-5">
        <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
          <BookOpen size={18} className="text-accent" />
          Operator deliverables
        </h2>
        <p className="mt-2 max-w-4xl text-sm leading-6 text-text-secondary">
          These are the products a civilian analyst, mediator, policy team, or
          intelligence user should get from the same graph backbone. Each output is
          tied to graph primitives so answers remain auditable and repeatable.
        </p>
        <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          {operatorDeliverables.map((item) => (
            <div key={item.name} className="rounded-lg border border-border bg-background p-4">
              <p className="text-sm font-semibold text-text-primary">{item.name}</p>
              <p className="mt-2 text-xs leading-5 text-text-secondary">{item.description}</p>
              <p className="mt-3 rounded-md bg-surface px-2 py-1 text-[11px] leading-5 text-accent">
                {item.graphBasis}
              </p>
            </div>
          ))}
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
        <div className="rounded-lg border border-border bg-surface p-5">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
            <Sparkles size={18} className="text-accent" />
            Why ontology grounding matters
          </h2>
          <p className="mt-2 text-sm leading-6 text-text-secondary">
            The product thesis is testable: ontology-grounded generation should reduce
            unsupported claims, improve retrieval precision, and make conflict answers
            easier to verify. The site now names the research claim and ties it to
            repeatable Databricks benchmarks.
          </p>
          <div className="mt-4 space-y-3">
            {researchSignals.map((signal) => (
              <a
                key={signal.claim}
                href={signal.url}
                target="_blank"
                rel="noopener noreferrer"
                className="block rounded-lg border border-border bg-background p-4 transition-colors hover:border-border-hover"
              >
                <p className="text-sm font-semibold text-text-primary">{signal.claim}</p>
                <p className="mt-2 text-xs leading-5 text-text-secondary">{signal.evidence}</p>
                <p className="mt-2 text-[11px] text-accent">{signal.source}</p>
              </a>
            ))}
          </div>
        </div>

        <div className="rounded-lg border border-border bg-surface p-5">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
            <Package size={18} className="text-accent" />
            Embeddable TACITUS services
          </h2>
          <p className="mt-2 text-sm leading-6 text-text-secondary">
            DIALECTICA should not be trapped in this app. It should expose a reusable
            graph-memory contract that Praxis, policy tools, mediation tools, and
            benchmark labs can call.
          </p>
          <Link
            href="/api/graphops/manifest"
            className="mt-4 inline-flex items-center gap-2 rounded-md border border-border px-3 py-2 text-xs text-text-secondary hover:text-accent"
          >
            Open GraphOps manifest
            <ArrowRight size={13} />
          </Link>
          <div className="mt-4 space-y-3">
            {embeddableSurfaces.map((surface) => (
              <div key={surface.product} className="rounded-lg border border-border bg-background p-4">
                <div className="flex items-center justify-between gap-3">
                  <p className="text-sm font-semibold text-text-primary">{surface.product}</p>
                  <span className="rounded-md bg-accent/10 px-2 py-1 text-[10px] text-accent">
                    {surface.capability}
                  </span>
                </div>
                <p className="mt-3 text-xs leading-5 text-text-secondary">{surface.contract}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="rounded-lg border border-border bg-surface p-5">
        <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
          <Sparkles size={18} className="text-accent" />
          What we are doing and why
        </h2>
        <p className="mt-2 max-w-4xl text-sm leading-6 text-text-secondary">
          TACITUS needs DIALECTICA to become the shared analytical backbone for
          conflict and human-friction reasoning. The experiment here is simple:
          take messy open text, force it through the TACITUS ontology, store the
          result as a Neo4j graph, use Databricks to inspect and improve that graph,
          then test whether graph-grounded answers beat ordinary LLM answers on hard
          conflict questions.
        </p>

        <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          {databricksNeo4jExplanation.map((item) => (
            <div key={item.title} className="rounded-lg border border-border bg-background p-4">
              <p className="text-sm font-semibold text-text-primary">{item.title}</p>
              <p className="mt-2 text-xs leading-5 text-text-secondary">{item.detail}</p>
            </div>
          ))}
        </div>

        <div className="mt-5 grid gap-3 lg:grid-cols-4">
          {ahaWorkflows.map((workflow) => (
            <div key={workflow.name} className="rounded-lg border border-border bg-background p-4">
              <p className="text-sm font-semibold text-text-primary">{workflow.name}</p>
              <p className="mt-2 text-xs leading-5 text-text-secondary">{workflow.steps}</p>
              <p className="mt-3 rounded-md bg-accent/10 px-2 py-1 text-[11px] leading-5 text-accent">
                {workflow.value}
              </p>
            </div>
          ))}
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
        <div className="rounded-lg border border-border bg-surface p-5">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
            <KeyRound size={18} className="text-accent" />
            Read-only Neo4j query tester
          </h2>
          <p className="mt-1 text-sm text-text-secondary">
            These are allowlisted Cypher patterns for the protected console. They
            should run only server-side against Neo4j credentials stored in environment
            variables.
          </p>

          <label className="mt-5 block text-xs font-medium uppercase tracking-wide text-text-secondary">
            Workspace
          </label>
          <input
            value={workspaceId}
            onChange={(event) => setWorkspaceId(event.target.value)}
            className="input-base mt-2 w-full"
            placeholder="books-romeo-juliet"
          />

          <div className="mt-4 space-y-2">
            {sampleCypherQueries.map((item) => (
              <button
                key={item.title}
                onClick={() => setActiveQuery(item.title)}
                className={`w-full rounded-lg border px-3 py-2 text-left transition-colors ${
                  item.title === activeQuery
                    ? "border-accent bg-accent/10 text-text-primary"
                    : "border-border bg-background text-text-secondary hover:border-border-hover"
                }`}
              >
                <p className="text-sm font-medium">{item.title}</p>
                <p className="mt-1 text-xs">{item.prompt}</p>
              </button>
            ))}
          </div>

          <button onClick={runQuery} className="btn-primary mt-4 inline-flex w-full items-center justify-center gap-2">
            <Play size={15} />
            Run Query
          </button>
        </div>

        <div className="rounded-lg border border-border bg-surface p-5">
          <div className="mb-3 flex items-center justify-between">
            <h3 className="text-sm font-semibold text-text-primary">{query.title}</h3>
            <span className="rounded-md bg-accent/10 px-2 py-1 text-[11px] text-accent">Cypher</span>
          </div>
          <pre className="min-h-[160px] overflow-x-auto rounded-lg border border-border bg-background p-4 text-xs leading-5 text-text-secondary">
            <code>{queryState.status === "ok" || queryState.status === "error" ? queryState.cypher : query.cypher}</code>
          </pre>

          <div className="mt-4 rounded-lg border border-border bg-background p-4">
            {queryState.status === "idle" && (
              <p className="text-sm text-text-secondary">
                Run an allowlisted query after Neo4j environment variables are configured.
              </p>
            )}
            {queryState.status === "loading" && (
              <p className="text-sm text-accent">Querying Neo4j...</p>
            )}
            {queryState.status === "error" && (
              <div>
                <p className="text-sm font-medium text-warning">Query not available yet</p>
                <p className="mt-1 text-xs leading-5 text-text-secondary">{queryState.message}</p>
              </div>
            )}
            {queryState.status === "ok" && (
              <pre className="max-h-[260px] overflow-auto text-xs leading-5 text-text-secondary">
                <code>{JSON.stringify(queryState.records, null, 2)}</code>
              </pre>
            )}
          </div>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
        <div className="rounded-lg border border-border bg-surface p-5">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
            <Layers size={18} className="text-accent" />
            TACITUS conflict ontology
          </h2>
          <div className="mt-4 grid gap-3 md:grid-cols-3">
            {ontologyTiers.map((tier) => (
              <div key={tier.name} className="rounded-lg border border-border bg-background p-4">
                <div className="flex items-center gap-2">
                  <span className="h-3 w-3 rounded-full" style={{ backgroundColor: tier.color }} />
                  <p className="text-sm font-semibold text-text-primary">{tier.name}</p>
                </div>
                <p className="mt-2 text-xs text-text-secondary">{tier.description}</p>
                <p className="mt-3 font-mono text-xs text-accent">
                  {tier.nodes} nodes / {tier.edges} edges
                </p>
              </div>
            ))}
          </div>

          <div className="mt-5 grid gap-2 md:grid-cols-2">
            {ontologyNodes.map((node) => (
              <div key={node.label} className="rounded-lg border border-border bg-background p-3">
                <div className="flex items-center justify-between gap-3">
                  <p className="text-sm font-medium text-text-primary">{node.label}</p>
                  <span className="rounded-md bg-surface px-2 py-0.5 text-[10px] text-text-secondary">{node.tier}</span>
                </div>
                <p className="mt-1 text-xs leading-5 text-text-secondary">{node.conflictUse}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-lg border border-border bg-surface p-5">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
            <GitBranch size={18} className="text-accent" />
            Relationship contract
          </h2>
          <div className="mt-4 max-h-[660px] space-y-2 overflow-auto pr-1">
            {ontologyEdges.map((edge) => (
              <div key={edge.type} className="rounded-lg border border-border bg-background p-3">
                <code className="text-xs font-semibold text-accent">{edge.type}</code>
                <p className="mt-1 text-[11px] text-text-secondary">
                  {edge.source} -&gt; {edge.target}
                </p>
                <p className="mt-1 text-xs text-text-secondary">{edge.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="rounded-lg border border-border bg-surface p-5">
        <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
          <div>
            <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
              <Brain size={18} className="text-accent" />
              Neurosymbolic benchmark plan
            </h2>
            <p className="mt-1 max-w-3xl text-sm text-text-secondary">
              The Databricks manual benchmark job compares plain LLM answers against
              DIALECTICA graph-grounded answers. Results land in Delta so the advantage
              can be inspected by task, domain, provenance, and graph score.
            </p>
          </div>
          <a
            href={databricksJobsUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-primary inline-flex items-center justify-center gap-2"
          >
            Open Benchmark Job
            <ArrowRight size={15} />
          </a>
        </div>

        <div className="mt-5 grid gap-3 lg:grid-cols-5">
          {benchmarkPlan.map((item) => (
            <div key={item.task} className="rounded-lg border border-border bg-background p-4">
              <p className="text-sm font-semibold text-text-primary">{item.task}</p>
              <p className="mt-3 text-[11px] font-semibold uppercase tracking-wide text-warning">
                Baseline risk
              </p>
              <p className="mt-1 text-xs leading-5 text-text-secondary">{item.baselineWeakness}</p>
              <p className="mt-3 text-[11px] font-semibold uppercase tracking-wide text-accent">
                DIALECTICA advantage
              </p>
              <p className="mt-1 text-xs leading-5 text-text-secondary">{item.dialecticaAdvantage}</p>
            </div>
          ))}
        </div>

        <div className="mt-5 grid gap-3 lg:grid-cols-3">
          {benchmarkRunCards.map((run) => (
            <div key={run.run} className="rounded-lg border border-border bg-background p-4">
              <div className="flex items-start justify-between gap-3">
                <code className="text-xs text-accent">{run.run}</code>
                <span className="rounded-md bg-surface px-2 py-1 text-[10px] text-text-secondary">n={run.n}</span>
              </div>
              <p className="mt-3 text-xs leading-5 text-text-secondary">{run.graphSnapshot}</p>
              <p className="mt-2 text-xs leading-5 text-text-secondary">Evaluator: {run.evaluator}</p>
              <p className="mt-2 rounded-md bg-surface px-2 py-1 text-[11px] leading-5 text-accent">
                {run.metrics}
              </p>
              <p className="mt-3 text-[11px] leading-5 text-warning">{run.failureMode}</p>
            </div>
          ))}
        </div>

        <div className="mt-5 grid gap-3 md:grid-cols-4">
          {[
            ["benchmark_items", "seed questions and gold summaries"],
            ["benchmark_prompts", "baseline and graph-grounded prompts"],
            ["benchmark_answers", "model outputs by approach"],
            ["benchmark_judgments", "AI judge scores and notes"],
          ].map(([table, label]) => (
            <div key={table} className="rounded-lg border border-border bg-background p-3">
              <code className="text-xs text-accent">{table}</code>
              <p className="mt-1 text-xs text-text-secondary">{label}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-lg border border-border bg-surface p-5">
        <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
          <Shield size={18} className="text-accent" />
          Governance and use boundaries
        </h2>
        <p className="mt-2 max-w-4xl text-sm leading-6 text-text-secondary">
          This is built for civilian, mediation, policy, and intelligence-adjacent
          understanding where provenance and restraint matter. The system should help
          people understand complex situations, identify gaps, and reduce unsupported
          reasoning, not automate high-impact action from unverified claims.
        </p>
        <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          {safetyBoundaries.map((item) => (
            <div key={item.boundary} className="rounded-lg border border-border bg-background p-4">
              <p className="text-sm font-semibold text-text-primary">{item.boundary}</p>
              <p className="mt-2 text-xs leading-5 text-text-secondary">{item.detail}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-2">
        <div className="rounded-lg border border-border bg-surface p-5">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
            <Shield size={18} className="text-accent" />
            Conflict analysis ontology extensions
          </h2>
          <div className="mt-4 space-y-3">
            {conflictOntologyExtensions.map((item) => (
              <div key={item.name} className="rounded-lg border border-border bg-background p-4">
                <div className="flex items-center gap-2">
                  <CheckCircle2 size={15} className="text-success" />
                  <p className="text-sm font-semibold text-text-primary">{item.name}</p>
                </div>
                <p className="mt-1 text-xs text-accent">{item.frameworks}</p>
                <p className="mt-2 text-xs leading-5 text-text-secondary">{item.graphSignals}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-lg border border-border bg-surface p-5">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-text-primary">
            <BookOpen size={18} className="text-accent" />
            Open-source book ingestion starts
          </h2>
          <p className="mt-1 text-sm text-text-secondary">
            Start with public-domain books because they contain dense conflict dynamics
            without licensing friction.
          </p>
          <div className="mt-4 space-y-3">
            {bookStarts.map((book) => (
              <div key={book.id} className="rounded-lg border border-border bg-background p-4">
                <div className="flex items-center justify-between gap-3">
                  <p className="text-sm font-semibold text-text-primary">{book.title}</p>
                  <code className="rounded-md bg-surface px-2 py-1 text-[11px] text-accent">Gutenberg {book.id}</code>
                </div>
                <p className="mt-2 text-xs leading-5 text-text-secondary">{book.why}</p>
              </div>
            ))}
          </div>
          <pre className="mt-4 overflow-x-auto rounded-lg border border-border bg-background p-4 text-xs leading-5 text-text-secondary">
            <code>{`uv run python tools/download_gutenberg.py 1513 --output data/raw/romeo_juliet.txt --max-chars 80000
uv run python tools/ingest_text_to_neo4j.py data/raw/romeo_juliet.txt --workspace-id books-romeo-juliet --tenant-id tacitus-lab
databricks bundle validate -t dev
databricks bundle run tacitus_operational_loop -t dev`}</code>
          </pre>
        </div>
      </section>
    </div>
  );
}
