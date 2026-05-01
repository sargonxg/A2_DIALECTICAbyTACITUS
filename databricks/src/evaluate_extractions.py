"""Databricks entry point for extraction quality and benchmark scoring."""

from __future__ import annotations

import argparse

from common import ensure_schema, get_spark, now_iso, table_name
from pyspark.sql import functions as fn

EXPECTED_PRIMITIVES = ("Actor", "Claim", "Event", "Constraint", "EvidenceSpan", "Episode")
CLAIM_LIKE_PRIMITIVES = ("Claim", "Event", "Constraint", "Commitment", "Narrative", "ActorState")


def text_expr() -> fn.Column:
    return fn.coalesce(
        fn.col("provenance_span"),
        fn.col("text"),
        fn.col("description"),
        fn.col("content"),
        fn.col("name"),
        fn.col("title"),
        fn.lit(""),
    )


def score_rows(benchmarks: object) -> object:
    return benchmarks.select(
        "benchmark_id",
        "workspace_id",
        "case_id",
        "extraction_run_id",
        "evaluated_at",
        fn.expr(
            """
            stack(
              7,
              'ontologyCoverage', ontology_coverage,
              'evidenceGrounding', evidence_grounding,
              'sourceGrounding', source_grounding,
              'causalDiscipline', causal_discipline,
              'ruleCompliance', rule_compliance,
              'answerUsefulness', answer_usefulness,
              'overall', overall
            ) as (metric, score)
            """
        ),
    )


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

    expected_array = fn.array(*[fn.lit(item) for item in EXPECTED_PRIMITIVES])
    type_sets = nodes.groupBy("workspace_id", "case_id", "extraction_run_id").agg(
        fn.collect_set("primitive_type").alias("primitive_types"),
        fn.sum(fn.when(fn.col("primitive_type") == "EvidenceSpan", 1).otherwise(0)).alias(
            "evidence_span_count"
        ),
        fn.sum(fn.when(fn.col("primitive_type") == "Actor", 1).otherwise(0)).alias("actor_count"),
        fn.sum(fn.when(fn.col("primitive_type") == "Event", 1).otherwise(0)).alias("event_count"),
        fn.sum(fn.when(fn.col("primitive_type") == "Constraint", 1).otherwise(0)).alias(
            "constraint_count"
        ),
    )
    claim_like = (
        nodes.where(fn.col("primitive_type").isin(*CLAIM_LIKE_PRIMITIVES))
        .groupBy("workspace_id", "case_id", "extraction_run_id")
        .agg(
            fn.count("*").alias("claim_like_count"),
            fn.sum(
                fn.when(
                    fn.col("evidence_span_id").isNotNull() | (fn.length(text_expr()) > 0),
                    1,
                ).otherwise(0)
            ).alias("grounded_claim_like_count"),
        )
    )
    diagnostics = nodes.groupBy("workspace_id", "case_id", "extraction_run_id").agg(
        fn.sum(
            fn.when(
                (fn.col("primitive_type") == "EvidenceSpan") & (fn.col("confidence") < 0.7),
                1,
            ).otherwise(0)
        ).alias("weak_evidence_count"),
        fn.sum(
            fn.when(
                text_expr().rlike(r"(?i)\b(because|caused|therefore|led to|resulted in)\b"),
                1,
            ).otherwise(0)
        ).alias("causal_cue_count"),
    )
    benchmarks = (
        quality.join(type_sets, ["workspace_id", "case_id", "extraction_run_id"], "left")
        .join(claim_like, ["workspace_id", "case_id", "extraction_run_id"], "left")
        .join(diagnostics, ["workspace_id", "case_id", "extraction_run_id"], "left")
        .fillna(
            {
                "evidence_span_count": 0,
                "actor_count": 0,
                "event_count": 0,
                "constraint_count": 0,
                "claim_like_count": 0,
                "grounded_claim_like_count": 0,
                "weak_evidence_count": 0,
                "causal_cue_count": 0,
            }
        )
        .withColumn("expected_primitive_types", expected_array)
        .withColumn(
            "missing_primitive_types",
            fn.array_except(expected_array, fn.col("primitive_types")),
        )
        .withColumn(
            "benchmark_id",
            fn.concat(
                fn.lit("bench_"),
                fn.substring(
                    fn.sha2(
                        fn.concat_ws(
                            "|",
                            "workspace_id",
                            "case_id",
                            "extraction_run_id",
                            fn.lit("databricks_extraction_readiness"),
                        ),
                        256,
                    ),
                    1,
                    16,
                ),
            ),
        )
        .withColumn(
            "ontology_coverage",
            fn.round(
                fn.size(fn.array_intersect(fn.col("primitive_types"), expected_array))
                / fn.lit(len(EXPECTED_PRIMITIVES)),
                2,
            ),
        )
        .withColumn(
            "evidence_grounding",
            fn.round(
                fn.col("grounded_claim_like_count")
                / fn.greatest(fn.col("claim_like_count"), fn.lit(1)),
                2,
            ),
        )
        .withColumn(
            "source_grounding",
            fn.when(
                (fn.col("source_documents") > 0) & (fn.col("evidence_span_count") > 0),
                fn.lit(0.75),
            ).otherwise(fn.lit(0.25)),
        )
        .withColumn(
            "causal_discipline",
            fn.when((fn.col("event_count") >= 2) & (fn.col("causal_cue_count") == 0), fn.lit(0.8))
            .when((fn.col("event_count") >= 2) & (fn.col("causal_cue_count") > 0), fn.lit(0.95))
            .otherwise(fn.lit(1.0)),
        )
        .withColumn(
            "rule_compliance",
            fn.when(fn.size(fn.col("missing_primitive_types")) > 1, fn.lit(0.7))
            .when(fn.size(fn.col("missing_primitive_types")) == 1, fn.lit(0.85))
            .otherwise(fn.lit(1.0)),
        )
        .withColumn(
            "answer_usefulness",
            fn.round(
                (
                    fn.least(fn.col("actor_count"), fn.lit(4)) / fn.lit(4) * fn.lit(0.35)
                    + fn.when(fn.col("constraint_count") > 0, fn.lit(0.25)).otherwise(fn.lit(0.0))
                    + fn.when(fn.col("event_count") > 0, fn.lit(0.25)).otherwise(fn.lit(0.0))
                    + fn.when(fn.col("evidence_span_count") > 0, fn.lit(0.15)).otherwise(
                        fn.lit(0.0)
                    )
                ),
                2,
            ),
        )
        .withColumn(
            "overall",
            fn.round(
                fn.col("ontology_coverage") * fn.lit(0.18)
                + fn.col("evidence_grounding") * fn.lit(0.22)
                + fn.col("source_grounding") * fn.lit(0.16)
                + fn.col("causal_discipline") * fn.lit(0.14)
                + fn.col("rule_compliance") * fn.lit(0.16)
                + fn.col("answer_usefulness") * fn.lit(0.14),
                2,
            ),
        )
        .withColumn("mode", fn.lit("databricks_extraction_readiness_benchmark"))
    )
    benchmark_runs = benchmarks.select(
        "benchmark_id",
        "mode",
        "workspace_id",
        "case_id",
        "extraction_run_id",
        fn.col("evaluated_at").alias("created_at"),
        fn.lit("Is this extraction ready for graph-grounded Praxis answers?").alias("question"),
        "overall",
        "ontology_coverage",
        "evidence_grounding",
        "source_grounding",
        "causal_discipline",
        "rule_compliance",
        "answer_usefulness",
    )
    benchmark_diagnostics = benchmarks.select(
        "benchmark_id",
        "workspace_id",
        "case_id",
        "extraction_run_id",
        "evaluated_at",
        "primitive_count",
        "primitive_type_count",
        "expected_primitive_types",
        "primitive_types",
        "missing_primitive_types",
        "weak_evidence_count",
        "causal_cue_count",
        "claim_like_count",
        "grounded_claim_like_count",
        fn.when(
            fn.size("missing_primitive_types") > 0,
            fn.concat(
                fn.lit("Run targeted extraction for "),
                fn.concat_ws(", ", "missing_primitive_types"),
            ),
        ).alias("ontology_recommendation"),
        fn.when(
            fn.col("evidence_grounding") < 0.85,
            fn.lit(
                "Review primitives without evidence spans before graph-grounded answer generation."
            ),
        ).alias("evidence_recommendation"),
    )
    benchmark_runs.write.mode("overwrite").format("delta").saveAsTable(
        table_name(args.catalog, args.schema, "benchmark_runs")
    )
    score_rows(benchmarks).write.mode("overwrite").format("delta").saveAsTable(
        table_name(args.catalog, args.schema, "benchmark_scores")
    )
    benchmark_diagnostics.write.mode("overwrite").format("delta").saveAsTable(
        table_name(args.catalog, args.schema, "benchmark_diagnostics")
    )

    print(
        f"Wrote {quality.count()} extraction quality row(s) to "
        f"{args.catalog}.{args.schema}.extraction_quality."
    )
    print(
        f"Wrote {benchmark_runs.count()} benchmark run(s), "
        f"{score_rows(benchmarks).count()} score row(s), and diagnostics to "
        f"{args.catalog}.{args.schema}."
    )


if __name__ == "__main__":
    main()
