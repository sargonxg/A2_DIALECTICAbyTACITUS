# Databricks notebook source
# MAGIC %md
# MAGIC # DIALECTICA Neo4j -> Delta operational signals
# MAGIC
# MAGIC This notebook turns the live Neo4j graph into Databricks tables, computes operational graph signals, optionally summarizes them with Gemini, and can write a compact signal node back to Neo4j.
# MAGIC
# MAGIC Store secrets in a Databricks secret scope first. Do not paste credentials into notebook cells.

# COMMAND ----------

# MAGIC %pip install neo4j google-genai

# COMMAND ----------

import json
import re
from datetime import datetime, timezone

from neo4j import GraphDatabase
from pyspark.sql import functions as F
from pyspark.sql.types import (
    DoubleType,
    StringType,
    StructField,
    StructType,
)


def clean_identifier(value: str, field_name: str) -> str:
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
        raise ValueError(f"Invalid {field_name}: {value!r}")
    return value


dbutils.widgets.text("workspace_id", "")
dbutils.widgets.text("secret_scope", "tacitus")
dbutils.widgets.text("catalog", "dialectica")
dbutils.widgets.text("schema", "conflict_graphs")
dbutils.widgets.dropdown("write_back_to_neo4j", "false", ["false", "true"])
dbutils.widgets.text("gemini_model", "gemini-2.5-flash")

WORKSPACE_ID = dbutils.widgets.get("workspace_id").strip()
SECRET_SCOPE = dbutils.widgets.get("secret_scope").strip()
CATALOG = clean_identifier(dbutils.widgets.get("catalog").strip(), "catalog")
SCHEMA = clean_identifier(dbutils.widgets.get("schema").strip(), "schema")
WRITE_BACK = dbutils.widgets.get("write_back_to_neo4j") == "true"
GEMINI_MODEL = dbutils.widgets.get("gemini_model").strip()

NODE_TABLE = f"{CATALOG}.{SCHEMA}.nodes_bronze"
EDGE_TABLE = f"{CATALOG}.{SCHEMA}.edges_bronze"
ACTOR_FEATURE_TABLE = f"{CATALOG}.{SCHEMA}.actor_features"
QUALITY_TABLE = f"{CATALOG}.{SCHEMA}.graph_quality_signals"

# COMMAND ----------

neo4j_uri = dbutils.secrets.get(SECRET_SCOPE, "neo4j-uri")
neo4j_user = dbutils.secrets.get(SECRET_SCOPE, "neo4j-user")
neo4j_password = dbutils.secrets.get(SECRET_SCOPE, "neo4j-password")
neo4j_database = dbutils.secrets.get(SECRET_SCOPE, "neo4j-database")

driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

# COMMAND ----------

node_schema = StructType(
    [
        StructField("id", StringType(), False),
        StructField("workspace_id", StringType(), True),
        StructField("tenant_id", StringType(), True),
        StructField("label", StringType(), True),
        StructField("name", StringType(), True),
        StructField("confidence", DoubleType(), True),
        StructField("created_at", StringType(), True),
        StructField("properties_json", StringType(), True),
        StructField("ingested_at", StringType(), False),
    ]
)

edge_schema = StructType(
    [
        StructField("id", StringType(), False),
        StructField("workspace_id", StringType(), True),
        StructField("tenant_id", StringType(), True),
        StructField("source_id", StringType(), True),
        StructField("target_id", StringType(), True),
        StructField("type", StringType(), True),
        StructField("confidence", DoubleType(), True),
        StructField("weight", DoubleType(), True),
        StructField("properties_json", StringType(), True),
        StructField("ingested_at", StringType(), False),
    ]
)


