# Databricks notebook source
# MAGIC %md
# MAGIC # DIALECTICA Dynamic Ontology Quality and Profiles
# MAGIC
# MAGIC Builds operational tables for dynamic ontology profiles, source trust,
# MAGIC temporal reasoning, and claim review. This can run before Neo4j writeback
# MAGIC because it uses Delta extraction candidates.

# COMMAND ----------

import json
import re
from datetime import datetime, timezone

from pyspark.sql import functions as F, types as T

dbutils.widgets.text("catalog", "dialectica")
dbutils.widgets.text("schema", "conflict_graphs")
dbutils.widgets.text("workspace_id", "books-complex-conflict-lab")

CATALOG = dbutils.widgets.get("catalog")
SCHEMA = dbutils.widgets.get("schema")
WORKSPACE_ID = dbutils.widgets.get("workspace_id")

CANDIDATE_TABLE = f"{CATALOG}.{SCHEMA}.ai_extraction_candidates"
PROFILE_TABLE = f"{CATALOG}.{SCHEMA}.ontology_profile_coverage"
SOURCE_TABLE = f"{CATALOG}.{SCHEMA}.source_reliability_signals"
TEMPORAL_TABLE = f"{CATALOG}.{SCHEMA}.temporal_event_signals"
CLAIM_TABLE = f"{CATALOG}.{SCHEMA}.claim_review_queue"

# COMMAND ----------

node_schema = T.ArrayType(
    T.StructType(
        [
            T.StructField("local_id", T.StringType()),
            T.StructField("label", T.StringType()),
            T.StructField("name", T.StringType()),
            T.StructField("confidence", T.DoubleType()),
            T.StructField("source_quote", T.StringType()),
            T.StructField("properties", T.MapType(T.StringType(), T.StringType())),
        ]
    )
)

edge_schema = T.ArrayType(
    T.StructType(
        [
            T.StructField("type", T.StringType()),
            T.StructField("source_local_id", T.StringType()),
            T.StructField("target_local_id", T.StringType()),
            T.StructField("confidence", T.DoubleType()),
            T.StructField("source_quote", T.StringType()),
            T.StructField("properties", T.MapType(T.StringType(), T.StringType())),
        ]
    )
)

payload_schema = T.StructType(
    [
        T.StructField("nodes", node_schema),
        T.StructField("edges", edge_schema),
        T.StructField("warnings", T.ArrayType(T.StringType())),
    ]
)

def clean_json(text: str) -> str:
    if text is None:
        return "{}"
    text = re.sub(r"^```(?:json)?", "", text.strip())
    text = re.sub(r"```$", "", text.strip())
    return text

clean_json_udf = F.udf(clean_json, T.StringType())

candidates = (
    spark.table(CANDIDATE_TABLE)
    .where(F.col("workspace_id") == WORKSPACE_ID)
    .withColumn("payload", F.from_json(clean_json_udf("extraction_json"), payload_schema))
)

nodes = (
    candidates
    .select("workspace_id", "tenant_id", "source_id", "chunk_id", F.explode_outer("payload.nodes").alias("node"))
    .where(F.col("node.label").isNotNull())
)

edges = (
    candidates
    .select("workspace_id", "tenant_id", "source_id", "chunk_id", F.explode_outer("payload.edges").alias("edge"))
    .where(F.col("edge.type").isNotNull())
)

# COMMAND ----------

profile_requirements = spark.createDataFrame(
    [
        ("human_friction", "Actor"),
        ("human_friction", "Issue"),
        ("human_friction", "Interest"),
        ("human_friction", "EmotionalState"),
        ("human_friction", "TrustState"),
        ("human_friction", "PowerDynamic"),
        ("literary_conflict", "Actor"),
        ("literary_conflict", "Event"),
        ("literary_conflict", "Narrative"),
        ("literary_conflict", "EmotionalState"),
        ("literary_conflict", "Location"),
        ("political_policy", "Actor"),
        ("political_policy", "Norm"),
        ("political_policy", "Interest"),
        ("political_policy", "Process"),
        ("political_policy", "Outcome"),
        ("mediation_resolution", "Actor"),
        ("mediation_resolution", "Interest"),
        ("mediation_resolution", "Process"),
        ("mediation_resolution", "TrustState"),
        ("mediation_resolution", "Outcome"),
    ],
    ["profile", "required_label"],
)

