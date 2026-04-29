CREATE CONSTRAINT dialectica_conflict_node_id IF NOT EXISTS
FOR (n:ConflictNode)
REQUIRE n.id IS UNIQUE;

CREATE INDEX dialectica_conflict_node_workspace IF NOT EXISTS
FOR (n:ConflictNode)
ON (n.workspace_id);

CREATE INDEX dialectica_conflict_node_tenant IF NOT EXISTS
FOR (n:ConflictNode)
ON (n.tenant_id);

CREATE INDEX dialectica_conflict_node_label IF NOT EXISTS
FOR (n:ConflictNode)
ON (n.label);

CREATE INDEX dialectica_conflict_node_source IF NOT EXISTS
FOR (n:ConflictNode)
ON (n.source);

CREATE INDEX dialectica_conflict_name IF NOT EXISTS
FOR (n:Conflict)
ON (n.name);

CREATE INDEX dialectica_actor_name IF NOT EXISTS
FOR (n:Actor)
ON (n.name);

CREATE INDEX dialectica_event_time IF NOT EXISTS
FOR (n:Event)
ON (n.occurred_at);

CREATE INDEX dialectica_evidence_hash IF NOT EXISTS
FOR (n:Evidence)
ON (n.source_hash);

CREATE INDEX dialectica_operational_signal_workspace IF NOT EXISTS
FOR (n:OperationalSignal)
ON (n.workspace_id);

CREATE INDEX dialectica_reasoning_trace_workspace IF NOT EXISTS
FOR (n:ReasoningTrace)
ON (n.workspace_id);

CREATE INDEX dialectica_ingestion_run_workspace IF NOT EXISTS
FOR (n:IngestionRun)
ON (n.workspace_id);