def fetch_graph_snapshot(workspace_id: str) -> tuple[list[dict], list[dict]]:
    ingested_at = datetime.now(timezone.utc).isoformat()
    with driver.session(database=neo4j_database) as session:
        nodes = session.run(
            """
            MATCH (n:ConflictNode)
            WHERE $workspace_id = "" OR n.workspace_id = $workspace_id
            RETURN
              n.id AS id,
              n.workspace_id AS workspace_id,
              n.tenant_id AS tenant_id,
              coalesce(n.label, head(labels(n))) AS label,
              coalesce(n.name, n.title, n.id) AS name,
              toFloat(coalesce(n.confidence, 1.0)) AS confidence,
              toString(n.created_at) AS created_at,
              properties(n) AS properties
            """,
            workspace_id=workspace_id,
        )
        node_rows = [
            {
                "id": row["id"],
                "workspace_id": row["workspace_id"],
                "tenant_id": row["tenant_id"],
                "label": row["label"],
                "name": row["name"],
                "confidence": row["confidence"],
                "created_at": row["created_at"],
                "properties_json": json.dumps(row["properties"], default=str),
                "ingested_at": ingested_at,
            }
            for row in nodes
        ]

        edges = session.run(
            """
            MATCH (s:ConflictNode)-[r]->(t:ConflictNode)
            WHERE r.type IS NOT NULL
              AND ($workspace_id = "" OR r.workspace_id = $workspace_id)
            RETURN
              coalesce(r.id, elementId(r)) AS id,
              r.workspace_id AS workspace_id,
              r.tenant_id AS tenant_id,
              s.id AS source_id,
              t.id AS target_id,
              r.type AS type,
              toFloat(coalesce(r.confidence, 1.0)) AS confidence,
              toFloat(coalesce(r.weight, 1.0)) AS weight,
              properties(r) AS properties
            """,
            workspace_id=workspace_id,
        )
        edge_rows = [
            {
                "id": row["id"],
                "workspace_id": row["workspace_id"],
                "tenant_id": row["tenant_id"],
                "source_id": row["source_id"],
                "target_id": row["target_id"],
                "type": row["type"],
                "confidence": row["confidence"],
                "weight": row["weight"],
                "properties_json": json.dumps(row["properties"], default=str),
                "ingested_at": ingested_at,
            }
            for row in edges
        ]

    return node_rows, edge_rows


node_rows, edge_rows = fetch_graph_snapshot(WORKSPACE_ID)
nodes_df = spark.createDataFrame(node_rows, node_schema)
edges_df = spark.createDataFrame(edge_rows, edge_schema)

display(nodes_df.groupBy("label").count().orderBy(F.desc("count")))
display(edges_df.groupBy("type").count().orderBy(F.desc("count")))

# COMMAND ----------

spark.sql(f"CREATE CATALOG IF NOT EXISTS {CATALOG}")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}")

nodes_df.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(NODE_TABLE)
edges_df.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(EDGE_TABLE)

print(f"Wrote {nodes_df.count()} nodes to {NODE_TABLE}")
print(f"Wrote {edges_df.count()} edges to {EDGE_TABLE}")

# COMMAND ----------

nodes = spark.table(NODE_TABLE)
edges = spark.table(EDGE_TABLE)

source_degree = edges.groupBy(F.col("source_id").alias("id")).agg(F.count("*").alias("out_degree"))
target_degree = edges.groupBy(F.col("target_id").alias("id")).agg(F.count("*").alias("in_degree"))

actor_features = (
    nodes.filter(F.col("label") == "Actor")
    .select("id", "workspace_id", "tenant_id", "name", "confidence")
    .join(source_degree, "id", "left")
    .join(target_degree, "id", "left")
    .fillna({"out_degree": 0, "in_degree": 0})
    .withColumn("degree", F.col("out_degree") + F.col("in_degree"))
)

edge_counts = edges.groupBy("source_id", "type").count()

