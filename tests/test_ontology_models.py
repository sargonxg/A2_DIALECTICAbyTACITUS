import pytest
from pydantic import ValidationError

from dialectica.ontology.models import Actor, EvidenceSpan, ExtractionRun
from dialectica.ontology.schema import core_primitive_names


def test_core_schema_contains_requested_primitives():
    names = core_primitive_names()
    assert {"Actor", "Claim", "Commitment", "ActorState", "EvidenceSpan", "ExtractionRun"} <= names


def test_extraction_run_defaults_to_own_run_id():
    run = ExtractionRun(
        workspace_id="ws",
        case_id="case",
        model_name="local",
        extraction_method="rule_based",
    )
    assert run.extraction_run_id == run.id


def test_provenanced_actor_requires_source_fields():
    with pytest.raises(ValidationError):
        Actor(
            workspace_id="ws",
            case_id="case",
            name="Actor A",
            confidence=0.8,
        )


def test_evidence_span_requires_valid_offsets():
    try:
        EvidenceSpan(
            workspace_id="ws",
            case_id="case",
            source_id="source",
            chunk_id="chunk",
            extraction_run_id="run",
            provenance_span="text",
            start_char=10,
            end_char=5,
            confidence=0.7,
        )
    except ValidationError as exc:
        assert "end_char must be greater" in str(exc)
    else:
        raise AssertionError("expected ValidationError")
