# Databricks notebook source
# MAGIC %md
# MAGIC # DIALECTICA Neurosymbolic Benchmark
# MAGIC
# MAGIC Compares two answer modes:
# MAGIC
# MAGIC 1. **Baseline LLM**: answers from the raw prompt only.
# MAGIC 2. **DIALECTICA Graph-Grounded LLM**: answers with Neo4j situation graph context,
# MAGIC    TACITUS ontology constraints, and evidence-first instructions.
# MAGIC
# MAGIC This is inspired by the separate TCGC benchmark repository, but it is owned
# MAGIC by this DIALECTICA operational repo and writes results into Delta.

# COMMAND ----------

# MAGIC %pip install neo4j

# COMMAND ----------

import json
import uuid
from datetime import datetime, timezone

from neo4j import GraphDatabase
from pyspark.sql import functions as F

dbutils.widgets.text("workspace_id", "books-romeo-juliet")
dbutils.widgets.text("secret_scope", "tacitus")
dbutils.widgets.text("catalog", "dialectica")
dbutils.widgets.text("schema", "conflict_graphs")
dbutils.widgets.text("model_endpoint", "databricks-meta-llama-3-3-70b-instruct")
dbutils.widgets.text("max_graph_facts", "80")

WORKSPACE_ID = dbutils.widgets.get("workspace_id").strip()
SECRET_SCOPE = dbutils.widgets.get("secret_scope").strip()
CATALOG = dbutils.widgets.get("catalog").strip()
SCHEMA = dbutils.widgets.get("schema").strip()
MODEL_ENDPOINT = dbutils.widgets.get("model_endpoint").strip()
MAX_GRAPH_FACTS = int(dbutils.widgets.get("max_graph_facts"))

spark.sql(f"CREATE CATALOG IF NOT EXISTS {CATALOG}")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}")

ITEM_TABLE = f"{CATALOG}.{SCHEMA}.benchmark_items"
PROMPT_TABLE = f"{CATALOG}.{SCHEMA}.benchmark_prompts"
ANSWER_TABLE = f"{CATALOG}.{SCHEMA}.benchmark_answers"
JUDGE_TABLE = f"{CATALOG}.{SCHEMA}.benchmark_judgments"

RUN_ID = str(uuid.uuid4())

# COMMAND ----------

seed_items = [
    {
        "item_id": "dialectica-bench-0001",
        "domain": "workplace",
        "task_type": "commitment-tracking",
        "question": "Was there a commitment on content ownership, when was it made, and who later contested it?",
        "input_text": (
            "Mon 09:14 Sam: So we're agreed - you own the Q4 launch deck content, I handle design. "
            "Lock it in by Thursday?\n"
            "Mon 09:47 Alex: Sounds good. I'll pick it up after the Jenkins pitch.\n"
            "Thu 09:02 Alex: I never said I'd own it. Just help."
        ),
        "gold_summary": "Sam asserted Alex owned Q4 launch deck content; Alex ambiguously acknowledged; Alex later denied scope.",
    },
    {
        "item_id": "dialectica-bench-0002",
        "domain": "commercial",
        "task_type": "position-interest-separation",
        "question": "Separate the stated positions from the underlying interests.",
        "input_text": (
            "Vendor: We cannot accept any delivery after June 1. Buyer: We need guaranteed launch inventory "
            "because our retail contracts impose penalties. Vendor: The factory has limited night-shift capacity."
        ),
        "gold_summary": "Buyer position is June 1 delivery; buyer interest is avoiding retail penalties; vendor interest is capacity protection.",
    },
    {
        "item_id": "dialectica-bench-0003",
        "domain": "policy",
        "task_type": "constraint-extraction",
        "question": "What constraints shape the feasible policy options?",
        "input_text": (
            "The agency can reallocate emergency funds only after committee notice. The mayor wants immediate shelter expansion, "
            "while the finance office warns that state matching funds expire if reporting is late."
        ),
        "gold_summary": "Committee notice, emergency fund rules, state matching-fund reporting deadlines, and political urgency constrain options.",
    },
    {
        "item_id": "dialectica-bench-0004",
        "domain": "family",
        "task_type": "narrative-drift",
        "question": "How did the narrative change across the exchange?",
        "input_text": (
            "Parent: I asked you to call when plans changed. Teen: You never trust me. Parent: This is about safety, not trust. "
            "Teen: You just want control."
        ),
        "gold_summary": "The narrative drifts from coordination/safety into mistrust and control.",
    },
    {
        "item_id": "dialectica-bench-0005",
        "domain": "diplomatic",
        "task_type": "causal-chain",
        "question": "Identify the plausible escalation chain and the evidence for each step.",
        "input_text": (
            "After the inspection delay, State A suspended talks. State B announced reciprocal tariffs. "
            "Regional partners then postponed the summit, citing uncertainty."
        ),
        "gold_summary": "Inspection delay plausibly caused suspended talks, which contributed to tariffs and summit postponement.",
    },
]

seed_df = spark.createDataFrame(seed_items).withColumn("workspace_id", F.lit(WORKSPACE_ID))
seed_df.write.mode("overwrite").format("delta").saveAsTable(ITEM_TABLE)
display(seed_df)

# COMMAND ----------

