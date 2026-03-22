"""
Shared System Prompt Components — Common prompt fragments for DIALECTICA extraction.
"""

from __future__ import annotations

from dialectica_ontology.tiers import TIER_EDGES, TIER_NODES, OntologyTier

SYSTEM_IDENTITY = """\
You are DIALECTICA, a neurosymbolic conflict analysis system. Your task is to \
extract structured knowledge from unstructured text about conflicts, disputes, \
and negotiations. You produce JSON output conforming to the TACITUS Core Ontology v2.0.

You are precise, evidence-based, and conservative in your extractions. Only extract \
entities and relationships that are explicitly supported by the source text. Assign \
confidence scores reflecting how clearly the text supports each extraction."""


EXTRACTION_RULES = """\
Rules:
1. Every extracted entity MUST have a source_text field \
quoting the text that supports it.
2. Confidence scores: 1.0 = explicit statement, \
0.8 = strong implication, 0.6 = reasonable inference, \
0.4 = weak inference.
3. Do NOT hallucinate entities. If the text does not mention it, \
do not extract it.
4. Prefer specificity: "protest march" over "event", \
"water rights" over "issue".
5. Resolve ambiguity conservatively: if unclear whether someone \
is an ally or opponent, omit the relationship.
6. Temporal information: extract dates, durations, and sequences \
when available.
7. For each entity, use the exact label from the schema \
(e.g., "Actor", "Conflict", "Event")."""


def get_node_type_descriptions(tier: OntologyTier) -> str:
    """Return a formatted description of node types available at the given tier."""
    from dialectica_ontology.primitives import NODE_TYPES

    allowed = TIER_NODES[tier]
    lines = []
    for name, cls in NODE_TYPES.items():
        if name not in allowed:
            continue
        fields = []
        for field_name, field_info in cls.model_fields.items():
            if field_name in (
                "id",
                "workspace_id",
                "tenant_id",
                "created_at",
                "updated_at",
                "embedding",
                "metadata",
                "extraction_method",
            ):
                continue
            required = field_info.is_required()
            annotation = field_info.annotation
            type_name = getattr(annotation, "__name__", str(annotation))
            marker = " (required)" if required else ""
            fields.append(f"    - {field_name}: {type_name}{marker}")
        lines.append(f"  {name}:\n" + "\n".join(fields))
    return "\n".join(lines)


def get_edge_type_descriptions(tier: OntologyTier) -> str:
    """Return a formatted description of edge types available at the given tier."""
    from dialectica_ontology.relationships import EDGE_SCHEMA

    allowed = TIER_EDGES[tier]
    lines = []
    for edge_type, schema in EDGE_SCHEMA.items():
        if edge_type.value not in allowed:
            continue
        sources = ", ".join(schema["source"])
        targets = ", ".join(schema["target"])
        optional = ", ".join(schema.get("optional", []))
        line = f"  {edge_type.value}: {sources} -> {targets}"
        if optional:
            line += f" [optional props: {optional}]"
        lines.append(line)
    return "\n".join(lines)


def build_system_prompt(tier: OntologyTier) -> str:
    """Build the complete system prompt for a given extraction tier."""
    return f"""{SYSTEM_IDENTITY}

{EXTRACTION_RULES}

Available Node Types ({tier.value} tier):
{get_node_type_descriptions(tier)}

Available Relationship Types ({tier.value} tier):
{get_edge_type_descriptions(tier)}"""
