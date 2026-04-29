# Databricks notebook source
# MAGIC %md
# MAGIC # DIALECTICA review queue
# MAGIC
# MAGIC Builds a human validation queue from Delta graph snapshots. This should be run after `01_neo4j_delta_operational_signals.py`.

# COMMAND ----------

from datetime import datetime, timezone

from pyspark.sql import functions as F


dbutils.widgets.text("catalog", "dialectica")
dbutils.widgets.text("schema", "conflict_graphs")
dbutils.widgets.text("workspace_id", "")
dbutils.widgets.text("min_confidence", "0.60")

CATALOG = dbutils.widgets.get("catalog")
SCHEMA = dbutils.widgets.get("schema")
WORKSPACE_ID = dbutils.widgets.get("workspace_id").strip()
MIN_CONFIDENCE = float(dbutils.widgets.get("min_confidence"))

NODE_TABLE = f"{CATALOG}.{SCHEMA}.nodes_bronze"
EDGE_TABLE = f"{CATALOG}.{SCHEMA}.edges_bronze"
REVIEW_TABLE = f"{CATALOG}.{SCHEMA}.review_queue"

# COMMAND ----------

nodes = spark.table(NODE_TABLE)
edges = spark.table(EDGE_TABLE)

if WORKSPACE_ID:
    nodes = nodes.filter(F.col("workspace_id") == WORKSPACE_ID)
    edges = edges.filter(F.col("workspace_id") == WORKSPACE_ID)

evidenced_targets = edges.filter(F.col("type") == "EVIDENCED_BY").select(
    F.col("source_id").alias("evidenced_item_id")
)

unsupported_key_nodes = (
    nodes.filter(F.col("label").isin("Conflict", "Event", "Issue", "Interest", "Narrative"))
    .join(evidenced_targets, F.col("id") == F.col("evidenced_item_id"), "left_anti")
    .select(
        F.col("workspace_id"),
        F.col("tenant_id"),
        F.col("id").alias("item_id"),
        F.col("label").alias("item_type"),
        F.lit("missing_evidence_edge").alias("reason"),
        F.when(F.col("label").isin("Conflict", "Event"), F.lit("high")).otherwise(F.lit("medium")).alias(
            "severity"
        ),
        F.col("name").alias("item_name"),
        F.col("confidence"),
        F.col("properties_json"),
    )
)

low_confidence_edges = edges.filter(F.col("confidence") < MIN_CONFIDENCE).select(
    F.col("workspace_id"),
    F.col("tenant_id"),
    F.col("id").alias("item_id"),
    F.col("type").alias("item_type"),
    F.lit("low_confidence_edge").alias("reason"),
    F.when(F.col("confidence") < 0.35, F.lit("high")).otherwise(F.lit("medium")).alias("severity"),
    F.concat_ws(" -> ", F.col("source_id"), F.col("target_id")).alias("item_name"),
    F.col("confidence"),
    F.col("properties_json"),
)

orphan_edges = (
    edges.join(nodes.select(F.col("id").alias("source_id")), "source_id", "left_anti")
    .select(
        F.col("workspace_id"),
        F.col("tenant_id"),
        F.col("id").alias("item_id"),
        F.col("type").alias("item_type"),
        F.lit("missing_source_node").alias("reason"),
        F.lit("critical").alias("severity"),
        F.concat_ws(" -> ", F.col("source_id"), F.col("target_id")).alias("item_name"),
        F.col("confidence"),
        F.col("properties_json"),
    )
    .unionByName(
        edges.join(nodes.select(F.col("id").alias("target_id")), "target_id", "left_anti")
        .select(
            F.col("workspace_id"),
            F.col("tenant_id"),
            F.col("id").alias("item_id"),
            F.col("type").alias("item_type"),
            F.lit("missing_target_node").alias("reason"),
            F.lit("critical").alias("severity"),
            F.concat_ws(" -> ", F.col("source_id"), F.col("target_id")).alias("item_name"),
            F.col("confidence"),
            F.col("properties_json"),
        )
    )
)

review_queue = (
    unsupported_key_nodes.unionByName(low_confidence_edges)
    .unionByName(orphan_edges)
    .dropDuplicates(["workspace_id", "item_id", "reason"])
    .withColumn("status", F.lit("open"))
    .withColumn("assigned_to", F.lit(None).cast("string"))
    .withColumn("review_notes", F.lit(None).cast("string"))
    .withColumn("created_at", F.lit(datetime.now(timezone.utc).isoformat()))
    .withColumn("reviewed_at", F.lit(None).cast("string"))
)

review_queue.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(REVIEW_TABLE)

display(review_queue.orderBy(F.desc("severity"), F.asc("confidence")))

# COMMAND ----------

display(
    spark.table(REVIEW_TABLE)
    .groupBy("workspace_id", "severity", "reason")
    .count()
    .orderBy(F.desc("count"))
)
