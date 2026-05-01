"""Databricks entry point for syncing graph-ready Delta rows to Neo4j."""

from __future__ import annotations

import argparse
import os

from common import ensure_schema, get_spark, table_name


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", default="dialectica")
    parser.add_argument("--schema", default="conflict_graphs")
    parser.add_argument("--limit", type=int, default=5000)
    args = parser.parse_args()

    uri = os.getenv("NEO4J_URI")
    username = os.getenv("NEO4J_USERNAME") or os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")
    database = os.getenv("NEO4J_DATABASE", "neo4j")
    if not uri or not username or not password:
        print(
            "Neo4j sync skipped: NEO4J_URI, NEO4J_USERNAME/NEO4J_USER, "
            "and NEO4J_PASSWORD are required."
        )
        return

    try:
        from neo4j import GraphDatabase
    except ImportError as exc:
        raise SystemExit(
            "Install the neo4j Python package on the Databricks cluster to sync graph rows."
        ) from exc

    spark = get_spark()
    ensure_schema(spark, args.catalog, args.schema)
    rows = (
        spark.table(table_name(args.catalog, args.schema, "graph_ready_nodes"))
        .limit(args.limit)
        .collect()
    )

    driver = GraphDatabase.driver(uri, auth=(username, password))
    try:
        with driver.session(database=database) as session:
            session.run(
                "CREATE CONSTRAINT tacitus_core_v1_id IF NOT EXISTS "
                "FOR (n:TacitusCoreV1) REQUIRE n.id IS UNIQUE"
            )
            for row in rows:
                props = {
                    key: value
                    for key, value in row.asDict(recursive=True).items()
                    if value is not None
                }
                label = "".join(
                    ch
                    for ch in str(props.get("primitive_type", "Primitive"))
                    if ch.isalnum() or ch == "_"
                )
                label = label or "Primitive"
                session.run(
                    f"MERGE (n:TacitusCoreV1:{label} {{id: $id}}) "
                    "SET n += $props, n.updated_at = datetime()",
                    id=props["id"],
                    props=props,
                )
    finally:
        driver.close()

    print(f"Synced {len(rows)} graph-ready node row(s) from {args.catalog}.{args.schema} to Neo4j.")


if __name__ == "__main__":
    main()
