"""Databricks entry point for TACITUS primitive extraction to Delta."""

from __future__ import annotations

import argparse
from typing import Any

from common import ensure_schema, get_spark, now_iso, table_name
from pyspark.sql import functions as fn
from pyspark.sql.window import Window


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", default="dialectica")
    parser.add_argument("--schema", default="conflict_graphs")
    args = parser.parse_args()

    spark = get_spark()
    ensure_schema(spark, args.catalog, args.schema)

    raw_table = table_name(args.catalog, args.schema, "raw_documents")
    raw = spark.table(raw_table).where(fn.col("text").isNotNull() & (fn.length("text") > 0))

    base = raw.select(
        "workspace_id",
        "case_id",
        "extraction_run_id",
        fn.lit("tacitus_core_v1").alias("ontology_version"),
        fn.coalesce(fn.col("source_title"), fn.lit("Untitled source")).alias("source_title"),
        fn.coalesce(fn.col("source_type"), fn.lit("text")).alias("source_type"),
        fn.coalesce(fn.col("objective"), fn.lit("Understand the conflict")).alias("objective"),
        fn.coalesce(fn.col("ontology_profile"), fn.lit("human-friction")).alias(
            "ontology_profile"
        ),
        fn.col("text"),
    ).dropDuplicates(["workspace_id", "case_id", "extraction_run_id"])
    cleaned = base.withColumn(
        "cleaned_text",
        fn.trim(
            fn.regexp_replace(
                fn.regexp_replace(
                    "text",
                    r"(?is)\*\*\*\s*END OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*$",
                    "",
                ),
                r"(?is)^.*?\*\*\*\s*START OF (?:THE|THIS) PROJECT GUTENBERG EBOOK[^\n]*\*\*\*",
                "",
            )
        ),
    ).withColumn(
        "cleaned_text",
        fn.when(fn.length("cleaned_text") > 0, fn.col("cleaned_text")).otherwise(fn.col("text")),
    )

    source_documents = cleaned.select(
        fn.concat_ws(
            "_",
            fn.lit("doc"),
            fn.sha2(fn.concat_ws("|", "workspace_id", "case_id", "extraction_run_id"), 256),
        ).alias("id"),
        fn.lit("SourceDocument").alias("primitive_type"),
        "workspace_id",
        "case_id",
        "extraction_run_id",
        "ontology_version",
        fn.lit(1.0).alias("confidence"),
        fn.col("source_title").alias("title"),
        "source_type",
        fn.length("text").alias("original_char_count"),
        fn.length("cleaned_text").alias("cleaned_char_count"),
        fn.lit(now_iso()).alias("observed_at"),
    )
    sentence_windows = (
        cleaned.withColumn("sentence", fn.explode(fn.split("cleaned_text", r"(?<=[.!?])\s+")))
        .withColumn("sentence", fn.trim("sentence"))
        .where(fn.length("sentence") > 0)
        .withColumn(
            "sentence_index",
            fn.row_number().over(
                Window.partitionBy(
                    "workspace_id", "case_id", "extraction_run_id"
                ).orderBy(fn.monotonically_increasing_id())
            )
            - 1,
        )
        .withColumn("episode_index", fn.floor(fn.col("sentence_index") / fn.lit(5)))
    )

    source_chunks = sentence_windows.select(
        fn.concat_ws(
            "_",
            fn.lit("chunk"),
            fn.sha2(
                fn.concat_ws("|", "workspace_id", "case_id", "extraction_run_id", "sentence_index"),
                256,
            ),
        ).alias("id"),
        fn.lit("SourceChunk").alias("primitive_type"),
        "workspace_id",
        "case_id",
        "extraction_run_id",
        "ontology_version",
        fn.lit(1.0).alias("confidence"),
        fn.col("sentence").alias("text"),
        fn.col("sentence_index").alias("chunk_index"),
        fn.lit(None).cast("int").alias("start_char"),
        fn.lit(None).cast("int").alias("end_char"),
        fn.concat(fn.lit("Episode "), (fn.col("episode_index") + 1).cast("string")).alias(
            "episode_label"
        ),
        fn.lit(now_iso()).alias("observed_at"),
    )
    extraction_runs = cleaned.select(
        fn.col("extraction_run_id").alias("id"),
        fn.lit("ExtractionRun").alias("primitive_type"),
        "workspace_id",
        "case_id",
        "extraction_run_id",
        "ontology_version",
        fn.lit(1.0).alias("confidence"),
        fn.lit("databricks-delta-deterministic-extractor").alias("model_name"),
        fn.lit("rule_based_databricks").alias("extraction_method"),
        "objective",
        "ontology_profile",
        fn.lit(now_iso()).alias("observed_at"),
    )
    episodes = (
        sentence_windows.select(
            "workspace_id",
            "case_id",
            "extraction_run_id",
            "ontology_version",
            "episode_index",
        )
        .dropDuplicates(["workspace_id", "case_id", "extraction_run_id", "episode_index"])
        .select(
            fn.concat_ws(
                "_",
                fn.lit("episode"),
                fn.sha2(
                    fn.concat_ws(
                        "|", "workspace_id", "case_id", "extraction_run_id", "episode_index"
                    ),
                    256,
                ),
            ).alias("id"),
            fn.lit("Episode").alias("primitive_type"),
            "workspace_id",
            "case_id",
            "extraction_run_id",
            "ontology_version",
            fn.lit(0.86).alias("confidence"),
            fn.concat(fn.lit("Episode "), (fn.col("episode_index") + 1).cast("string")).alias(
                "name"
            ),
            fn.lit("databricks_sentence_window").alias("segmentation_reason"),
            fn.lit(now_iso()).alias("observed_at"),
        )
    )
    evidence_spans = source_chunks.select(
        fn.concat_ws(
            "_", fn.lit("span"), fn.sha2(fn.concat_ws("|", "id", fn.lit("span")), 256)
        ).alias("id"),
        fn.lit("EvidenceSpan").alias("primitive_type"),
        "workspace_id",
        "case_id",
        "extraction_run_id",
        "ontology_version",
        fn.lit(0.72).alias("confidence"),
        fn.col("id").alias("chunk_id"),
        fn.col("text").alias("provenance_span"),
        fn.lit(now_iso()).alias("observed_at"),
    )
    claim_rows = evidence_spans.select(
        fn.concat_ws(
            "_", fn.lit("claim"), fn.sha2(fn.concat_ws("|", "id", fn.lit("claim")), 256)
        ).alias("id"),
        fn.lit("Claim").alias("primitive_type"),
        "workspace_id",
        "case_id",
        "extraction_run_id",
        "ontology_version",
        fn.lit(0.64).alias("confidence"),
        fn.col("id").alias("evidence_span_id"),
        fn.col("provenance_span").alias("text"),
        fn.lit("explicit").alias("assertion_type"),
        fn.lit("extracted").alias("claim_status"),
        fn.lit(now_iso()).alias("observed_at"),
    )
    actors = evidence_spans.withColumn(
        "actor_name",
        fn.regexp_extract("provenance_span", r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})\b", 1),
    ).where(fn.length("actor_name") > 0)
    actor_rows = actors.select(
        fn.concat_ws(
            "_",
            fn.lit("actor"),
            fn.sha2(fn.concat_ws("|", "workspace_id", "case_id", "actor_name"), 256),
        ).alias("id"),
        fn.lit("Actor").alias("primitive_type"),
        "workspace_id",
        "case_id",
        "extraction_run_id",
        "ontology_version",
        fn.lit(0.7).alias("confidence"),
        fn.col("id").alias("evidence_span_id"),
        fn.col("actor_name").alias("name"),
        fn.lit("person_or_collective").alias("actor_type"),
        fn.lit(now_iso()).alias("observed_at"),
    ).dropDuplicates(["workspace_id", "case_id", "name"])

    def classified_rows(
        pattern: str, primitive_type: str, column_name: str, confidence: float
    ) -> Any:
        return evidence_spans.where(fn.col("provenance_span").rlike(pattern)).select(
            fn.concat_ws(
                "_",
                fn.lit(primitive_type.lower()),
                fn.sha2(fn.concat_ws("|", "id", fn.lit(primitive_type)), 256),
            ).alias("id"),
            fn.lit(primitive_type).alias("primitive_type"),
            "workspace_id",
            "case_id",
            "extraction_run_id",
            "ontology_version",
            fn.lit(confidence).alias("confidence"),
            fn.col("id").alias("evidence_span_id"),
            fn.col("provenance_span").alias(column_name),
            fn.lit(now_iso()).alias("observed_at"),
        )

    events = classified_rows(
        r"(?i)\b(after|then|announced|suspended|postponed|failed|meeting|fight|death|banished|warned)\b",
        "Event",
        "description",
        0.68,
    )
    constraints = classified_rows(
        r"(?i)\b(cannot|must|only after|deadline|requires|penalty|red line|"
        r"banished|law|rule|limited)\b",
        "Constraint",
        "description",
        0.72,
    )
    commitments = classified_rows(
        r"(?i)\b(agrees?|committed|promise[ds]?|pledge[ds]?|will|shall|vow)\b",
        "Commitment",
        "description",
        0.7,
    )
    narratives = classified_rows(
        r"(?i)\b(says|claims|argues|warns|honor|love|hate|feud|betray|legitimacy)\b",
        "Narrative",
        "content",
        0.66,
    )

    primitive_candidates = (
        extraction_runs.unionByName(source_documents, allowMissingColumns=True).unionByName(
            source_chunks,
            allowMissingColumns=True,
        )
        .unionByName(episodes, allowMissingColumns=True)
        .unionByName(evidence_spans, allowMissingColumns=True)
        .unionByName(claim_rows, allowMissingColumns=True)
        .unionByName(actor_rows, allowMissingColumns=True)
        .unionByName(events, allowMissingColumns=True)
        .unionByName(constraints, allowMissingColumns=True)
        .unionByName(commitments, allowMissingColumns=True)
        .unionByName(narratives, allowMissingColumns=True)
    )
    primitive_candidates.write.mode("overwrite").format("delta").saveAsTable(
        table_name(args.catalog, args.schema, "primitive_candidates")
    )
    primitive_candidates.write.mode("overwrite").format("delta").saveAsTable(
        table_name(args.catalog, args.schema, "graph_ready_nodes")
    )

    print(
        f"Extracted {primitive_candidates.count()} graph-ready primitive row(s) into "
        f"{args.catalog}.{args.schema}.primitive_candidates and graph_ready_nodes."
    )


if __name__ == "__main__":
    main()
