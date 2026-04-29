"""Tiny Neo4j Cypher CLI for DIALECTICA.

This is a Python-driver fallback for Windows terminals where cypher-shell is
not installed yet.

Examples:
    uv run python tools/neo4j_cypher.py "MATCH (n) RETURN labels(n), count(*) LIMIT 10"
    uv run python tools/neo4j_cypher.py --file query.cypher
"""

from __future__ import annotations

import argparse
import getpass
import json
import os
from pathlib import Path
from typing import Any

from neo4j import GraphDatabase


def env_or_prompt(name: str, prompt: str, secret: bool = False, default: str = "") -> str:
    value = os.getenv(name, "")
    if value:
        return value
    if default:
        entered = getpass.getpass(f"{prompt} [{default}]: ") if secret else input(f"{prompt} [{default}]: ")
        return entered or default
    return getpass.getpass(f"{prompt}: ") if secret else input(f"{prompt}: ")


def normalize(value: Any) -> Any:
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: normalize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [normalize(v) for v in value]
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("query", nargs="?", help="Cypher query to run")
    parser.add_argument("--file", help="Read Cypher from file")
    parser.add_argument("--params", default="{}", help="JSON query parameters")
    parser.add_argument("--limit", type=int, default=50, help="Display row limit")
    args = parser.parse_args()

    if args.file:
        query = Path(args.file).read_text(encoding="utf-8")
    elif args.query:
        query = args.query
    else:
        raise SystemExit("Provide a Cypher query or --file.")

    uri = env_or_prompt("NEO4J_URI", "Neo4j URI")
    user = env_or_prompt("NEO4J_USER", "Neo4j user", default="neo4j")
    password = env_or_prompt("NEO4J_PASSWORD", "Neo4j password", secret=True)
    database = env_or_prompt("NEO4J_DATABASE", "Neo4j database", default="neo4j")
    params = json.loads(args.params)

    with GraphDatabase.driver(uri, auth=(user, password)) as driver:
        driver.verify_connectivity()
        with driver.session(database=database) as session:
            records = session.run(query, **params)
            count = 0
            for record in records:
                print(json.dumps(normalize(record.data()), ensure_ascii=False, indent=2))
                count += 1
                if count >= args.limit:
                    break
            print(f"Rows shown: {count}")


if __name__ == "__main__":
    main()
