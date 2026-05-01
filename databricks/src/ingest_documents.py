"""Databricks entry point for staged GraphOps source/artifact ingestion."""

from __future__ import annotations

import argparse
from typing import Any

from common import ensure_schema, get_spark, now_iso, table_name
from pyspark.sql import functions as fn
from pyspark.sql.types import StringType, StructField, StructType


def read_json_or_empty(spark: Any, path: str, schema: StructType) -> Any:
    try:
        return spark.read.option("recursiveFileLookup", "true").json(path)
    except Exception:
        return spark.createDataFrame([], schema)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", default="dialectica")
    parser.add_argument("--schema", default="conflict_graphs")
    parser.add_argument("--input-path", default="dbfs:/FileStore/tacitus/dialectica/uploads")
    parser.add_argument("--artifact-path", default="dbfs:/FileStore/tacitus/dialectica/artifacts")
    args = parser.parse_args()

    spark = get_spark()
    ensure_schema(spark, args.catalog, args.schema)

    upload_schema = StructType(
        [
            StructField("kind", StringType()),
            StructField("workspace_id", StringType()),
            StructField("case_id", StringType()),
            StructField("extraction_run_id", StringType()),
            StructField("source_title", StringType()),
            StructField("source_type", StringType()),
            StructField("objective", StringType()),
            StructField("ontology_profile", StringType()),
            StructField("text", StringType()),
            StructField("staged_at", StringType()),
        ]
    )
    artifact_schema = StructType(
        [
            StructField("kind", StringType()),
            StructField("workspace_id", StringType()),
            StructField("case_id", StringType()),
            StructField("extraction_run_id", StringType()),
        ]
    )

    raw_documents = (
        read_json_or_empty(spark, args.input_path, upload_schema)
        .withColumn("ingested_at", fn.lit(now_iso()))
        .withColumn("source_path", fn.input_file_name())
    )
    rule_artifacts = (
        read_json_or_empty(spark, args.artifact_path, artifact_schema)
        .withColumn("ingested_at", fn.lit(now_iso()))
        .withColumn("source_path", fn.input_file_name())
    )

    raw_documents.write.mode("append").format("delta").saveAsTable(
        table_name(args.catalog, args.schema, "raw_documents")
    )
    rule_artifacts.write.mode("append").format("delta").saveAsTable(
        table_name(args.catalog, args.schema, "rule_evaluation_artifacts")
    )

    print(
        "Ingested staged GraphOps uploads/artifacts into "
        f"{args.catalog}.{args.schema}: "
        f"{raw_documents.count()} raw document row(s), "
        f"{rule_artifacts.count()} rule artifact row(s)."
    )


if __name__ == "__main__":
    main()
