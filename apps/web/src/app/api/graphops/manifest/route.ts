import { NextResponse } from "next/server";
import {
  agenticTools,
  embeddableSurfaces,
  graphCategories,
  ontologyProfileOptions,
  orchestrationEvents,
  qualityGates,
  sourcePacks,
} from "@/data/graphops";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  return NextResponse.json({
    product: "TACITUS DIALECTICA GraphOps",
    version: "0.1.0",
    purpose:
      "Reusable neurosymbolic graph operations layer for TACITUS products: source ingestion, dynamic ontology selection, Databricks extraction, Neo4j graph memory, quality review, and benchmarking.",
    auth: {
      current: "Basic Auth at deployment edge",
      productionTarget:
        "TACITUS product-to-product service auth with scoped workspace permissions and audit logs.",
    },
    endpoints: {
      console: "/graphops",
      databricksJobs: "/api/graphops/databricks/jobs",
      databricksTables: "/api/graphops/databricks/tables",
      ingest: "/api/graphops/ingest",
      triggerWorkflow: "/api/graphops/databricks/run",
      neo4jQuery: "/api/graphops/query",
      manifest: "/api/graphops/manifest",
    },
    integrationPattern: [
      "Product creates or selects a workspace and source pack.",
      "Product selects or requests an ontology profile from objective, user role, and question type.",
      "GraphOps triggers a Databricks workflow for ingestion, extraction, quality gates, and benchmark runs.",
      "Accepted claims write into Neo4j as workspace-scoped graph memory after production Neo4j secrets are configured.",
      "Product asks graph-grounded questions through allowlisted query and GraphRAG planner APIs.",
    ],
    capabilities: agenticTools,
    embeddableSurfaces,
    ontologyProfiles: ontologyProfileOptions,
    graphCategories,
    qualityGates,
    sourcePacks,
    events: orchestrationEvents,
    readiness: {
      deployed: true,
      databricksLive: true,
      neo4jCodeReady: true,
      neo4jSecretsConfigured: Boolean(
        process.env.NEO4J_URI &&
          (process.env.NEO4J_USERNAME || process.env.NEO4J_USER) &&
          process.env.NEO4J_PASSWORD,
      ),
    },
  });
}