graph_facts: list[str] = []
try:
    neo4j_uri = dbutils.secrets.get(SECRET_SCOPE, "neo4j-uri")
    neo4j_user = dbutils.secrets.get(SECRET_SCOPE, "neo4j-user")
    neo4j_password = dbutils.secrets.get(SECRET_SCOPE, "neo4j-password")
    neo4j_database = dbutils.secrets.get(SECRET_SCOPE, "neo4j-database")

    with GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password)) as driver:
        with driver.session(database=neo4j_database) as session:
            result = session.run(
                """
                MATCH (a:ConflictNode)-[r]->(b:ConflictNode)
                WHERE a.workspace_id = $workspace_id
                RETURN labels(a) AS source_labels, a.name AS source_name,
                       type(r) AS edge_type, labels(b) AS target_labels, b.name AS target_name,
                       r.confidence AS confidence, r.source_quote AS quote
                ORDER BY coalesce(r.confidence, 0.0) DESC
                LIMIT $limit
                """,
                workspace_id=WORKSPACE_ID,
                limit=MAX_GRAPH_FACTS,
            )
            for record in result:
                graph_facts.append(
                    f"{record['source_name']} -[{record['edge_type']} conf={record['confidence']}]-> "
                    f"{record['target_name']} | evidence: {record['quote']}"
                )
except Exception as exc:
    fallback_rows = (
        spark.table(f"{CATALOG}.{SCHEMA}.ai_extraction_candidates")
        .where(F.col("workspace_id") == WORKSPACE_ID)
        .orderBy(F.desc("extracted_at"))
        .limit(MAX_GRAPH_FACTS)
        .select("chunk_id", "extraction_json")
        .collect()
    )
    for row in fallback_rows:
        graph_facts.append(f"Delta candidate {row['chunk_id']}: {row['extraction_json'][:600]}")
    graph_facts.insert(0, f"Neo4j context unavailable; using Delta extraction candidates. Reason: {exc}")

graph_context = "\n".join(graph_facts) if graph_facts else "No Neo4j facts available yet."

# COMMAND ----------

ontology_contract = """
Use TACITUS DIALECTICA concepts: Actor, Conflict, Event, Issue, Interest, Norm,
Process, Outcome, Narrative, PowerDynamic, EmotionalState, TrustState, Location,
Evidence, Role. Prefer typed relationships such as PARTY_TO, CAUSED, HAS_INTEREST,
VIOLATES, HAS_POWER_OVER, TRUSTS, PROMOTES, EVIDENCED_BY.
"""

items = spark.table(ITEM_TABLE).where(F.col("workspace_id") == WORKSPACE_ID)

baseline_prompts = items.select(
    F.lit(RUN_ID).alias("run_id"),
    F.col("item_id"),
    F.lit("baseline_llm").alias("approach"),
    F.concat(
        F.lit("Answer the conflict-analysis question. Be concise.\n\nQuestion: "),
        F.col("question"),
        F.lit("\n\nText:\n"),
        F.col("input_text"),
    ).alias("prompt"),
)

dialectica_prompts = items.select(
    F.lit(RUN_ID).alias("run_id"),
    F.col("item_id"),
    F.lit("dialectica_graph_grounded").alias("approach"),
    F.concat(
        F.lit("Answer using the TACITUS neurosymbolic graph method.\n"),
        F.lit(ontology_contract),
        F.lit("\nReturn JSON with keys: answer, primitives, edges, provenance, uncertainty.\n"),
        F.lit("\nNeo4j graph context:\n"),
        F.lit(graph_context[:12000]),
        F.lit("\n\nQuestion: "),
        F.col("question"),
        F.lit("\n\nText:\n"),
        F.col("input_text"),
    ).alias("prompt"),
)

prompts = baseline_prompts.unionByName(dialectica_prompts)
prompts.write.mode("overwrite").format("delta").saveAsTable(PROMPT_TABLE)
prompts.createOrReplaceTempView("benchmark_prompts")

# COMMAND ----------

answers = spark.sql(
    f"""
    SELECT
      run_id,
      item_id,
      approach,
      ai_query(
        '{MODEL_ENDPOINT}',
        prompt,
        modelParameters => named_struct('temperature', 0.1, 'max_tokens', 1200)
      ) AS answer,
      current_timestamp() AS answered_at,
      '{MODEL_ENDPOINT}' AS model_endpoint
    FROM benchmark_prompts
    """
)

answers.write.mode("append").format("delta").saveAsTable(ANSWER_TABLE)
display(answers)

# COMMAND ----------

answers.createOrReplaceTempView("benchmark_answers_current")
items.select("item_id", "gold_summary").createOrReplaceTempView("benchmark_gold_current")

judge_prompts = spark.sql(
    """
    SELECT
      a.run_id,
      a.item_id,
      a.approach,
      CONCAT(
        'You are scoring conflict reasoning. Compare the answer to the gold summary. ',
        'Return strict JSON with keys graph_score, provenance_score, causal_score, notes. ',
        'Scores must be 0 to 1.\\n\\nGold: ', g.gold_summary,
        '\\n\\nAnswer: ', a.answer
      ) AS judge_prompt
    FROM benchmark_answers_current a
    JOIN benchmark_gold_current g USING (item_id)
    """
)
judge_prompts.createOrReplaceTempView("benchmark_judge_prompts")

judgments = spark.sql(
    f"""
    SELECT
      run_id,
      item_id,
      approach,
      ai_query(
        '{MODEL_ENDPOINT}',
        judge_prompt,
        modelParameters => named_struct('temperature', 0.0, 'max_tokens', 500)
      ) AS judgment_json,
      current_timestamp() AS judged_at,
      '{MODEL_ENDPOINT}' AS judge_model
    FROM benchmark_judge_prompts
    """
)

judgments.write.mode("append").format("delta").saveAsTable(JUDGE_TABLE)
display(judgments)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Inspect
# MAGIC
# MAGIC Tables:
# MAGIC
# MAGIC - `dialectica.conflict_graphs.benchmark_items`
# MAGIC - `dialectica.conflict_graphs.benchmark_prompts`
# MAGIC - `dialectica.conflict_graphs.benchmark_answers`
# MAGIC - `dialectica.conflict_graphs.benchmark_judgments`
