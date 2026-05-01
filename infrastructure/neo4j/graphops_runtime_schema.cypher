// DIALECTICA GraphOps runtime schema
// Mirrors apps/web/src/lib/graphopsGraph.ts for the TacitusCoreV1 runtime graph.

CREATE CONSTRAINT tacitus_core_v1_id IF NOT EXISTS
FOR (n:TacitusCoreV1)
REQUIRE n.id IS UNIQUE;

CREATE INDEX tacitus_core_workspace IF NOT EXISTS
FOR (n:TacitusCoreV1)
ON (n.workspace_id);

CREATE INDEX tacitus_core_case IF NOT EXISTS
FOR (n:TacitusCoreV1)
ON (n.case_id);

CREATE INDEX tacitus_core_extraction_run IF NOT EXISTS
FOR (n:TacitusCoreV1)
ON (n.extraction_run_id);

CREATE INDEX tacitus_core_primitive_type IF NOT EXISTS
FOR (n:TacitusCoreV1)
ON (n.primitive_type);

CREATE INDEX tacitus_core_review_status IF NOT EXISTS
FOR (n:TacitusCoreV1)
ON (n.review_status);

CREATE INDEX tacitus_core_observed_at IF NOT EXISTS
FOR (n:TacitusCoreV1)
ON (n.observed_at);

CREATE FULLTEXT INDEX tacitus_claim_text IF NOT EXISTS
FOR (n:Claim)
ON EACH [n.text, n.provenance_span];

CREATE FULLTEXT INDEX tacitus_chunk_text IF NOT EXISTS
FOR (n:SourceChunk)
ON EACH [n.text];

