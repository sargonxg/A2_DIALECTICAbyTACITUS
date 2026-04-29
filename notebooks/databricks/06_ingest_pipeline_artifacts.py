# Databricks notebook source
"""Ingest GraphOps pipeline artifacts staged from the DIALECTICA frontend.

The frontend writes JSON artifacts under:
  /Workspace/Shared/tacitus/dialectica/artifacts/<workspace>/<case>/<artifact_type>/<artifact>.json

This notebook normalizes those artifacts into Delta tables so Databricks can
track pipeline plans, ontology profiles, block states, benchmark requirements,
and terminal agents before the graph writeback step.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pyspark.sql import Row
from pyspark.sql.functions import col

dbutils.widgets.text("catalog", "dialectica")
dbutils.widgets.text("schema", "conflict_graphs")
dbutils.widgets.text("artifact_root", "/Workspace/Shared/tacitus/dialectica/artifacts")
dbutils.widgets.text("workspace_id", "")

CATALOG = dbutils.widgets.get("catalog").strip()
SCHEMA = dbutils.widgets.get("schema").strip()
ARTIFACT_ROOT = dbutils.widgets.get("artifact_root").strip()
WORKSPACE_FILTER = dbutils.widgets.get("workspace_id").strip()

spark.sql(f"CREATE CATALOG IF NOT EXISTS {CATALOG}")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}")


def iter_json_files(root: str):
    path = Path(root)
    if not path.exists():
        return
    for current_root, _, files in os.walk(path):
        for file_name in files:
            if file_name.endswith(".json"):
                yield Path(current_root) / file_name


def as_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


now = datetime.now(timezone.utc).isoformat()
pipeline_rows = []
block_rows = []
ontology_rows = []
benchmark_rows = []
agent_rows = []

for artifact_path in iter_json_files(ARTIFACT_ROOT) or []:
    try:
        raw_text = artifact_path.read_text(encoding="utf-8").strip()
        if not raw_text:
            print(f"Skipping empty artifact: {artifact_path}")
            continue
        artifact = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        print(f"Skipping invalid JSON artifact {artifact_path}: {exc}")
        continue

    workspace_id = str(artifact.get("workspace_id", ""))
    if WORKSPACE_FILTER and workspace_id != WORKSPACE_FILTER:
        continue

    case_id = str(artifact.get("case_id", ""))
    pipeline_id = str(artifact.get("pipeline_id", artifact_path.stem))
    ontology_profile = artifact.get("ontology_profile") or {}

    pipeline_rows.append(
        Row(
            pipeline_id=pipeline_id,
            workspace_id=workspace_id,
            case_id=case_id,
            case_name=str(artifact.get("case_name", "")),
            backend_mode=str(artifact.get("backend_mode", "")),
            objective=str(artifact.get("objective", "")),
            artifact_path=str(artifact_path),
            graph_layers=as_json(artifact.get("graph_layers", [])),
            created_at=str(artifact.get("created_at", "")),
            ingested_at=now,
            raw_json=as_json(artifact),
        )
    )

    ontology_rows.append(
        Row(
            pipeline_id=pipeline_id,
            workspace_id=workspace_id,
            case_id=case_id,
            ontology_profile_id=str(ontology_profile.get("id", "")),
            label=str(ontology_profile.get("label", "")),
            objective=str(ontology_profile.get("objective", "")),
            required_nodes=as_json(ontology_profile.get("required_nodes", [])),
            required_edges=as_json(ontology_profile.get("required_edges", [])),
            custom_mappings=as_json(ontology_profile.get("custom_mappings", [])),
            schema_validation_status=str(ontology_profile.get("schema_validation_status", "")),
            ingested_at=now,
        )
    )

    for block in artifact.get("blocks", []):
        block_rows.append(
            Row(
                pipeline_id=pipeline_id,
                workspace_id=workspace_id,
                case_id=case_id,
                block_id=str(block.get("id", "")),
                block_order=int(block.get("order", 0)),
                stage=str(block.get("stage", "")),
                name=str(block.get("name", "")),
                status=str(block.get("status", "")),
                backend=str(block.get("backend", "")),
                description=str(block.get("description", "")),
                ingested_at=now,
            )
        )

    for benchmark in artifact.get("benchmark_blocks", []):
        benchmark_rows.append(
            Row(
                pipeline_id=pipeline_id,
                workspace_id=workspace_id,
                case_id=case_id,
                benchmark_id=str(benchmark.get("id", "")),
                name=str(benchmark.get("name", "")),
                metric=str(benchmark.get("metric", "")),
                applies_to=str(benchmark.get("appliesTo", "")),
                ingested_at=now,
            )
        )

    for agent in artifact.get("terminal_agents", []):
        agent_rows.append(
            Row(
                pipeline_id=pipeline_id,
                workspace_id=workspace_id,
                case_id=case_id,
                agent_name=str(agent),
                status="planned",
                ingested_at=now,
            )
        )


def write_rows(rows: list[Row], table_name: str):
    if not rows:
        print(f"No rows for {table_name}")
        return
    frame = spark.createDataFrame(rows).dropDuplicates()
    (
        frame.write.mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(f"{CATALOG}.{SCHEMA}.{table_name}")
    )
    print(f"Wrote {frame.count()} rows to {CATALOG}.{SCHEMA}.{table_name}")


write_rows(pipeline_rows, "pipeline_plans")
write_rows(block_rows, "pipeline_blocks")
write_rows(ontology_rows, "pipeline_ontology_profiles")
write_rows(benchmark_rows, "pipeline_benchmark_blocks")
write_rows(agent_rows, "pipeline_terminal_agents")

if pipeline_rows:
    display(
        spark.table(f"{CATALOG}.{SCHEMA}.pipeline_plans")
        .select("pipeline_id", "workspace_id", "case_id", "backend_mode", "objective", "ingested_at")
        .orderBy(col("ingested_at").desc())
    )
