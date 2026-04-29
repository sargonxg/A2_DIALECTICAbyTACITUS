from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from dialectica.ontology.models import ActorState


def _state(actor_id: str, level: str, valid_from: datetime) -> ActorState:
    return ActorState(
        workspace_id="ws",
        case_id="case",
        episode_id="episode-1",
        source_id="source-1",
        extraction_run_id="run-1",
        evidence_span_id="span-1",
        provenance_span="The manager warned that trust is falling.",
        confidence=0.7,
        actor_id=actor_id,
        trust_level=level,
        valid_from=valid_from,
        source_ids=["source-1"],
    )


def test_actor_state_is_append_only_not_overwritten():
    first = _state("actor-1", "medium", datetime(2026, 1, 1, tzinfo=UTC))
    second = _state("actor-1", "low", datetime(2026, 1, 2, tzinfo=UTC))
    assert first.id != second.id
    assert first.actor_id == second.actor_id
    assert first.trust_level == "medium"
    assert second.trust_level == "low"


def test_actor_state_requires_at_least_one_state_value():
    with pytest.raises(ValidationError):
        ActorState(
            workspace_id="ws",
            case_id="case",
            episode_id="episode-1",
            source_id="source-1",
            extraction_run_id="run-1",
            evidence_span_id="span-1",
            provenance_span="text",
            confidence=0.7,
            actor_id="actor-1",
        )
