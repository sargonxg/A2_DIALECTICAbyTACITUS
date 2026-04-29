"""Apply DIALECTICA Neo4j constraints and indexes from a Cypher file."""

from __future__ import annotations

import argparse
import getpass
import os
from pathlib import Path

from neo4j import GraphDatabase


def split_statements(cypher: str) -> list[str]:
    statements: list[str] = []
    buffer: list[str] = []
    for line in cypher.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("//"):
            continue
        buffer.append(line)
        if stripped.endswith(";"):
            statement = "\n".join(buffer).strip().rstrip(";").strip()
            if statement:
                statements.append(statement)
            buffer = []
    if buffer:
        statement = "\n".join(buffer).strip().rstrip(";").strip()
        if statement:
            statements.append(statement)
    return statements


def env_or_prompt(name: str, prompt: str, secret: bool = False) -> str:
    value = os.getenv(name)
    if value:
        return value
    if secret:
        return getpass.getpass(prompt)
    return input(prompt)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--schema",
        default="infrastructure/neo4j/dialectica_constraints.cypher",
        help="Cypher schema file to apply.",
    )
    args = parser.parse_args()

    uri = env_or_prompt("NEO4J_URI", "Neo4j URI: ")
    user = os.getenv("NEO4J_USERNAME") or os.getenv("NEO4J_USER") or input("Neo4j user: ")
    password = env_or_prompt("NEO4J_PASSWORD", "Neo4j password: ", secret=True)
    database = os.getenv("NEO4J_DATABASE", "neo4j")

    schema_path = Path(args.schema)
    statements = split_statements(schema_path.read_text(encoding="utf-8"))

    with GraphDatabase.driver(uri, auth=(user, password)) as driver:
        with driver.session(database=database) as session:
            for statement in statements:
                session.run(statement).consume()
                print(f"applied: {statement.splitlines()[0]}")

    print(f"Applied {len(statements)} schema statements to database '{database}'.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
