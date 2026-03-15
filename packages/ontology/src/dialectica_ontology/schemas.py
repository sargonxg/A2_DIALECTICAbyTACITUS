"""
DDL / Schema Generators for the DIALECTICA ontology.

Generates database schemas and serialisation formats from the canonical
Pydantic node and edge definitions:

  - generate_cypher_ddl()   -> Cypher constraints + indexes (Neo4j / FalkorDB)
  - generate_spanner_ddl()  -> Google Cloud Spanner SQL DDL
  - generate_gql_schema()   -> GQL graph schema for Spanner Graph
  - generate_json_schema()  -> Combined JSON Schema for API validation
  - generate_turtle()       -> OWL/Turtle for RDF interoperability
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, get_args, get_origin

from dialectica_ontology.primitives import (
    NODE_TYPES,
    ConflictNode,
    Actor,
    Conflict,
    Event,
    Issue,
    Interest,
    Norm,
    Process,
    Outcome,
    Narrative,
    EmotionalState,
    TrustState,
    PowerDynamic,
    Location,
    Evidence,
    Role,
)
from dialectica_ontology.relationships import EdgeType, EDGE_SCHEMA

# QuadClass is referenced by Event but not imported in primitives.py, leaving
# a dangling forward reference.  Inject it into the primitives module namespace
# so that model_rebuild() can resolve it.
from dialectica_ontology.enums import QuadClass as _QuadClass  # noqa: F401
import dialectica_ontology.primitives as _primitives_mod

if not hasattr(_primitives_mod, "QuadClass"):
    _primitives_mod.QuadClass = _QuadClass  # type: ignore[attr-defined]

Event.model_rebuild()


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

# Indexes to generate beyond the mandatory uniqueness constraint on `id`.
# Mapping: NodeTypeName -> list of (property_name,) tuples.
# Tuples with >1 element become composite indexes.
_INDEXES: dict[str, list[tuple[str, ...]]] = {
    "Actor": [
        ("name",),
        ("actor_type",),
    ],
    "Conflict": [
        ("domain",),
        ("status",),
        ("glasl_stage",),
        ("started_at",),
        ("domain", "status"),
    ],
    "Event": [
        ("event_type",),
        ("occurred_at",),
        ("severity",),
        ("event_type", "occurred_at"),
    ],
}


def _python_type_to_spanner(annotation: Any) -> str:
    """Map a Python / Pydantic type annotation to a Spanner column type."""
    origin = get_origin(annotation)

    # Handle Optional (Union[X, None])
    if origin is type(None):
        return "STRING(MAX)"
    args = get_args(annotation)
    if args and type(None) in args:
        # Unwrap Optional
        inner = [a for a in args if a is not type(None)]
        if inner:
            return _python_type_to_spanner(inner[0])

    if annotation is str or annotation == str:
        return "STRING(MAX)"
    if annotation is float or annotation == float:
        return "FLOAT64"
    if annotation is int or annotation == int:
        return "INT64"
    if annotation is bool or annotation == bool:
        return "BOOL"
    if annotation is datetime or annotation == datetime:
        return "TIMESTAMP"

    # list[X]
    if origin is list:
        inner_args = get_args(annotation)
        if inner_args:
            inner_spanner = _python_type_to_spanner(inner_args[0])
            return f"ARRAY<{inner_spanner}>"
        return "ARRAY<STRING(MAX)>"

    # dict / Any fallback -> JSON string
    if origin is dict or annotation is dict:
        return "JSON"

    # Enum subclasses -> STRING
    if isinstance(annotation, type) and issubclass(annotation, str):
        return "STRING(MAX)"

    return "STRING(MAX)"


def _get_model_fields(model_cls: type[ConflictNode]) -> list[tuple[str, Any]]:
    """Return (field_name, annotation) pairs for a Pydantic model, respecting MRO."""
    fields: list[tuple[str, Any]] = []
    seen: set[str] = set()
    for name, field_info in model_cls.model_fields.items():
        if name in seen:
            continue
        seen.add(name)
        fields.append((name, field_info.annotation))
    return fields


# ---------------------------------------------------------------------------
# 1. Cypher DDL (Neo4j / FalkorDB)
# ---------------------------------------------------------------------------

def generate_cypher_ddl() -> str:
    """Return Cypher CREATE CONSTRAINT and CREATE INDEX statements.

    Produces:
    - A uniqueness constraint on ``id`` for every node label.
    - Single-property and composite indexes as defined in ``_INDEXES``.
    """
    lines: list[str] = []

    # Uniqueness constraints
    for label in NODE_TYPES:
        lines.append(
            f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{label}) REQUIRE n.id IS UNIQUE;"
        )

    lines.append("")

    # Property indexes (single and composite)
    for label, index_defs in _INDEXES.items():
        for props in index_defs:
            prop_list = ", ".join(f"n.{p}" for p in props)
            idx_name = f"idx_{label.lower()}_{'_'.join(props)}"
            lines.append(
                f"CREATE INDEX {idx_name} IF NOT EXISTS FOR (n:{label}) ON ({prop_list});"
            )

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# 2. Google Cloud Spanner SQL DDL
# ---------------------------------------------------------------------------

def generate_spanner_ddl() -> str:
    """Return CREATE TABLE statements for Google Cloud Spanner.

    Each DIALECTICA node type becomes a table.  Column types are derived
    from the Pydantic field annotations.
    """
    statements: list[str] = []

    for label, model_cls in NODE_TYPES.items():
        cols: list[str] = []
        for name, annotation in _get_model_fields(model_cls):
            spanner_type = _python_type_to_spanner(annotation)
            cols.append(f"  {name} {spanner_type}")
        col_block = ",\n".join(cols)
        statements.append(
            f"CREATE TABLE {label} (\n{col_block}\n) PRIMARY KEY (id);"
        )

    # Edge table
    statements.append(
        "CREATE TABLE Relationship (\n"
        "  id STRING(MAX) NOT NULL,\n"
        "  type STRING(MAX) NOT NULL,\n"
        "  source_id STRING(MAX) NOT NULL,\n"
        "  target_id STRING(MAX) NOT NULL,\n"
        "  source_label STRING(MAX),\n"
        "  target_label STRING(MAX),\n"
        "  workspace_id STRING(MAX),\n"
        "  tenant_id STRING(MAX),\n"
        "  properties JSON,\n"
        "  weight FLOAT64,\n"
        "  confidence FLOAT64,\n"
        "  temporal_start TIMESTAMP,\n"
        "  temporal_end TIMESTAMP,\n"
        "  source_text STRING(MAX)\n"
        ") PRIMARY KEY (id);"
    )

    return "\n\n".join(statements) + "\n"


# ---------------------------------------------------------------------------
# 3. GQL Graph Schema (Spanner Graph)
# ---------------------------------------------------------------------------

def generate_gql_schema() -> str:
    """Return a GQL graph schema suitable for Spanner Graph.

    Defines NODE TABLE declarations for every node type and EDGE TABLE
    declarations for every edge type with KEY/SOURCE/DESTINATION references.
    """
    lines: list[str] = [
        "CREATE OR REPLACE PROPERTY GRAPH DialecticaGraph",
        "  NODE TABLES (",
    ]

    node_entries: list[str] = []
    for label in NODE_TYPES:
        node_entries.append(f"    {label} KEY (id)")
    lines.append(",\n".join(node_entries))
    lines.append("  )")

    lines.append("  EDGE TABLES (")

    edge_entries: list[str] = []
    for edge_type, schema in EDGE_SCHEMA.items():
        src_label = schema["source"][0]
        tgt_label = schema["target"][0]
        entry = (
            f"    Relationship AS {edge_type.value}\n"
            f"      KEY (id)\n"
            f"      SOURCE KEY (source_id) REFERENCES {src_label} (id)\n"
            f"      DESTINATION KEY (target_id) REFERENCES {tgt_label} (id)"
        )
        edge_entries.append(entry)
    lines.append(",\n".join(edge_entries))
    lines.append("  );")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# 4. JSON Schema (API validation)
# ---------------------------------------------------------------------------

def generate_json_schema() -> dict[str, Any]:
    """Return a combined JSON Schema with definitions for all node types.

    Uses Pydantic's ``model_json_schema()`` for each node type and merges
    them under a top-level ``$defs`` key.
    """
    defs: dict[str, Any] = {}
    for label, model_cls in NODE_TYPES.items():
        schema = model_cls.model_json_schema()
        # Pydantic may nest shared sub-schemas under $defs; hoist them.
        if "$defs" in schema:
            for k, v in schema["$defs"].items():
                if k not in defs:
                    defs[k] = v
            del schema["$defs"]
        defs[label] = schema

    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "DIALECTICA Ontology",
        "description": "Combined JSON Schema for all 15 DIALECTICA node types.",
        "$defs": defs,
        "oneOf": [{"$ref": f"#/$defs/{label}"} for label in NODE_TYPES],
    }


# ---------------------------------------------------------------------------
# 5. OWL / Turtle (RDF interoperability)
# ---------------------------------------------------------------------------

_TURTLE_NAMESPACE = "https://dialectica.ai/ontology#"
_TURTLE_PREFIX = "dia"


def generate_turtle() -> str:
    """Return an OWL ontology serialised as Turtle.

    Declares a namespace, OWL classes for each node type, datatype
    properties for each field, and object properties for each edge type.
    """
    lines: list[str] = [
        f"@prefix {_TURTLE_PREFIX}: <{_TURTLE_NAMESPACE}> .",
        "@prefix owl: <http://www.w3.org/2002/07/owl#> .",
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .",
        "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .",
        "",
        f"<{_TURTLE_NAMESPACE}> a owl:Ontology ;",
        '    rdfs:label "DIALECTICA Conflict Ontology" ;',
        '    rdfs:comment "Auto-generated from DIALECTICA Pydantic models." .',
        "",
    ]

    # Classes
    lines.append("# ── Node Classes ──")
    lines.append("")
    for label in NODE_TYPES:
        lines.append(f"{_TURTLE_PREFIX}:{label} a owl:Class ;")
        lines.append(f'    rdfs:label "{label}" .')
        lines.append("")

    # Datatype properties (from base ConflictNode — shared by all)
    lines.append("# ── Datatype Properties (shared) ──")
    lines.append("")
    xsd_map: dict[str, str] = {
        "str": "xsd:string",
        "float": "xsd:double",
        "int": "xsd:integer",
        "bool": "xsd:boolean",
        "datetime": "xsd:dateTime",
    }
    for name, field_info in ConflictNode.model_fields.items():
        ann = field_info.annotation
        # Resolve Optional
        args = get_args(ann)
        if args and type(None) in args:
            inner = [a for a in args if a is not type(None)]
            ann = inner[0] if inner else ann

        type_name = getattr(ann, "__name__", str(ann))
        xsd_type = xsd_map.get(type_name, "xsd:string")
        lines.append(f"{_TURTLE_PREFIX}:{name} a owl:DatatypeProperty ;")
        lines.append(f'    rdfs:label "{name}" ;')
        lines.append(f"    rdfs:range {xsd_type} .")
        lines.append("")

    # Per-node-type specific properties
    lines.append("# ── Datatype Properties (type-specific) ──")
    lines.append("")
    base_fields = set(ConflictNode.model_fields.keys())
    emitted: set[str] = set()
    for label, model_cls in NODE_TYPES.items():
        for name, field_info in model_cls.model_fields.items():
            if name in base_fields or name in emitted:
                continue
            emitted.add(name)
            ann = field_info.annotation
            args = get_args(ann)
            if args and type(None) in args:
                inner = [a for a in args if a is not type(None)]
                ann = inner[0] if inner else ann
            type_name = getattr(ann, "__name__", str(ann))
            xsd_type = xsd_map.get(type_name, "xsd:string")
            lines.append(f"{_TURTLE_PREFIX}:{name} a owl:DatatypeProperty ;")
            lines.append(f'    rdfs:label "{name}" ;')
            lines.append(f"    rdfs:domain {_TURTLE_PREFIX}:{label} ;")
            lines.append(f"    rdfs:range {xsd_type} .")
            lines.append("")

    # Object properties (edges)
    lines.append("# ── Object Properties (edges) ──")
    lines.append("")
    for edge_type, schema in EDGE_SCHEMA.items():
        src_label = schema["source"][0]
        tgt_label = schema["target"][0]
        prop_name = edge_type.value.lower()
        lines.append(f"{_TURTLE_PREFIX}:{prop_name} a owl:ObjectProperty ;")
        lines.append(f'    rdfs:label "{edge_type.value}" ;')
        lines.append(f"    rdfs:domain {_TURTLE_PREFIX}:{src_label} ;")
        lines.append(f"    rdfs:range {_TURTLE_PREFIX}:{tgt_label} .")
        lines.append("")

    return "\n".join(lines)
