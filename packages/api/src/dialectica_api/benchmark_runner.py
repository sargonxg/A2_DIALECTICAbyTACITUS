"""
Benchmark Runner — Extraction pipeline evaluation against gold-standard annotations.

Compares LLM-extracted conflict graphs against human-annotated gold standards
using fuzzy node matching and edge comparison. Computes precision, recall, and
F1 scores per node type, per edge type, and overall.

Corpora: jcpoa, romeo_juliet, crime_punishment, war_peace, custom
Tiers: essential (nodes only), standard (nodes + edges), full (nodes + edges + properties)
"""
from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class MetricScore:
    """Precision / Recall / F1 for a category."""
    precision: float = 0.0
    recall: float = 0.0
    f1: float = 0.0
    true_positives: int = 0
    false_positives: int = 0
    false_negatives: int = 0


@dataclass
class BenchmarkMetrics:
    """Aggregated benchmark evaluation results."""
    overall: MetricScore = field(default_factory=MetricScore)
    by_node_type: dict[str, MetricScore] = field(default_factory=dict)
    by_edge_type: dict[str, MetricScore] = field(default_factory=dict)
    graph_augmented: MetricScore | None = None
    evaluation_points: int = 480
    extraction_time_ms: float = 0.0
    hallucination_rate: float = 0.0


@dataclass
class BenchmarkResult:
    """Full benchmark run result."""
    benchmark_id: str = ""
    corpus_id: str = ""
    tier: str = "standard"
    model: str = "gemini-2.0-flash"
    results: BenchmarkMetrics = field(default_factory=BenchmarkMetrics)
    completed_at: str = ""


# ---------------------------------------------------------------------------
# Gold-standard paths
# ---------------------------------------------------------------------------

_BENCHMARKS_DIR = Path(__file__).resolve().parents[4] / "data" / "seed" / "benchmarks"

_CORPUS_FILES: dict[str, str] = {
    "jcpoa": "jcpoa_gold.json",
    "romeo_juliet": "romeo_juliet_gold.json",
    "crime_punishment": "crime_punishment_gold.json",
    "war_peace": "war_peace_gold.json",
}

VALID_CORPUS_IDS = {"jcpoa", "romeo_juliet", "crime_punishment", "war_peace", "custom"}


# ---------------------------------------------------------------------------
# Similarity helpers
# ---------------------------------------------------------------------------

def _name_similarity(a: str, b: str) -> float:
    """Fuzzy string similarity ratio between two names."""
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()


def _compute_f1(precision: float, recall: float) -> float:
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def _score_from_counts(tp: int, fp: int, fn: int) -> MetricScore:
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    return MetricScore(
        precision=round(precision, 4),
        recall=round(recall, 4),
        f1=round(_compute_f1(precision, recall), 4),
        true_positives=tp,
        false_positives=fp,
        false_negatives=fn,
    )


# ---------------------------------------------------------------------------
# BenchmarkRunner
# ---------------------------------------------------------------------------

