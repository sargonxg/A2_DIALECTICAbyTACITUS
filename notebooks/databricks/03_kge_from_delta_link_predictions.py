# Databricks notebook source
# MAGIC %md
# MAGIC # DIALECTICA KGE link prediction from Delta triples
# MAGIC
# MAGIC Trains a small PyKEEN model from `edges_bronze` and writes candidate links to a Delta table.
# MAGIC Keep candidates separate from the authoritative graph until a human validates them.

# COMMAND ----------

# MAGIC %pip install pykeen

# COMMAND ----------

import uuid
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from pyspark.sql import functions as F


dbutils.widgets.text("catalog", "dialectica")
dbutils.widgets.text("schema", "conflict_graphs")
dbutils.widgets.text("workspace_id", "")
dbutils.widgets.dropdown("model", "TransE", ["TransE", "RotatE"])
dbutils.widgets.text("epochs", "25")
dbutils.widgets.text("embedding_dim", "64")
dbutils.widgets.text("top_k_per_query", "10")
dbutils.widgets.text("max_training_edges", "5000")

CATALOG = dbutils.widgets.get("catalog")
SCHEMA = dbutils.widgets.get("schema")
WORKSPACE_ID = dbutils.widgets.get("workspace_id").strip()
MODEL = dbutils.widgets.get("model")
EPOCHS = int(dbutils.widgets.get("epochs"))
EMBEDDING_DIM = int(dbutils.widgets.get("embedding_dim"))
TOP_K = int(dbutils.widgets.get("top_k_per_query"))
MAX_TRAINING_EDGES = int(dbutils.widgets.get("max_training_edges"))

EDGE_TABLE = f"{CATALOG}.{SCHEMA}.edges_bronze"
PREDICTION_TABLE = f"{CATALOG}.{SCHEMA}.kge_link_candidates"

# COMMAND ----------

edges = spark.table(EDGE_TABLE).select("workspace_id", "source_id", "type", "target_id").dropna()
if WORKSPACE_ID:
    edges = edges.filter(F.col("workspace_id") == WORKSPACE_ID)

training_edges = (
    edges.dropDuplicates(["source_id", "type", "target_id"])
    .orderBy(F.rand(seed=42))
    .limit(MAX_TRAINING_EDGES)
)

triples_pdf = training_edges.select("source_id", "type", "target_id").toPandas()
if len(triples_pdf) < 20:
    raise ValueError("Need at least 20 graph edges before KGE training is useful.")

labeled_triples = triples_pdf[["source_id", "type", "target_id"]].astype(str).to_numpy(dtype=str)
print(f"Training {MODEL} on {len(labeled_triples)} triples")

# COMMAND ----------

from pykeen.pipeline import pipeline
from pykeen.predict import predict_target
from pykeen.triples import TriplesFactory

factory = TriplesFactory.from_labeled_triples(labeled_triples)

result = pipeline(
    training=factory,
    model=MODEL,
    model_kwargs={"embedding_dim": EMBEDDING_DIM},
    training_kwargs={"num_epochs": EPOCHS, "batch_size": 256},
    random_seed=42,
)

print("KGE training finished.")

# COMMAND ----------

candidate_queries = (
    training_edges.groupBy("source_id", "type")
    .count()
    .orderBy(F.desc("count"))
    .limit(50)
    .toPandas()
)

known = set(map(tuple, triples_pdf[["source_id", "type", "target_id"]].astype(str).values.tolist()))
rows = []
run_id = str(uuid.uuid4())
computed_at = datetime.now(timezone.utc).isoformat()

for _, query in candidate_queries.iterrows():
    head = str(query["source_id"])
    relation = str(query["type"])
    try:
        predictions = predict_target(
            model=result.model,
            head=head,
            relation=relation,
            triples_factory=result.training,
        )
        pred_df = predictions.df.head(TOP_K * 3)
    except Exception as exc:
        print(f"Skipping {head} / {relation}: {exc}")
        continue

    for _, pred in pred_df.iterrows():
        tail = str(pred.get("tail_label") or pred.get("tail_id") or "")
        score = float(pred["score"])
        if not tail or (head, relation, tail) in known:
            continue
        rows.append(
            {
                "run_id": run_id,
                "workspace_id": WORKSPACE_ID or "all",
                "head_id": head,
                "relation": relation,
                "tail_id": tail,
                "score": score,
                "model": MODEL,
                "epochs": EPOCHS,
                "embedding_dim": EMBEDDING_DIM,
                "source": "databricks_pykeen",
                "human_validated": False,
                "computed_at": computed_at,
            }
        )
        if len([r for r in rows if r["head_id"] == head and r["relation"] == relation]) >= TOP_K:
            break

if not rows:
    raise ValueError("KGE produced no novel candidate links.")

predictions_df = spark.createDataFrame(pd.DataFrame(rows))
predictions_df.write.mode("append").saveAsTable(PREDICTION_TABLE)

display(predictions_df.orderBy(F.desc("score")))

# COMMAND ----------

display(
    spark.table(PREDICTION_TABLE)
    .groupBy("workspace_id", "relation", "human_validated")
    .count()
    .orderBy(F.desc("count"))
)
