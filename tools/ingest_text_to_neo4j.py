"""Extract a DIALECTICA graph from plain text and write it to Neo4j.

This is the beginner terminal path:
raw .txt -> Gemini JSON extraction -> Neo4j graph -> Databricks mirror job.

Required env vars, or enter when prompted:
    GEMINI_API_KEY
    NEO4J_URI
    NEO4J_USER
    NEO4J_PASSWORD
    NEO4J_DATABASE

Example:
    uv run python tools/ingest_text_to_neo4j.py data/raw/romeo_juliet_act1.txt --workspace-id ws_romeo_act1
"""

from __future__ import annotations

import argparse
import getpass
import json
import os
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from google import genai
from google.genai import types
from neo4j import GraphDatabase

NODE_LABELS = {
    "Actor",
    "Conflict",
    "Event",
    "Issue",
    "Interest",
    "Norm",
    "Process",
    "Outcome",
    "Narrative",
    "PowerDynamic",
    "EmotionalState",
    "TrustState",
    "Location",
    "Evidence",
    "Role",
}

EDGE_TYPES = {
    "PARTY_TO",
    "PARTICIPATES_IN",
    "HAS_INTEREST",
    "PART_OF",
    "CAUSED",
    "AT_LOCATION",
    "WITHIN",
    "GOVERNED_BY",
    "VIOLATES",
    "RESOLVED_THROUGH",
    "PRODUCES",
    "ALLIED_WITH",
    "OPPOSED_TO",
    "HAS_POWER_OVER",
    "MEMBER_OF",
    "EXPERIENCES",
    "TRUSTS",
    "PROMOTES",
    "ABOUT",
    "EVIDENCED_BY",
}


def env_or_prompt(name: str, prompt: str, secret: bool = False, default: str = "") -> str:
    value = os.getenv(name, "")
    if value:
        return value
    if default:
        entered = getpass.getpass(f"{prompt} [{default}]: ") if secret else input(f"{prompt} [{default}]: ")
        return entered or default
    return getpass.getpass(f"{prompt}: ") if secret else input(f"{prompt}: ")


def safe_id(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9_]+", "_", value.lower()).strip("_")
    return value[:80] or "item"


def validate_label(label: str) -> str:
    if label not in NODE_LABELS:
        return "Evidence"
    return label


def validate_edge_type(edge_type: str) -> str:
    if edge_type not in EDGE_TYPES:
        return "ABOUT"
    return edge_type


def extract_graph(text: str, workspace_id: str, title: str, model: str, api_key: str) -> dict[str, Any]:
    client = genai.Client(api_key=api_key)
    prompt = f"""
Extract a DIALECTICA conflict graph from this text.

Return JSON only with this shape:
{{
  "nodes": [
    {{
      "temp_id": "short_unique_id",
      "label": "Actor|Conflict|Event|Issue|Interest|Norm|Process|Outcome|Narrative|PowerDynamic|EmotionalState|TrustState|Location|Evidence|Role",
      "name": "human readable name",
      "summary": "one sentence",
      "confidence": 0.0,
      "source_quote": "short quote under 20 words"
    }}
  ],
  "edges": [
    {{
      "source": "temp_id",
      "target": "temp_id",
      "type": "PARTY_TO|PARTICIPATES_IN|HAS_INTEREST|PART_OF|CAUSED|AT_LOCATION|WITHIN|GOVERNED_BY|VIOLATES|RESOLVED_THROUGH|PRODUCES|ALLIED_WITH|OPPOSED_TO|HAS_POWER_OVER|MEMBER_OF|EXPERIENCES|TRUSTS|PROMOTES|ABOUT|EVIDENCED_BY",
      "confidence": 0.0,
      "rationale": "short reason"
    }}
  ]
}}

Rules:
- Prefer fewer, higher-confidence nodes.
- Preserve ambiguity by using confidence below 0.7 when inferred.
- Include Evidence nodes for important source quotes.
- Do not invent facts outside the text.
- Use temp_id values that edges can reference.

Title: {title}
Workspace: {workspace_id}

Text:
{text}
"""
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1,
        ),
    )
    return json.loads(response.text)


