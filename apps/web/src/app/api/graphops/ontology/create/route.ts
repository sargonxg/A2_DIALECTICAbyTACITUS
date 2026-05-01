import { NextResponse } from "next/server";
import { buildDynamicOntologyPlan } from "@/lib/dynamicOntology";
import { stageGraphOpsArtifactToDatabricks } from "@/lib/graphopsDatabricks";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  const body = await request.json().catch(() => ({}));
  const workspaceId = String(body.workspaceId || "graphops-workspace");
  const caseId = String(body.caseId || "graphops-case");
  const profileId = String(body.ontologyProfile || "human-friction");
  const objective = String(body.objective || "Understand the conflict with provenance.");
  const sourceType = String(body.sourceType || "");
  const stageToDatabricks = Boolean(body.stageToDatabricks);
  const plan = buildDynamicOntologyPlan({
    profileId,
    objective,
    sourceType,
    templateId: String(body.templateId || ""),
  });
  const artifact = {
    kind: "tacitus.dialectica.dynamic_ontology_plan.v1",
    workspace_id: workspaceId,
    case_id: caseId,
    ontology_plan: plan,
    created_at: new Date().toISOString(),
  };
  const databricks = stageToDatabricks
    ? await stageGraphOpsArtifactToDatabricks({
        workspaceId,
        caseId,
        artifactType: "dynamic-ontology",
        artifactId: plan.id,
        payload: artifact,
      })
    : { requested: false };

  return NextResponse.json({ artifact, databricks });
}
