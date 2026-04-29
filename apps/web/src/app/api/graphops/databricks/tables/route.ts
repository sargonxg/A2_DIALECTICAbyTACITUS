import { NextResponse } from "next/server";
import { liveDeltaTables } from "@/data/graphops";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function databricksConfig() {
  const host =
    process.env.DATABRICKS_HOST ||
    "https://dbc-69e04818-40fb.cloud.databricks.com";
  const token = process.env.DATABRICKS_TOKEN;
  const warehouseId = process.env.DATABRICKS_WAREHOUSE_ID || "899e49cf534f936b";
  return { host: host.replace(/\/$/, ""), token, warehouseId };
}

const statement = `
SELECT 'raw_text_chunks' AS table_name, count(*) AS rows FROM dialectica.conflict_graphs.raw_text_chunks
UNION ALL SELECT 'ai_extraction_candidates', count(*) FROM dialectica.conflict_graphs.ai_extraction_candidates
UNION ALL SELECT 'ontology_profile_coverage', count(*) FROM dialectica.conflict_graphs.ontology_profile_coverage
UNION ALL SELECT 'source_reliability_signals', count(*) FROM dialectica.conflict_graphs.source_reliability_signals
UNION ALL SELECT 'temporal_event_signals', count(*) FROM dialectica.conflict_graphs.temporal_event_signals
UNION ALL SELECT 'claim_review_queue', count(*) FROM dialectica.conflict_graphs.claim_review_queue
`;

export async function GET() {
  const { host, token, warehouseId } = databricksConfig();

  if (!token) {
    return NextResponse.json({
      mode: "configured-metadata",
      message: "Set DATABRICKS_TOKEN for live Delta table counts.",
      tables: liveDeltaTables,
    });
  }

  const response = await fetch(`${host}/api/2.0/sql/statements`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      warehouse_id: warehouseId,
      statement,
      wait_timeout: "50s",
      on_wait_timeout: "CONTINUE",
    }),
    cache: "no-store",
  });

  const payload = await response.json().catch(() => ({}));
  if (!response.ok || payload?.status?.state !== "SUCCEEDED") {
    return NextResponse.json(
      {
        mode: "fallback",
        message: `Could not read Databricks table counts. Status: ${payload?.status?.state ?? response.status}`,
        tables: liveDeltaTables,
      },
      { status: 502 },
    );
  }

  const rows = Array.isArray(payload?.result?.data_array) ? payload.result.data_array : [];
  const counts = new Map<string, number>(
    rows.map((row: unknown[]) => [String(row[0]), Number(row[1] ?? 0)]),
  );

  return NextResponse.json({
    mode: "live",
    tables: liveDeltaTables.map((table) => ({
      ...table,
      rows: counts.get(table.table) ?? table.rows,
    })),
  });
}
