# Databricks notebook source
# MAGIC %md
# MAGIC # DIALECTICA Seed: Open Books to Raw Text Chunks
# MAGIC
# MAGIC Downloads public-domain Project Gutenberg texts and writes chunk rows for
# MAGIC AI extraction. This keeps the first experiment reproducible and open-source.

# COMMAND ----------

import re
import urllib.request
from datetime import datetime, timezone

from pyspark.sql import functions as F

dbutils.widgets.text("catalog", "dialectica")
dbutils.widgets.text("schema", "conflict_graphs")
dbutils.widgets.text("workspace_id", "books-romeo-juliet")
dbutils.widgets.text("tenant_id", "tacitus-lab")
dbutils.widgets.text("gutenberg_ids", "1513")
dbutils.widgets.text("max_chars_per_book", "80000")
dbutils.widgets.text("chunk_chars", "2500")

CATALOG = dbutils.widgets.get("catalog")
SCHEMA = dbutils.widgets.get("schema")
WORKSPACE_ID = dbutils.widgets.get("workspace_id")
TENANT_ID = dbutils.widgets.get("tenant_id")
GUTENBERG_IDS = [item.strip() for item in dbutils.widgets.get("gutenberg_ids").split(",") if item.strip()]
MAX_CHARS = int(dbutils.widgets.get("max_chars_per_book"))
CHUNK_CHARS = int(dbutils.widgets.get("chunk_chars"))

spark.sql(f"CREATE CATALOG IF NOT EXISTS {CATALOG}")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}")

RAW_TABLE = f"{CATALOG}.{SCHEMA}.raw_text_chunks"

# COMMAND ----------

def gutenberg_url(book_id: str) -> str:
    return f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt"


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_text(text: str, size: int) -> list[str]:
    chunks: list[str] = []
    cursor = 0
    while cursor < len(text):
        end = min(cursor + size, len(text))
        boundary = text.rfind("\n\n", cursor, end)
        if boundary <= cursor + 500:
            boundary = end
        chunks.append(text[cursor:boundary].strip())
        cursor = boundary
    return [chunk for chunk in chunks if len(chunk) > 120]


rows = []
for book_id in GUTENBERG_IDS:
    url = gutenberg_url(book_id)
    with urllib.request.urlopen(url, timeout=30) as response:
        raw = response.read().decode("utf-8", errors="replace")
    text = clean_text(raw[:MAX_CHARS])
    for index, chunk in enumerate(chunk_text(text, CHUNK_CHARS)):
        rows.append(
            {
                "workspace_id": WORKSPACE_ID,
                "tenant_id": TENANT_ID,
                "source_id": f"gutenberg-{book_id}",
                "source_url": url,
                "chunk_id": f"gutenberg-{book_id}-chunk-{index:04d}",
                "chunk_index": index,
                "chunk_text": chunk,
                "loaded_at": datetime.now(timezone.utc).isoformat(),
            }
        )

if not rows:
    raise ValueError("No chunks were generated.")

df = spark.createDataFrame(rows)

(
    df.dropDuplicates(["workspace_id", "source_id", "chunk_id"])
    .write
    .mode("append")
    .format("delta")
    .saveAsTable(RAW_TABLE)
)

display(spark.table(RAW_TABLE).where(F.col("workspace_id") == WORKSPACE_ID).orderBy("source_id", "chunk_index"))
