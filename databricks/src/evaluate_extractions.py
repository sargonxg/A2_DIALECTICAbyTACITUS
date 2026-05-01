"""Databricks entry point for extraction quality and benchmark scoring."""

from __future__ import annotations

import argparse

from common import ensure_schema, get_spark, now_iso, table_name
from pyspark.sql import functions as fn


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", default="dialectica")
    parser.add_argument("--schema", default="conflict_graphs")
    args = parser.parse_args()

    spark = get_spark()
    ensure_schema(spark, args.catalog, args.schema)

    nodes = spark.table(table_name(args.catalog, args.schema, "graph_ready_nodes"))
    quality = (
        nodes.groupBy("workspace_id", "case_id", "extraction_run_id")
        .agg(
            fn.count("*").alias("primitive_count"),
            fn.countDistinct("primitive_type").alias("primitive_type_count"),
            fn.avg("confidence").alias("avg_confidence"),
            fn.sum(fn.when(fn.col("primitive_type") == "SourceDocument", 1).otherwise(0)).alias(
                "source_documents"
            ),
            fn.sum(fn.when(fn.col("primitive_type") == "SourceChunk", 1).otherwise(0)).alias(
                "source_chunks"
            ),
        )
        .withColumn(
            "coverage_status",
            fn.when(
                (fn.col("source_documents") > 0) & (fn.col("source_chunks") > 0),
                fn.lit("ready"),
            ).otherwise(fn.lit("needs_review")),
        )
        .withColumn("evaluated_at", fn.lit(now_iso()))
    )
    quality.write.mode("overwrite").format("delta").saveAsTable(
        table_name(args.catalog, args.schema, "extraction_quality")
    )

    print(
        f"Wrote {quality.count()} extraction quality row(s) to "
        f"{args.catalog}.{args.schema}.extraction_quality."
    )


if __name__ == "__main__":
    main()
