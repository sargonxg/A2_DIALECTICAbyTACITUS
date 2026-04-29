"""Optional Databricks entry point for syncing graph-ready records to Neo4j."""

from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", default="dialectica")
    parser.add_argument("--schema", default="conflict_graphs")
    args = parser.parse_args()
    print(f"TODO sync {args.catalog}.{args.schema}.graph_ready_* records to Neo4j")


if __name__ == "__main__":
    main()
