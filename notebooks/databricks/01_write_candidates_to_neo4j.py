# Databricks notebook source
# MAGIC %md
# MAGIC # DIALECTICA Writer: AI Extraction Candidates to Neo4j
# MAGIC
# MAGIC Validates AI extraction candidate JSON against the TACITUS ontology contract
# MAGIC and writes accepted candidates into the Neo4j operational graph.

# COMMAND ----------

# MAGIC %pip install neo4j

# COMMAND ----------

import json
import re
from datetime import datetime, timezone
from hashlib import sha256

from neo4j import GraphDatabase
from pyspark.sql import functions as F

dbutils.widgets.text("workspace_id", "books-romeo-juliet")
dbutils.widgets.text("secret_scope", "tacitus")
dbutils.widgets.text("catalog", "dialectica")
dbutils.widgets.text("schema", "conflict_graphs")
dbutils.widgets.text("max_rows", "100")

WORKSPACE_ID = dbutils.widgets.get("workspace_id").strip()
SECRET_SCOPE = dbutils.widgets.get("secret_scope").strip()
CATALOG = dbutils.widgets.get("catalog").strip()
SCHEMA = dbutils.widgets.get("schema").strip()
MAX_ROWS = int(dbutils.widgets.get("max_rows"))

CANDIDATE_TABLE = f"{CATALOG}.{SCHEMA}.ai_extraction_candidates"

ALLOWED_LABELS = {
    "Actor",
    "Conflict",
    "Event",
    "Issue",
    "Interest",
    "Norm",
    "Process",
    "Outcome",
    "Narrative",
    "PowerDynamic",
    "EmotionalState",
    "TrustState",
    "Location",
    "Evidence",
    "Role",
}

ALLOWED_EDGES = {
    "PARTY_TO",
    "PARTICIPATES_IN",
    "HAS_INTEREST",
    "PART_OF",
    "CAUSED",
    "AT_LOCATION",
    "WITHIN",
    "GOVERNED_BY",
    "VIOLATES",
    "RESOLVED_THROUGH",
    "PRODUCES",
    "ALLIED_WITH",
    "OPPOSED_TO",
    "HAS_POWER_OVER",
    "MEMBER_OF",
    "EXPERIENCES",
    "TRUSTS",
    "PROMOTES",
    "ABOUT",
    "EVIDENCED_BY",
}


def stable_id(*parts: str) -> str:
    joined = "::".join(parts)
    return sha256(joined.encode("utf-8")).hexdigest()[:24]


def clean_json(raw: str) -> dict:
    text = raw.strip()
    text = re.sub(r"^```(?:json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    return json.loads(text)


def confidence(value) -> float:
    try:
        return max(0.0, min(1.0, float(value)))
    except Exception:
        return 0.5


rows = (
    spark.table(CANDIDATE_TABLE)
    .where(F.col("workspace_id") == WORKSPACE_ID)
    .orderBy(F.desc("extracted_at"))
    .limit(MAX_ROWS)
    .collect()
)

nodes: dict[str, dict] = {}
edges: list[dict] = []
rejections: list[dict] = []

for row in rows:
    try:
        payload = clean_json(row["extraction_json"])
    except Exception as exc:
        rejections.append({"chunk_id": row["chunk_id"], "reason": f"invalid_json: {exc}"})
        continue

    local_to_global: dict[str, str] = {}
    for node in payload.get("nodes", []):
        label = str(node.get("label", ""))
        local_id = str(node.get("local_id", ""))
        if label not in ALLOWED_LABELS or not local_id:
            rejections.append({"chunk_id": row["chunk_id"], "reason": f"bad_node: {label}/{local_id}"})
            continue
        node_id = stable_id(row["workspace_id"], row["chunk_id"], local_id, label)
        local_to_global[local_id] = node_id
        props = dict(node.get("properties") or {})
        props.update(
            {
                "id": node_id,
                "label": label,
                "workspace_id": row["workspace_id"],
                "tenant_id": row["tenant_id"],
                "name": str(node.get("name", local_id))[:500],
                "confidence": confidence(node.get("confidence")),
                "source": row["source_id"],
                "source_chunk_id": row["chunk_id"],
                "source_quote": str(node.get("source_quote", ""))[:500],
                "extraction_method": "databricks_ai_query",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        nodes[node_id] = {"id": node_id, "label": label, "props": props}

    for edge in payload.get("edges", []):
        edge_type = str(edge.get("type", ""))
        source_id = local_to_global.get(str(edge.get("source_local_id", "")))
        target_id = local_to_global.get(str(edge.get("target_local_id", "")))
        if edge_type not in ALLOWED_EDGES or not source_id or not target_id:
            rejections.append({"chunk_id": row["chunk_id"], "reason": f"bad_edge: {edge_type}"})
            continue
        edge_props = dict(edge.get("properties") or {})
        edge_props.update(
            {
                "id": stable_id(row["workspace_id"], row["chunk_id"], source_id, edge_type, target_id),
                "workspace_id": row["workspace_id"],
                "tenant_id": row["tenant_id"],
                "confidence": confidence(edge.get("confidence")),
                "source": row["source_id"],
                "source_chunk_id": row["chunk_id"],
                "source_quote": str(edge.get("source_quote", ""))[:500],
                "extraction_method": "databricks_ai_query",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        edges.append({"source_id": source_id, "target_id": target_id, "type": edge_type, "props": edge_props})

# COMMAND ----------

neo4j_uri = dbutils.secrets.get(SECRET_SCOPE, "neo4j-uri")
neo4j_user = dbutils.secrets.get(SECRET_SCOPE, "neo4j-user")
neo4j_password = dbutils.secrets.get(SECRET_SCOPE, "neo4j-password")
neo4j_database = dbutils.secrets.get(SECRET_SCOPE, "neo4j-database")

with GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password)) as driver:
    with driver.session(database=neo4j_database) as session:
        for item in nodes.values():
            label = item["label"]
            session.run(
                f"""
                MERGE (n:ConflictNode:{label} {{id: $id}})
                SET n += $props
                """,
                id=item["id"],
                props=item["props"],
            ).consume()

        for edge in edges:
            session.run(
                f"""
                MATCH (a:ConflictNode {{id: $source_id}})
                MATCH (b:ConflictNode {{id: $target_id}})
                MERGE (a)-[r:{edge["type"]} {{id: $id}}]->(b)
                SET r += $props
                """,
                source_id=edge["source_id"],
                target_id=edge["target_id"],
                id=edge["props"]["id"],
                props=edge["props"],
            ).consume()

summary = spark.createDataFrame(
    [
        {
            "workspace_id": WORKSPACE_ID,
            "nodes_written": len(nodes),
            "edges_written": len(edges),
            "rejections": len(rejections),
            "written_at": datetime.now(timezone.utc).isoformat(),
        }
    ]
)
summary.write.mode("append").format("delta").saveAsTable(f"{CATALOG}.{SCHEMA}.neo4j_write_summaries")

display(summary)
if rejections:
    display(spark.createDataFrame(rejections))
