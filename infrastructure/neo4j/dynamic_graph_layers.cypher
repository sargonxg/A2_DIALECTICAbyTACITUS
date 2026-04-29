CREATE CONSTRAINT dialectica_workspace_id IF NOT EXISTS
FOR (n:Workspace)
REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT dialectica_project_id IF NOT EXISTS
FOR (n:Project)
REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT dialectica_situation_id IF NOT EXISTS
FOR (n:Situation)
REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT dialectica_episode_id IF NOT EXISTS
FOR (n:Episode)
REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT dialectica_claim_id IF NOT EXISTS
FOR (n:Claim)
REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT dialectica_source_id IF NOT EXISTS
FOR (n:Source)
REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT dialectica_chunk_id IF NOT EXISTS
FOR (n:Chunk)
REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT dialectica_profile_id IF NOT EXISTS
FOR (n:OntologyProfile)
REQUIRE n.id IS UNIQUE;

CREATE INDEX dialectica_situation_workspace IF NOT EXISTS
FOR (n:Situation)
ON (n.workspace_id);

CREATE INDEX dialectica_episode_situation IF NOT EXISTS
FOR (n:Episode)
ON (n.situation_id);

CREATE INDEX dialectica_claim_status IF NOT EXISTS
FOR (n:Claim)
ON (n.claim_status);

CREATE INDEX dialectica_claim_assertion_type IF NOT EXISTS
FOR (n:Claim)
ON (n.assertion_type);

CREATE INDEX dialectica_claim_source_trust IF NOT EXISTS
FOR (n:Claim)
ON (n.source_trust);

CREATE INDEX dialectica_source_trust IF NOT EXISTS
FOR (n:Source)
ON (n.trust_level);

CREATE INDEX dialectica_phase_name IF NOT EXISTS
FOR (n:ConflictPhase)
ON (n.name);

CREATE INDEX dialectica_temporal_interval_start IF NOT EXISTS
FOR (n:TemporalInterval)
ON (n.start_time);

CREATE INDEX dialectica_ontology_profile_name IF NOT EXISTS
FOR (n:OntologyProfile)
ON (n.name);