label_counts = (
    nodes.groupBy("workspace_id", F.col("node.label").alias("label"))
    .agg(F.count("*").alias("count"))
)

coverage = (
    profile_requirements
    .join(label_counts, profile_requirements.required_label == label_counts.label, "left")
    .groupBy("profile")
    .agg(
        F.count("*").alias("required_labels"),
        F.sum(F.when(F.col("count") > 0, 1).otherwise(0)).alias("present_labels"),
        F.collect_list(
            F.struct("required_label", F.coalesce(F.col("count"), F.lit(0)).alias("count"))
        ).alias("label_counts"),
    )
    .withColumn("workspace_id", F.lit(WORKSPACE_ID))
    .withColumn("coverage_score", F.col("present_labels") / F.col("required_labels"))
    .withColumn("computed_at", F.current_timestamp())
)

coverage.write.mode("overwrite").format("delta").saveAsTable(PROFILE_TABLE)

# COMMAND ----------

source_signals = (
    candidates
    .groupBy("workspace_id", "source_id")
    .agg(
        F.countDistinct("chunk_id").alias("chunks"),
        F.count("*").alias("candidate_rows"),
        F.avg(F.length("extraction_json")).alias("avg_extraction_length"),
        F.max("extracted_at").alias("latest_extraction_at"),
    )
    .withColumn(
        "source_trust",
        F.when(F.col("source_id").startswith("gutenberg-"), F.lit("public_domain"))
        .otherwise(F.lit("unknown")),
    )
    .withColumn("computed_at", F.current_timestamp())
)

source_signals.write.mode("overwrite").format("delta").saveAsTable(SOURCE_TABLE)

# COMMAND ----------

temporal_labels = ["Event", "Process", "Outcome"]
temporal_edges = ["CAUSED", "PART_OF", "RESOLVED_THROUGH", "PRODUCES"]

temporal_signals = (
    nodes.where(F.col("node.label").isin(temporal_labels))
    .groupBy("workspace_id", "source_id")
    .agg(
        F.count("*").alias("temporal_node_count"),
        F.avg(F.coalesce(F.col("node.confidence"), F.lit(0.5))).alias("avg_temporal_confidence"),
    )
    .join(
        edges.where(F.col("edge.type").isin(temporal_edges))
        .groupBy("workspace_id", "source_id")
        .agg(F.count("*").alias("temporal_edge_count")),
        ["workspace_id", "source_id"],
        "left",
    )
    .fillna({"temporal_edge_count": 0})
    .withColumn("temporal_density", F.col("temporal_edge_count") / F.greatest(F.col("temporal_node_count"), F.lit(1)))
    .withColumn("computed_at", F.current_timestamp())
)

temporal_signals.write.mode("overwrite").format("delta").saveAsTable(TEMPORAL_TABLE)

# COMMAND ----------

claim_queue = (
    edges
    .select(
        "workspace_id",
        "tenant_id",
        "source_id",
        "chunk_id",
        F.col("edge.type").alias("edge_type"),
        F.col("edge.confidence").alias("confidence"),
        F.col("edge.source_quote").alias("source_quote"),
    )
    .withColumn(
        "review_reason",
        F.when(F.col("confidence") < 0.65, F.lit("low_confidence"))
        .when(F.length("source_quote") < 8, F.lit("weak_or_missing_evidence_quote"))
        .otherwise(F.lit("sample_for_audit")),
    )
    .withColumn(
        "claim_status",
        F.when(F.col("review_reason") == "sample_for_audit", F.lit("extracted"))
        .otherwise(F.lit("candidate")),
    )
    .withColumn(
        "source_trust",
        F.when(F.col("source_id").startswith("gutenberg-"), F.lit("public_domain"))
        .otherwise(F.lit("unknown")),
    )
    .where((F.col("review_reason") != "sample_for_audit") | (F.rand() < 0.1))
    .withColumn("computed_at", F.current_timestamp())
)

claim_queue.write.mode("overwrite").format("delta").saveAsTable(CLAIM_TABLE)

display(coverage)
display(source_signals)
display(temporal_signals)
display(claim_queue.limit(50))