class BenchmarkRunner:
    """Orchestrates benchmark evaluation of the DIALECTICA extraction pipeline.

    Usage:
        runner = BenchmarkRunner()
        result = await runner.run_benchmark(corpus_id="jcpoa", tier="standard")
    """

    _SIMILARITY_THRESHOLD = 0.8

    def load_gold_standard(self, corpus_id: str) -> dict[str, Any]:
        """Load gold-standard annotation from data/seed/benchmarks/."""
        if corpus_id not in _CORPUS_FILES:
            raise ValueError(
                f"Unknown corpus_id '{corpus_id}'. "
                f"Valid options: {sorted(_CORPUS_FILES.keys())}"
            )
        path = _BENCHMARKS_DIR / _CORPUS_FILES[corpus_id]
        if not path.exists():
            raise FileNotFoundError(
                f"Gold standard file not found: {path}. "
                f"Run seed scripts or create benchmark data first."
            )
        with open(path) as f:
            return json.load(f)

    async def run_benchmark(
        self,
        corpus_id: str = "jcpoa",
        tier: str = "standard",
        model: str = "gemini-2.0-flash",
        include_graph_augmented: bool = False,
        custom_text: str | None = None,
        custom_gold: dict[str, Any] | None = None,
    ) -> BenchmarkResult:
        """Orchestrate extraction + comparison against gold standard.

        For now, the actual extraction pipeline call is mocked (returns
        stub results) since running Gemini requires API credentials.
        The comparison logic is fully implemented.
        """
        benchmark_id = f"bench_{uuid.uuid4().hex[:12]}"
        start = time.monotonic()

        # Load gold standard
        if corpus_id == "custom":
            if not custom_text or not custom_gold:
                raise ValueError(
                    "corpus_id='custom' requires custom_text and custom_gold."
                )
            gold = custom_gold
            source_text = custom_text
        else:
            gold = self.load_gold_standard(corpus_id)
            source_text = gold.get("source_text", "")

        gold_nodes: list[dict[str, Any]] = gold.get("gold_nodes", [])
        gold_edges: list[dict[str, Any]] = gold.get("gold_edges", [])

        # Run extraction pipeline (stubbed — returns simulated results)
        extracted_nodes, extracted_edges = await self._run_extraction(
            source_text, tier, model
        )

        # Compare
        node_metrics = self.compare_nodes(gold_nodes, extracted_nodes)
        edge_metrics: dict[str, MetricScore] = {}
        if tier in ("standard", "full"):
            edge_metrics = self.compare_edges(gold_edges, extracted_edges)

        # Aggregate
        overall = self.compute_overall_metrics(node_metrics, edge_metrics)

        # Graph-augmented evaluation (optional)
        graph_aug: MetricScore | None = None
        if include_graph_augmented:
            graph_aug = self._evaluate_graph_augmented(
                gold_nodes, gold_edges, extracted_nodes, extracted_edges
            )

        elapsed_ms = (time.monotonic() - start) * 1000

        # Hallucination rate: fraction of extracted nodes not matching any gold node
        total_extracted = len(extracted_nodes) + len(extracted_edges)
        total_fp = overall.false_positives
        hallucination_rate = total_fp / total_extracted if total_extracted > 0 else 0.0

        metrics = BenchmarkMetrics(
            overall=overall,
            by_node_type=node_metrics,
            by_edge_type=edge_metrics,
            graph_augmented=graph_aug,
            evaluation_points=len(gold_nodes) * 10 + len(gold_edges) * 5,
            extraction_time_ms=round(elapsed_ms, 2),
            hallucination_rate=round(hallucination_rate, 4),
        )

        return BenchmarkResult(
            benchmark_id=benchmark_id,
            corpus_id=corpus_id,
            tier=tier,
            model=model,
            results=metrics,
            completed_at=datetime.utcnow().isoformat() + "Z",
        )

    async def _run_extraction(
        self, source_text: str, tier: str, model: str
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Run the extraction pipeline. Currently returns stub/simulated results.

        In production, this would call:
            from dialectica_extraction import ExtractionPipeline
            pipeline = ExtractionPipeline(model=model)
            result = await pipeline.extract(text=source_text, tier=tier)
        """
        # Stub: return a realistic partial extraction to exercise the comparison logic
        stub_nodes: list[dict[str, Any]] = [
            {"id": "ext_iran", "label": "Actor", "name": "Iran"},
            {"id": "ext_usa", "label": "Actor", "name": "United States"},
            {"id": "ext_uk", "label": "Actor", "name": "United Kingdom"},
            {"id": "ext_france", "label": "Actor", "name": "France"},
            {"id": "ext_germany", "label": "Actor", "name": "Germany"},
            {"id": "ext_russia", "label": "Actor", "name": "Russia"},
            {"id": "ext_china", "label": "Actor", "name": "China"},
            {"id": "ext_eu", "label": "Actor", "name": "European Union"},
            {"id": "ext_iaea", "label": "Actor", "name": "IAEA"},
            {"id": "ext_israel", "label": "Actor", "name": "Israel"},
            {"id": "ext_saudi", "label": "Actor", "name": "Saudi Arabia"},
            {"id": "ext_hezbollah", "label": "Actor", "name": "Hezbollah"},
            {"id": "ext_conflict", "label": "Conflict", "name": "Iran Nuclear Dispute"},
            {"id": "ext_jcpoa_signed", "label": "Event", "name": "JCPOA Signing"},
            {"id": "ext_us_withdrawal", "label": "Event", "name": "US Withdrawal from JCPOA"},
            {"id": "ext_iran_enrichment", "label": "Event", "name": "Iran Exceeds Limits"},
            {"id": "ext_soleimani", "label": "Event", "name": "Soleimani Killing"},
            {"id": "ext_enrichment_84", "label": "Event", "name": "Iran 83.7% Enrichment"},
            {"id": "ext_snapback", "label": "Event", "name": "Snapback Sanctions Triggered"},
            {"id": "ext_vienna", "label": "Event", "name": "Vienna Talks"},
            {"id": "ext_issue_enrich", "label": "Issue", "name": "Uranium Enrichment Rights"},
            {"id": "ext_issue_sanctions", "label": "Issue", "name": "Sanctions Relief"},
            {"id": "ext_issue_irgc", "label": "Issue", "name": "IRGC Designation"},
            {"id": "ext_interest_iran", "label": "Interest", "name": "Iran Security Interest"},
            {"id": "ext_interest_us", "label": "Interest", "name": "US Nonproliferation Interest"},
            {"id": "ext_process_jcpoa", "label": "Process", "name": "JCPOA Negotiations"},
            {"id": "ext_outcome_2015", "label": "Outcome", "name": "JCPOA Agreement 2015"},
            {"id": "ext_narrative_iran", "label": "Narrative", "name": "Iran Rights Narrative"},
            {"id": "ext_narrative_west", "label": "Narrative", "name": "Western Threat Narrative"},
            # False positive: entity not in gold standard
            {"id": "ext_netanyahu", "label": "Actor", "name": "Benjamin Netanyahu"},
        ]
        stub_edges: list[dict[str, Any]] = [
            {"source": "ext_iran", "target": "ext_conflict", "type": "PARTY_TO"},
            {"source": "ext_usa", "target": "ext_conflict", "type": "PARTY_TO"},
            {"source": "ext_uk", "target": "ext_conflict", "type": "PARTY_TO"},
            {"source": "ext_france", "target": "ext_conflict", "type": "PARTY_TO"},
            {"source": "ext_germany", "target": "ext_conflict", "type": "PARTY_TO"},
            {"source": "ext_russia", "target": "ext_conflict", "type": "PARTY_TO"},
            {"source": "ext_china", "target": "ext_conflict", "type": "PARTY_TO"},
            {"source": "ext_eu", "target": "ext_conflict", "type": "PARTY_TO"},
            {"source": "ext_iaea", "target": "ext_conflict", "type": "PARTY_TO"},
            {"source": "ext_iran", "target": "ext_interest_iran", "type": "HAS_INTEREST"},
            {"source": "ext_usa", "target": "ext_interest_us", "type": "HAS_INTEREST"},
            {"source": "ext_us_withdrawal", "target": "ext_iran_enrichment", "type": "CAUSED"},
            {"source": "ext_soleimani", "target": "ext_enrichment_84", "type": "CAUSED"},
            {"source": "ext_enrichment_84", "target": "ext_snapback", "type": "CAUSED"},
            {"source": "ext_uk", "target": "ext_france", "type": "ALLIED_WITH"},
            {"source": "ext_france", "target": "ext_germany", "type": "ALLIED_WITH"},
            {"source": "ext_uk", "target": "ext_usa", "type": "ALLIED_WITH"},
            {"source": "ext_usa", "target": "ext_iran", "type": "OPPOSED_TO"},
            {"source": "ext_saudi", "target": "ext_iran", "type": "OPPOSED_TO"},
            {"source": "ext_iran", "target": "ext_hezbollah", "type": "HAS_POWER_OVER"},
            {"source": "ext_usa", "target": "ext_iran", "type": "HAS_POWER_OVER"},
            {"source": "ext_iran", "target": "ext_process_jcpoa", "type": "PARTICIPATES_IN"},
            {"source": "ext_usa", "target": "ext_process_jcpoa", "type": "PARTICIPATES_IN"},
            {"source": "ext_conflict", "target": "ext_process_jcpoa", "type": "RESOLVED_THROUGH"},
            {"source": "ext_process_jcpoa", "target": "ext_outcome_2015", "type": "PRODUCES"},
            {"source": "ext_narrative_iran", "target": "ext_conflict", "type": "ABOUT"},
            {"source": "ext_narrative_west", "target": "ext_conflict", "type": "ABOUT"},
            {"source": "ext_issue_enrich", "target": "ext_conflict", "type": "PART_OF"},
            {"source": "ext_issue_sanctions", "target": "ext_conflict", "type": "PART_OF"},
            {"source": "ext_issue_irgc", "target": "ext_conflict", "type": "PART_OF"},
        ]
        return stub_nodes, stub_edges

    def compare_nodes(
        self,
        gold_nodes: list[dict[str, Any]],
        extracted_nodes: list[dict[str, Any]],
    ) -> dict[str, MetricScore]:
        """Compare extracted nodes against gold standard using fuzzy name matching.

        Groups results by node label (type). A match requires:
        1. Same label (node type)
        2. Name similarity > 0.8 (SequenceMatcher ratio)
        """
        # Group by label
        gold_by_label: dict[str, list[dict[str, Any]]] = {}
        for n in gold_nodes:
            label = n.get("label", "Unknown")
            gold_by_label.setdefault(label, []).append(n)

        ext_by_label: dict[str, list[dict[str, Any]]] = {}
        for n in extracted_nodes:
            label = n.get("label", "Unknown")
            ext_by_label.setdefault(label, []).append(n)

        all_labels = set(gold_by_label.keys()) | set(ext_by_label.keys())
        metrics: dict[str, MetricScore] = {}

        for label in sorted(all_labels):
            golds = gold_by_label.get(label, [])
            extracts = ext_by_label.get(label, [])
            matched_gold: set[int] = set()
            matched_ext: set[int] = set()

            for ei, ext in enumerate(extracts):
                ext_name = ext.get("name", "")
                best_score = 0.0
                best_gi = -1
                for gi, gold in enumerate(golds):
                    if gi in matched_gold:
                        continue
                    gold_name = gold.get("name", "")
                    sim = _name_similarity(ext_name, gold_name)
                    if sim > best_score:
                        best_score = sim
                        best_gi = gi
                if best_score >= self._SIMILARITY_THRESHOLD and best_gi >= 0:
                    matched_gold.add(best_gi)
                    matched_ext.add(ei)

            tp = len(matched_gold)
            fp = len(extracts) - len(matched_ext)
            fn = len(golds) - len(matched_gold)
            metrics[label] = _score_from_counts(tp, fp, fn)

        return metrics

    def compare_edges(
        self,
        gold_edges: list[dict[str, Any]],
        extracted_edges: list[dict[str, Any]],
    ) -> dict[str, MetricScore]:
        """Compare extracted edges against gold standard.

        An edge matches if it has the same type and source/target can be
        fuzzy-matched to the gold source/target IDs or names.
        """
        # Group by edge type
        gold_by_type: dict[str, list[dict[str, Any]]] = {}
        for e in gold_edges:
            etype = e.get("type", "UNKNOWN")
            gold_by_type.setdefault(etype, []).append(e)

        ext_by_type: dict[str, list[dict[str, Any]]] = {}
        for e in extracted_edges:
            etype = e.get("type", "UNKNOWN")
            ext_by_type.setdefault(etype, []).append(e)

        all_types = set(gold_by_type.keys()) | set(ext_by_type.keys())
        metrics: dict[str, MetricScore] = {}

        for etype in sorted(all_types):
            golds = gold_by_type.get(etype, [])
            extracts = ext_by_type.get(etype, [])
            matched_gold: set[int] = set()
            matched_ext: set[int] = set()

            for ei, ext in enumerate(extracts):
                for gi, gold in enumerate(golds):
                    if gi in matched_gold:
                        continue
                    # Match by source/target ID suffix similarity
                    src_match = self._edge_endpoint_matches(
                        ext.get("source", ""), gold.get("source", "")
                    )
                    tgt_match = self._edge_endpoint_matches(
                        ext.get("target", ""), gold.get("target", "")
                    )
                    if src_match and tgt_match:
                        matched_gold.add(gi)
                        matched_ext.add(ei)
                        break

            tp = len(matched_gold)
            fp = len(extracts) - len(matched_ext)
            fn = len(golds) - len(matched_gold)
            metrics[etype] = _score_from_counts(tp, fp, fn)

        return metrics

    def _edge_endpoint_matches(self, ext_id: str, gold_id: str) -> bool:
        """Check if two edge endpoint IDs refer to the same entity.

        Compares the suffix after the last underscore (e.g., 'ext_iran' matches
        'gold_actor_iran') using fuzzy matching.
        """
        ext_suffix = ext_id.rsplit("_", 1)[-1] if "_" in ext_id else ext_id
        gold_suffix = gold_id.rsplit("_", 1)[-1] if "_" in gold_id else gold_id
        return _name_similarity(ext_suffix, gold_suffix) >= self._SIMILARITY_THRESHOLD

    def compute_overall_metrics(
        self,
        node_metrics: dict[str, MetricScore],
        edge_metrics: dict[str, MetricScore],
    ) -> MetricScore:
        """Compute micro-averaged overall precision, recall, F1."""
        total_tp = sum(m.true_positives for m in node_metrics.values())
        total_fp = sum(m.false_positives for m in node_metrics.values())
        total_fn = sum(m.false_negatives for m in node_metrics.values())

        for m in edge_metrics.values():
            total_tp += m.true_positives
            total_fp += m.false_positives
            total_fn += m.false_negatives

        return _score_from_counts(total_tp, total_fp, total_fn)

    def _evaluate_graph_augmented(
        self,
        gold_nodes: list[dict[str, Any]],
        gold_edges: list[dict[str, Any]],
        extracted_nodes: list[dict[str, Any]],
        extracted_edges: list[dict[str, Any]],
    ) -> MetricScore:
        """Graph-augmented evaluation: considers structural connectivity.

        Gives bonus credit for correctly identifying connected components
        (e.g., an actor + its conflict + the PARTY_TO edge between them).
        """
        # Build gold adjacency
        gold_connected: set[tuple[str, str]] = set()
        for e in gold_edges:
            gold_connected.add((e.get("source", ""), e.get("target", "")))

        ext_connected: set[tuple[str, str]] = set()
        for e in extracted_edges:
            ext_connected.add((e.get("source", ""), e.get("target", "")))

        # Count matches (relaxed endpoint comparison)
        tp = 0
        for gs, gt in gold_connected:
            for es, et in ext_connected:
                if (self._edge_endpoint_matches(es, gs) and
                        self._edge_endpoint_matches(et, gt)):
                    tp += 1
                    break

        fp = max(0, len(ext_connected) - tp)
        fn = max(0, len(gold_connected) - tp)
        return _score_from_counts(tp, fp, fn)
