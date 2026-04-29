"""Command line interface for the TACITUS core v1 local graph pipeline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from dialectica.graph.memory_adapter import MemoryGraphAdapter
from dialectica.graph.neo4j_adapter import Neo4jAdapter
from dialectica.ingestion.pipeline import ingest_path
from dialectica.ingestion.write_graph import write_graph, write_jsonl


def _adapter(name: str) -> MemoryGraphAdapter | Neo4jAdapter:
    if name == "memory":
        return MemoryGraphAdapter()
    if name == "neo4j":
        return Neo4jAdapter()
    raise ValueError(f"Unknown graph backend: {name}")


def _cmd_ingest(args: argparse.Namespace) -> int:
    primitives = ingest_path(
        args.path,
        workspace_id=args.workspace_id,
        case_id=args.case_id,
        chunk_chars=args.chunk_chars,
    )
    out = Path(args.out)
    write_jsonl(out, primitives)
    print(f"extracted={len(primitives)}")
    print(f"jsonl={out}")

    if not args.dry_run:
        adapter = _adapter(args.backend)
        try:
            ids = write_graph(adapter, primitives)
            print(f"written={len(ids)} backend={args.backend}")
        finally:
            adapter.close()
    return 0


def _cmd_graph_init(args: argparse.Namespace) -> int:
    adapter = _adapter(args.backend)
    try:
        adapter.initialize_schema()
    finally:
        adapter.close()
    print(f"graph initialized backend={args.backend}")
    return 0


def _cmd_graph_query(args: argparse.Namespace) -> int:
    adapter = _adapter(args.backend)
    try:
        records = adapter.query(args.question, args.workspace_id, args.case_id)
    finally:
        adapter.close()
    print(json.dumps(records, indent=2, default=str))
    return 0


def _cmd_graph_episodes(args: argparse.Namespace) -> int:
    adapter = _adapter(args.backend)
    try:
        records = adapter.episodes(args.workspace_id, args.case_id)
    finally:
        adapter.close()
    print(json.dumps(records, indent=2, default=str))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dialectica")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest = subparsers.add_parser("ingest", help="Ingest local documents into TACITUS primitives")
    ingest.add_argument("path")
    ingest.add_argument("--workspace-id", default="local-workspace")
    ingest.add_argument("--case-id", default="demo")
    ingest.add_argument("--backend", choices=["memory", "neo4j"], default="memory")
    ingest.add_argument("--chunk-chars", type=int, default=1800)
    ingest.add_argument("--out", default=".dialectica/runs/latest.jsonl")
    ingest.add_argument("--dry-run", action="store_true")
    ingest.set_defaults(func=_cmd_ingest)

    graph = subparsers.add_parser("graph", help="Graph operations")
    graph_subparsers = graph.add_subparsers(dest="graph_command", required=True)

    graph_init = graph_subparsers.add_parser("init", help="Initialize graph schema")
    graph_init.add_argument("--backend", choices=["memory", "neo4j"], default="neo4j")
    graph_init.set_defaults(func=_cmd_graph_init)

    graph_query = graph_subparsers.add_parser("query", help="Run an allowlisted graph query")
    graph_query.add_argument("question")
    graph_query.add_argument("--workspace-id", default="local-workspace")
    graph_query.add_argument("--case-id", default="demo")
    graph_query.add_argument("--backend", choices=["memory", "neo4j"], default="neo4j")
    graph_query.set_defaults(func=_cmd_graph_query)

    graph_episodes = graph_subparsers.add_parser("episodes", help="List episodes")
    graph_episodes.add_argument("--workspace-id", default="local-workspace")
    graph_episodes.add_argument("--case-id", default="demo")
    graph_episodes.add_argument("--backend", choices=["memory", "neo4j"], default="neo4j")
    graph_episodes.set_defaults(func=_cmd_graph_episodes)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
