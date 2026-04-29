"""Optional Databricks entry point for TACITUS core v1 raw document ingestion.

The local CLI is the MVP path. This file exists so the optional Databricks
bundle has a stable structure before we turn it into production notebooks/jobs.
"""

from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", default="dialectica")
    parser.add_argument("--schema", default="conflict_graphs")
    args = parser.parse_args()
    print(f"TODO ingest raw documents into {args.catalog}.{args.schema}.raw_documents")


if __name__ == "__main__":
    main()