def write_graph(graph: dict[str, Any], workspace_id: str, tenant_id: str) -> dict[str, int]:
    uri = env_or_prompt("NEO4J_URI", "Neo4j URI")
    user = env_or_prompt("NEO4J_USER", "Neo4j user", default="neo4j")
    password = env_or_prompt("NEO4J_PASSWORD", "Neo4j password", secret=True)
    database = env_or_prompt("NEO4J_DATABASE", "Neo4j database", default="neo4j")
    now = datetime.now(UTC).isoformat()

    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    id_map: dict[str, str] = {}

    with GraphDatabase.driver(uri, auth=(user, password)) as driver:
        driver.verify_connectivity()
        with driver.session(database=database) as session:
            for raw in nodes:
                temp_id = str(raw.get("temp_id") or raw.get("name") or "node")
                label = validate_label(str(raw.get("label", "Evidence")))
                node_id = f"{workspace_id}_{label.lower()}_{safe_id(temp_id)}"
                id_map[temp_id] = node_id
                props = {
                    "id": node_id,
                    "label": label,
                    "name": str(raw.get("name", temp_id)),
                    "summary": str(raw.get("summary", "")),
                    "confidence": float(raw.get("confidence", 0.5) or 0.5),
                    "source_quote": str(raw.get("source_quote", "")),
                    "workspace_id": workspace_id,
                    "tenant_id": tenant_id,
                    "created_at": now,
                    "updated_at": now,
                    "source": "tools/ingest_text_to_neo4j.py",
                }
                session.run(
                    f"MERGE (n:ConflictNode:{label} {{id: $id}}) SET n += $props",
                    id=node_id,
                    props=props,
                )

            written_edges = 0
            for index, raw in enumerate(edges):
                source = id_map.get(str(raw.get("source", "")))
                target = id_map.get(str(raw.get("target", "")))
                if not source or not target or source == target:
                    continue
                edge_type = validate_edge_type(str(raw.get("type", "ABOUT")))
                edge_id = f"{workspace_id}_edge_{index}_{safe_id(edge_type)}"
                props = {
                    "id": edge_id,
                    "type": edge_type,
                    "workspace_id": workspace_id,
                    "tenant_id": tenant_id,
                    "confidence": float(raw.get("confidence", 0.5) or 0.5),
                    "weight": float(raw.get("confidence", 0.5) or 0.5),
                    "rationale": str(raw.get("rationale", "")),
                    "created_at": now,
                    "source": "tools/ingest_text_to_neo4j.py",
                }
                session.run(
                    (
                        "MATCH (s:ConflictNode {id: $source_id, workspace_id: $workspace_id}) "
                        "MATCH (t:ConflictNode {id: $target_id, workspace_id: $workspace_id}) "
                        f"MERGE (s)-[r:{edge_type} {{id: $edge_id}}]->(t) "
                        "SET r += $props"
                    ),
                    source_id=source,
                    target_id=target,
                    workspace_id=workspace_id,
                    edge_id=edge_id,
                    props=props,
                )
                written_edges += 1

    return {"nodes": len(nodes), "edges": written_edges}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("text_file")
    parser.add_argument("--workspace-id", required=True)
    parser.add_argument("--tenant-id", default="default")
    parser.add_argument("--title", default="")
    parser.add_argument("--model", default="gemini-2.5-flash")
    parser.add_argument("--max-chars", type=int, default=12000)
    parser.add_argument("--out", default="")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    path = Path(args.text_file)
    text = path.read_text(encoding="utf-8", errors="ignore")
    if args.max_chars > 0:
        text = text[: args.max_chars]

    api_key = env_or_prompt("GEMINI_API_KEY", "Gemini API key", secret=True)
    title = args.title or path.stem
    graph = extract_graph(text, args.workspace_id, title, args.model, api_key)

    out = Path(args.out or f"data/extracted/{args.workspace_id}.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(graph, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote extraction JSON to {out}")

    if args.dry_run:
        print("Dry run only; Neo4j was not modified.")
        return

    counts = write_graph(graph, args.workspace_id, args.tenant_id)
    print(f"Wrote {counts['nodes']} nodes and {counts['edges']} edges to Neo4j")


if __name__ == "__main__":
    main()
