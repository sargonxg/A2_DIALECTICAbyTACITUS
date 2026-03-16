"""
Graph Quality Analyzer — Completeness, consistency, and coverage metrics.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from statistics import mean

from dialectica_graph import GraphClient
from dialectica_ontology.relationships import validate_relationship

# Expected node types for a complete conflict graph
_EXPECTED_NODE_TYPES = [
    "Actor", "Conflict", "Event", "Issue", "Interest",
    "Norm", "Process", "Outcome", "Narrative",
    "EmotionalState", "TrustState", "PowerDynamic",
    "Location", "Evidence", "Role",
]

_ESSENTIAL_NODE_TYPES = ["Actor", "Conflict", "Event"]
_STANDARD_NODE_TYPES = _ESSENTIAL_NODE_TYPES + ["Issue", "Interest", "Process"]
_FULL_NODE_TYPES = _EXPECTED_NODE_TYPES


@dataclass
class CompletenessReport:
    workspace_id: str
    present_node_types: list[str] = field(default_factory=list)
    missing_node_types: list[str] = field(default_factory=list)
    orphan_node_count: int = 0
    completeness_score: float = 0.0
    tier_assessment: str = "essential"


@dataclass
class ConsistencyReport:
    workspace_id: str
    edge_schema_violations: int = 0
    temporal_violations: int = 0
    confidence_issues: int = 0
    consistency_score: float = 1.0
    issues: list[str] = field(default_factory=list)


@dataclass
class CoverageReport:
    workspace_id: str
    earliest_event: datetime | None = None
    latest_event: datetime | None = None
    temporal_span_days: int = 0
    actor_type_distribution: dict[str, int] = field(default_factory=dict)
    source_count: int = 0
    avg_confidence: float = 0.5
    coverage_score: float = 0.0


@dataclass
class QualityDashboard:
    workspace_id: str
    completeness: CompletenessReport | None = None
    consistency: ConsistencyReport | None = None
    coverage: CoverageReport | None = None
    overall_quality: float = 0.0
    recommendations: list[str] = field(default_factory=list)
    assessed_at: str = ""


class GraphQualityAnalyzer:
    """Measures knowledge graph completeness, consistency, and coverage."""

    def __init__(self, graph_client: GraphClient) -> None:
        self._gc = graph_client

    async def assess_completeness(self, workspace_id: str) -> CompletenessReport:
        """What node types are present/missing? Are there orphan nodes?"""
        nodes = await self._gc.get_nodes(workspace_id, limit=1000)
        edges = await self._gc.get_edges(workspace_id)

        present_types: set[str] = set()
        for n in nodes:
            label = getattr(n, "label", n.__class__.__name__)
            present_types.add(label)

        missing = [t for t in _EXPECTED_NODE_TYPES if t not in present_types]

        # Orphan nodes: nodes with no edges
        connected_ids: set[str] = set()
        for e in edges:
            connected_ids.add(e.source_id)
            connected_ids.add(e.target_id)
        orphans = [n for n in nodes if n.id not in connected_ids]

        # Completeness score
        score = len(present_types) / len(_EXPECTED_NODE_TYPES)
        score = round(min(1.0, score), 3)

        # Tier assessment
        essential_present = all(t in present_types for t in _ESSENTIAL_NODE_TYPES)
        standard_present = all(t in present_types for t in _STANDARD_NODE_TYPES)
        full_present = all(t in present_types for t in _FULL_NODE_TYPES)
        tier = "full" if full_present else ("standard" if standard_present else ("essential" if essential_present else "incomplete"))

        return CompletenessReport(
            workspace_id=workspace_id,
            present_node_types=sorted(present_types),
            missing_node_types=missing,
            orphan_node_count=len(orphans),
            completeness_score=score,
            tier_assessment=tier,
        )

    async def assess_consistency(self, workspace_id: str) -> ConsistencyReport:
        """Check temporal and schema constraint violations."""
        nodes = await self._gc.get_nodes(workspace_id, limit=1000)
        edges = await self._gc.get_edges(workspace_id)

        issues: list[str] = []
        edge_violations = 0
        temporal_violations = 0
        confidence_issues = 0

        # Edge schema validation
        for e in edges:
            errors = validate_relationship(e)
            edge_violations += len(errors)
            for err in errors:
                issues.append(f"Edge schema: {err}")

        # Low confidence nodes
        for n in nodes:
            conf = float(getattr(n, "confidence", 1.0))
            if conf < 0.2:
                confidence_issues += 1

        # Temporal: events without timestamps
        events = [n for n in nodes if getattr(n, "label", "") == "Event"]
        for ev in events:
            if getattr(ev, "occurred_at", None) is None:
                temporal_violations += 1
                issues.append(f"Event {ev.id} missing occurred_at timestamp")

        # Compute score
        total_issues = edge_violations + temporal_violations + confidence_issues
        score = max(0.0, 1.0 - total_issues * 0.05)

        return ConsistencyReport(
            workspace_id=workspace_id,
            edge_schema_violations=edge_violations,
            temporal_violations=temporal_violations,
            confidence_issues=confidence_issues,
            consistency_score=round(score, 3),
            issues=issues[:20],
        )

    async def assess_coverage(self, workspace_id: str) -> CoverageReport:
        """Temporal coverage, actor representation, source diversity."""
        nodes = await self._gc.get_nodes(workspace_id, limit=1000)

        events = [n for n in nodes if getattr(n, "label", "") == "Event"]
        actors = [n for n in nodes if getattr(n, "label", "") == "Actor"]

        timestamps = [
            getattr(ev, "occurred_at", None)
            for ev in events
            if getattr(ev, "occurred_at", None) is not None
        ]
        earliest = min(timestamps) if timestamps else None
        latest = max(timestamps) if timestamps else None
        span_days = (latest - earliest).days if earliest and latest else 0

        # Actor type distribution
        actor_types: dict[str, int] = {}
        for a in actors:
            at = getattr(a, "actor_type", "unknown")
            actor_types[str(at)] = actor_types.get(str(at), 0) + 1

        # Source diversity
        sources: set[str] = set()
        for n in nodes:
            src = getattr(n, "source_url", None) or getattr(n, "source_text", None)
            if src:
                sources.add(str(src)[:50])

        # Average confidence
        confidences = [
            float(getattr(n, "confidence", 1.0))
            for n in nodes
        ]
        avg_conf = round(mean(confidences), 3) if confidences else 0.5

        # Coverage score
        temporal_score = min(1.0, span_days / 365) if span_days else 0.0
        actor_score = min(1.0, len(actors) / 10)
        source_score = min(1.0, len(sources) / 5)
        coverage_score = round(mean([temporal_score, actor_score, source_score]), 3)

        return CoverageReport(
            workspace_id=workspace_id,
            earliest_event=earliest,
            latest_event=latest,
            temporal_span_days=span_days,
            actor_type_distribution=actor_types,
            source_count=len(sources),
            avg_confidence=avg_conf,
            coverage_score=coverage_score,
        )

    async def generate_quality_dashboard(self, workspace_id: str) -> QualityDashboard:
        """Combined quality metrics for frontend display."""
        completeness = await self.assess_completeness(workspace_id)
        consistency = await self.assess_consistency(workspace_id)
        coverage = await self.assess_coverage(workspace_id)

        overall = round(mean([
            completeness.completeness_score,
            consistency.consistency_score,
            coverage.coverage_score,
        ]), 3)

        recommendations: list[str] = []
        if completeness.missing_node_types:
            missing_key = [t for t in _STANDARD_NODE_TYPES if t in completeness.missing_node_types]
            if missing_key:
                recommendations.append(f"Add missing node types: {', '.join(missing_key[:3])}")
        if completeness.orphan_node_count > 5:
            recommendations.append(f"Connect {completeness.orphan_node_count} orphan nodes via relationships.")
        if consistency.edge_schema_violations > 0:
            recommendations.append(f"Fix {consistency.edge_schema_violations} edge schema violations.")
        if coverage.avg_confidence < 0.5:
            recommendations.append("Validate low-confidence nodes to improve data quality.")
        if coverage.temporal_span_days < 30:
            recommendations.append("Ingest more historical events to improve temporal coverage.")

        return QualityDashboard(
            workspace_id=workspace_id,
            completeness=completeness,
            consistency=consistency,
            coverage=coverage,
            overall_quality=overall,
            recommendations=recommendations,
            assessed_at=datetime.utcnow().isoformat(),
        )
