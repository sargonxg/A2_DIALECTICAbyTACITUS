# Databricks notebook source
# MAGIC %md
# MAGIC # DIALECTICA AI Extraction: Raw Text Chunks to Ontology Candidates
# MAGIC
# MAGIC This notebook uses Databricks AI Functions (`ai_query`) to transform raw text
# MAGIC chunks into TACITUS ontology candidates. It writes a Delta table that can be
# MAGIC reviewed, validated, and loaded into Neo4j.
# MAGIC
# MAGIC Expected input table:
# MAGIC `dialectica.conflict_graphs.raw_text_chunks`
# MAGIC
# MAGIC Required columns:
# MAGIC `workspace_id`, `tenant_id`, `source_id`, `chunk_id`, `chunk_text`

# COMMAND ----------

from pyspark.sql import functions as F

dbutils.widgets.text("catalog", "dialectica")
dbutils.widgets.text("schema", "conflict_graphs")
dbutils.widgets.text("model_endpoint", "databricks-meta-llama-3-3-70b-instruct")
dbutils.widgets.text("max_chunks", "50")

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
model_endpoint = dbutils.widgets.get("model_endpoint")
max_chunks = int(dbutils.widgets.get("max_chunks"))

spark.sql(f"CREATE CATALOG IF NOT EXISTS {catalog}")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema}")

raw_table = f"{catalog}.{schema}.raw_text_chunks"
output_table = f"{catalog}.{schema}.ai_extraction_candidates"

# COMMAND ----------

allowed_nodes = [
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
]

allowed_edges = [
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
]

system_contract = f"""
You extract conflict intelligence into the TACITUS DIALECTICA ontology.
Return strict JSON only, with this shape:
{{
  "nodes": [
    {{
      "local_id": "short stable id",
      "label": "one of {allowed_nodes}",
      "name": "short human name",
      "confidence": 0.0,
      "source_quote": "short quote from the chunk, under 20 words",
      "properties": {{}}
    }}
  ],
  "edges": [
    {{
      "type": "one of {allowed_edges}",
      "source_local_id": "local_id",
      "target_local_id": "local_id",
      "confidence": 0.0,
      "source_quote": "short quote from the chunk, under 20 words",
      "properties": {{}}
    }}
  ],
  "warnings": []
}}
Rules:
- Do not invent facts outside the chunk.
- Every edge endpoint must reference a node local_id in the same JSON.
- Prefer fewer high-confidence claims over many weak claims.
- If the chunk is not conflict-relevant, return empty nodes and edges.
"""

prompt_df = (
    spark.table(raw_table)
    .select("workspace_id", "tenant_id", "source_id", "chunk_id", "chunk_text")
    .where(F.length("chunk_text") > 80)
    .limit(max_chunks)
    .withColumn(
        "prompt",
        F.concat(
            F.lit(system_contract),
            F.lit("\n\nChunk:\n"),
            F.col("chunk_text"),
        ),
    )
)

prompt_df.createOrReplaceTempView("dialectica_ai_prompts")

# COMMAND ----------

extractions = spark.sql(
    f"""
    SELECT
      workspace_id,
      tenant_id,
      source_id,
      chunk_id,
      ai_query(
        '{model_endpoint}',
        prompt,
        modelParameters => named_struct('temperature', 0.1, 'max_tokens', 1400)
      ) AS extraction_json,
      current_timestamp() AS extracted_at,
      '{model_endpoint}' AS model_endpoint
    FROM dialectica_ai_prompts
    """
)

(
    extractions
    .withColumn("extractor", F.lit("databricks_ai_query"))
    .write
    .mode("append")
    .format("delta")
    .saveAsTable(output_table)
)

display(spark.table(output_table).orderBy(F.desc("extracted_at")).limit(20))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Next
# MAGIC
# MAGIC 1. Validate `extraction_json` against the TACITUS ontology contract.
# MAGIC 2. Convert accepted candidates into Neo4j nodes and relationships.
# MAGIC 3. Run `tacitus_operational_loop` to compute graph quality and review queues.
