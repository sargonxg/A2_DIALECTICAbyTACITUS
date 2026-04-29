import pytest

from dialectica.graph.memory_adapter import MemoryGraphAdapter
from dialectica.ontology.models import Commitment


def test_memory_graph_requires_case_scope():
    graph = MemoryGraphAdapter()
    with pytest.raises(ValueError):
        graph.write_primitive(
            Commitment(
                workspace_id="ws",
                case_id="case",
                episode_id="episode",
                source_id="source",
                extraction_run_id="run",
                evidence_span_id="span",
                provenance_span="Alex will own the launch deck.",
                confidence=0.8,
                actor_id="actor",
                description="Alex will own the launch deck.",
            ).model_copy(update={"case_id": ""})
        )


def test_memory_graph_keeps_cases_separate():
    graph = MemoryGraphAdapter()
    c1 = Commitment(
        workspace_id="ws",
        case_id="case-a",
        episode_id="episode-a",
        source_id="source",
        extraction_run_id="run",
        evidence_span_id="span",
        provenance_span="Alex will own the launch deck.",
        confidence=0.8,
        actor_id="actor",
        description="Alex will own the launch deck.",
    )
    c2 = c1.model_copy(
        update={"id": "commitment-b", "case_id": "case-b", "episode_id": "episode-b"}
    )
    graph.write_primitives([c1, c2])

    case_a = graph.query("What commitments constrain Actor X?", "ws", "case-a")
    case_b = graph.query("What commitments constrain Actor X?", "ws", "case-b")

    assert len(case_a) == 1
    assert len(case_b) == 1
    assert case_a[0]["case_id"] == "case-a"
    assert case_b[0]["case_id"] == "case-b"
