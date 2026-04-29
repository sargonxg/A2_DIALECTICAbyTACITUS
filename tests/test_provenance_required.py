from dialectica.ingestion.pipeline import ingest_path
from dialectica.ontology.models import ProvenancedPrimitive


def test_ingestion_outputs_provenance_for_extracted_primitives():
    primitives = ingest_path(
        "data/sample_docs",
        workspace_id="ws-demo",
        case_id="case-demo",
        chunk_chars=1200,
    )
    extracted = [item for item in primitives if isinstance(item, ProvenancedPrimitive)]
    assert extracted
    for primitive in extracted:
        assert primitive.source_id
        assert primitive.extraction_run_id
        assert primitive.evidence_span_id
        assert primitive.provenance_span
        assert primitive.confidence > 0


def test_ingestion_extracts_commitment_and_constraint():
    primitives = ingest_path(
        "data/sample_docs",
        workspace_id="ws-demo",
        case_id="case-demo",
        chunk_chars=1200,
    )
    names = {item.__class__.__name__ for item in primitives}
    assert "Commitment" in names
    assert "Constraint" in names
    assert "Episode" in names
