import { NextResponse } from "next/server";
import {
  benchmarkBlockCatalog,
  dynamicOntologyEngine,
  ontologyProfileOptions,
  pipelineBlockCatalog,
  workspaceProjectTemplates,
} from "@/data/graphops";
import { buildDynamicOntologyPlan, coreMappingsForProfile } from "@/lib/dynamicOntology";
import { stageGraphOpsArtifactToDatabricks } from "@/lib/graphopsDatabricks";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function safeId(value: string) {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "").slice(0, 80);
}

function selectBlockIds(
  mode: string,
  includeTemporal: boolean,
  includeAbstractKnowledge: boolean,
  includeBenchmarks: boolean,
) {
  const ids = [
    "source-upload",
    mode === "local-python" ? "local-python-digestion" : "lakehouse-chunking",
    "aletheia-ontology-profile",
    "primitive-extraction",
    mode === "falkordb" ? "falkordb-alternative" : "neo4j-memory-write",
    "agent-result-terminal",
  ];
  if (includeTemporal) ids.splice(3, 0, "temporal-episode-splitter");
  if (includeAbstractKnowledge) ids.splice(ids.length - 1, 0, "abstract-knowledge-graph");
  if (includeBenchmarks) ids.push("benchmark-evaluation");
  return ids;
}

export async function POST(request: Request) {
  const body = await request.json().catch(() => ({}));
  const templateId = String(body.templateId ?? "book-conflict-lab");
  const profileId = String(body.ontologyProfile ?? "literary-conflict");
  const backendMode = String(body.backendMode ?? "databricks-neo4j");
  const includeTemporal = body.includeTemporal !== false;
  const includeAbstractKnowledge = body.includeAbstractKnowledge !== false;
  const includeBenchmarks = body.includeBenchmarks !== false;
  const stageToDatabricks = Boolean(body.stageToDatabricks);
  const template = workspaceProjectTemplates.find((item) => item.id === templateId) ?? workspaceProjectTemplates[0];
  const profile = ontologyProfileOptions.find((item) => item.id === profileId) ?? ontologyProfileOptions[0];
  const caseName = String(body.caseName ?? template.name);
  const workspaceId = safeId(String(body.workspaceId ?? `${template.workspacePrefix}-${caseName}`));
  const caseId = safeId(String(body.caseId ?? caseName));
  const objective = String(body.objective ?? template.defaultObjective);
  const pipelineId = `pipeline_${crypto.randomUUID().replace(/-/g, "").slice(0, 16)}`;
  const blockIds = selectBlockIds(backendMode, includeTemporal, includeAbstractKnowledge, includeBenchmarks);
  const blocks = blockIds
    .map((id, order) => {
      const block = pipelineBlockCatalog.find((item) => item.id === id);
      return block ? { order: order + 1, ...block } : null;
    })
    .filter(Boolean);
  const ontologyPlan = buildDynamicOntologyPlan({
    profileId: profile.id,
    objective,
    sourceType: template.sourceExamples,
    templateId,
  });

  const artifact = {
    kind: "tacitus.dialectica.pipeline_plan.v1",
    pipeline_id: pipelineId,
    workspace_id: workspaceId,
    case_id: caseId,
    case_name: caseName,
    template,
    backend_mode: backendMode,
    objective,
    dynamic_ontology_engine: dynamicOntologyEngine,
    ontology_profile: {
      id: profile.id,
      label: profile.label,
      objective: profile.objective,
      required_nodes: profile.requiredNodes,
      required_edges: profile.requiredEdges,
      custom_mappings: coreMappingsForProfile(profile.id),
      schema_validation_status: "draft_valid",
    },
    dynamic_ontology_plan: ontologyPlan,
    graph_layers: [
      "source_provenance_graph",
      "situation_graph",
      "episodic_temporal_graph",
      "abstract_knowledge_graph",
      "reasoning_trace_graph",
      "activity_audit_graph",
    ],
    blocks,
    benchmark_blocks: includeBenchmarks ? benchmarkBlockCatalog : [],
    terminal_agents: ["Source Scout", "Ontology Builder", "Claim Verifier", "Temporal Analyst", "GraphRAG Planner", "Benchmark Judge"],
    created_at: new Date().toISOString(),
  };

  const databricks = stageToDatabricks
    ? await stageGraphOpsArtifactToDatabricks({
        workspaceId,
        caseId,
        artifactType: "pipeline-plan",
        artifactId: pipelineId,
        payload: artifact,
      })
    : { requested: false };

  return NextResponse.json({ artifact, databricks });
}