actor_features = (
    actor_features.join(
        edge_counts.filter(F.col("type") == "OPPOSED_TO")
        .select(F.col("source_id").alias("id"), F.col("count").alias("opposed_to_count")),
        "id",
        "left",
    )
    .join(
        edge_counts.filter(F.col("type") == "ALLIED_WITH")
        .select(F.col("source_id").alias("id"), F.col("count").alias("allied_with_count")),
        "id",
        "left",
    )
    .join(
        edge_counts.filter(F.col("type") == "TRUSTS")
        .select(F.col("source_id").alias("id"), F.col("count").alias("trust_edge_count")),
        "id",
        "left",
    )
    .fillna({"opposed_to_count": 0, "allied_with_count": 0, "trust_edge_count": 0})
    .withColumn("computed_at", F.current_timestamp())
)

actor_features.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(
    ACTOR_FEATURE_TABLE
)
display(actor_features.orderBy(F.desc("degree")).limit(25))

# COMMAND ----------

evidenced_targets = edges.filter(F.col("type") == "EVIDENCED_BY").select(
    F.col("source_id").alias("id")
)

unsupported_nodes = (
    nodes.filter(F.col("label").isin("Conflict", "Event", "Issue", "Interest", "Narrative"))
    .join(evidenced_targets, "id", "left_anti")
    .select("id", "workspace_id", "label", "name", "confidence")
)

low_confidence_edges = edges.filter(F.col("confidence") < 0.6).select(
    "id", "workspace_id", "type", "source_id", "target_id", "confidence"
)

quality_summary = spark.createDataFrame(
    [
        {
            "workspace_id": WORKSPACE_ID or "all",
            "node_count": nodes.count(),
            "edge_count": edges.count(),
            "unsupported_key_node_count": unsupported_nodes.count(),
            "low_confidence_edge_count": low_confidence_edges.count(),
            "computed_at": datetime.now(timezone.utc).isoformat(),
        }
    ]
)

quality_summary.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(
    QUALITY_TABLE
)

display(quality_summary)
display(unsupported_nodes.orderBy(F.asc("confidence")).limit(50))
display(low_confidence_edges.orderBy(F.asc("confidence")).limit(50))

# COMMAND ----------

summary_payload = {
    "workspace_id": WORKSPACE_ID or "all",
    "quality": quality_summary.collect()[0].asDict(),
    "top_actors": [row.asDict() for row in actor_features.orderBy(F.desc("degree")).limit(10).collect()],
    "top_edge_types": [row.asDict() for row in edges.groupBy("type").count().orderBy(F.desc("count")).limit(10).collect()],
}

try:
    from google import genai
    from google.genai import types

    gemini_api_key = dbutils.secrets.get(SECRET_SCOPE, "gemini-api-key")
    gemini = genai.Client(api_key=gemini_api_key)
    prompt = (
        "You are helping operate DIALECTICA by TACITUS. "
        "Given this graph operations JSON, return concise JSON with keys: "
        "risks, recommended_actions, watchlist_actor_ids, data_quality_fixes. "
        "Ground every point in the provided fields only.\n\n"
        f"{json.dumps(summary_payload, default=str)}"
    )
    response = gemini.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1,
        ),
    )
    operations_summary = json.loads(response.text)
except Exception as exc:
    operations_summary = {
        "risks": ["Gemini summary unavailable"],
        "recommended_actions": [str(exc)],
        "watchlist_actor_ids": [],
        "data_quality_fixes": [],
    }

print(json.dumps(operations_summary, indent=2))

# COMMAND ----------

if WRITE_BACK:
    signal_id = f"ops-signal-{WORKSPACE_ID or 'all'}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    with driver.session(database=neo4j_database) as session:
        session.run(
            """
            MERGE (s:OperationalSignal {id: $id})
            SET s.workspace_id = $workspace_id,
                s.kind = "databricks_graph_ops",
                s.summary_json = $summary_json,
                s.metrics_json = $metrics_json,
                s.created_at = datetime()
            """,
            id=signal_id,
            workspace_id=WORKSPACE_ID or "all",
            summary_json=json.dumps(operations_summary, default=str),
            metrics_json=json.dumps(summary_payload, default=str),
        )
    print(f"Wrote OperationalSignal {signal_id} back to Neo4j")
else:
    print("write_back_to_neo4j=false, so no Neo4j writes were made.")

driver.close()
