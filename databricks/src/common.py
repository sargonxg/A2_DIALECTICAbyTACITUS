"""Shared helpers for optional Databricks GraphOps jobs."""

from __future__ import annotations

from contextlib import suppress
from datetime import UTC, datetime
from typing import Any


def get_spark() -> Any:
    try:
        from pyspark.sql import SparkSession
    except ImportError as exc:
        raise SystemExit(
            "This entrypoint is intended for Databricks or a PySpark environment. "
            "Install pyspark locally only if you need to dry-run the bundle scripts."
        ) from exc
    return SparkSession.builder.getOrCreate()


def quote_name(value: str) -> str:
    return f"`{value.replace('`', '``')}`"


def table_name(catalog: str, schema: str, table: str) -> str:
    return ".".join([quote_name(catalog), quote_name(schema), quote_name(table)])


def ensure_schema(spark: Any, catalog: str, schema: str) -> None:
    with suppress(Exception):
        spark.sql(f"CREATE CATALOG IF NOT EXISTS {quote_name(catalog)}")
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {quote_name(catalog)}.{quote_name(schema)}")


def now_iso() -> str:
    return datetime.now(UTC).isoformat()
