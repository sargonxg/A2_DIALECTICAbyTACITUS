"""
Spanner Graph DDL — Complete schema definition for DIALECTICA on Google Cloud Spanner.

Tables:
  Nodes: All 15 node types via dynamic labels (Actor, Conflict, Event, ...)
  Edges: All 20 edge types via dynamic labels (PARTY_TO, PARTICIPATES_IN, ...)
  Workspaces: Workspace metadata with ontology_tier, Glasl/Kriesberg state
  TheoryAssessments: Cached theory analysis results
  APIKeys: API key management (hashed, tenant-scoped)
  UsageLogs: Per-request usage tracking
  ExtractionJobs: Async extraction job status

Property Graph:
  CREATE PROPERTY GRAPH ConflictGraph
  NODE TABLES (Nodes) ... DYNAMIC LABEL ... DYNAMIC PROPERTIES
  EDGE TABLES (Edges) ... DYNAMIC LABEL ... DYNAMIC PROPERTIES

Vector indexes: COSINE distance on embedding ARRAY<FLOAT32>(vector_length=768)

Key design: tenant_id as PK prefix for row-level multi-tenant isolation.
"""
from __future__ import annotations


# ── Core Tables ────────────────────────────────────────────────────────────

_NODES_TABLE = """\
CREATE TABLE Nodes (
  tenant_id    STRING(64)  NOT NULL,
  workspace_id STRING(64)  NOT NULL,
  id           STRING(64)  NOT NULL,
  label        STRING(64)  NOT NULL,
  properties   JSON,
  source_text  STRING(MAX),
  confidence   FLOAT64     NOT NULL DEFAULT (1.0),
  extraction_method STRING(64),
  embedding    ARRAY<FLOAT32>(vector_length=768),
  metadata     JSON,
  created_at   TIMESTAMP   NOT NULL DEFAULT (CURRENT_TIMESTAMP()),
  updated_at   TIMESTAMP   NOT NULL DEFAULT (CURRENT_TIMESTAMP()),
  deleted_at   TIMESTAMP,
) PRIMARY KEY (tenant_id, workspace_id, id)"""

_EDGES_TABLE = """\
CREATE TABLE Edges (
  tenant_id    STRING(64)  NOT NULL,
  workspace_id STRING(64)  NOT NULL,
  id           STRING(64)  NOT NULL,
  type         STRING(64)  NOT NULL,
  source_id    STRING(64)  NOT NULL,
  target_id    STRING(64)  NOT NULL,
  source_label STRING(64),
  target_label STRING(64),
  properties   JSON,
  weight       FLOAT64     NOT NULL DEFAULT (1.0),
  confidence   FLOAT64     NOT NULL DEFAULT (1.0),
  temporal_start TIMESTAMP,
  temporal_end   TIMESTAMP,
  source_text  STRING(MAX),
  created_at   TIMESTAMP   NOT NULL DEFAULT (CURRENT_TIMESTAMP()),
  updated_at   TIMESTAMP   NOT NULL DEFAULT (CURRENT_TIMESTAMP()),
) PRIMARY KEY (tenant_id, workspace_id, id)"""

_WORKSPACES_TABLE = """\
CREATE TABLE Workspaces (
  tenant_id      STRING(64)  NOT NULL,
  id             STRING(64)  NOT NULL,
  name           STRING(256) NOT NULL,
  description    STRING(MAX),
  ontology_tier  STRING(32)  NOT NULL DEFAULT ('standard'),
  glasl_stage    INT64,
  kriesberg_phase STRING(32),
  created_at     TIMESTAMP   NOT NULL DEFAULT (CURRENT_TIMESTAMP()),
  updated_at     TIMESTAMP   NOT NULL DEFAULT (CURRENT_TIMESTAMP()),
) PRIMARY KEY (tenant_id, id)"""

_THEORY_ASSESSMENTS_TABLE = """\
CREATE TABLE TheoryAssessments (
  tenant_id    STRING(64)  NOT NULL,
  workspace_id STRING(64)  NOT NULL,
  id           STRING(64)  NOT NULL,
  framework    STRING(64)  NOT NULL,
  assessment   JSON        NOT NULL,
  score        FLOAT64,
  created_at   TIMESTAMP   NOT NULL DEFAULT (CURRENT_TIMESTAMP()),
) PRIMARY KEY (tenant_id, workspace_id, id)"""

_API_KEYS_TABLE = """\
CREATE TABLE APIKeys (
  tenant_id   STRING(64)   NOT NULL,
  id          STRING(64)   NOT NULL,
  key_hash    STRING(256)  NOT NULL,
  name        STRING(256),
  scopes      ARRAY<STRING(64)>,
  created_at  TIMESTAMP    NOT NULL DEFAULT (CURRENT_TIMESTAMP()),
  expires_at  TIMESTAMP,
  revoked_at  TIMESTAMP,
) PRIMARY KEY (tenant_id, id)"""

_USAGE_LOGS_TABLE = """\
CREATE TABLE UsageLogs (
  tenant_id    STRING(64)  NOT NULL,
  id           STRING(64)  NOT NULL,
  workspace_id STRING(64),
  endpoint     STRING(256) NOT NULL,
  method       STRING(16)  NOT NULL,
  status_code  INT64       NOT NULL,
  latency_ms   INT64,
  tokens_used  INT64,
  created_at   TIMESTAMP   NOT NULL DEFAULT (CURRENT_TIMESTAMP()),
) PRIMARY KEY (tenant_id, id)"""

_EXTRACTION_JOBS_TABLE = """\
CREATE TABLE ExtractionJobs (
  tenant_id    STRING(64)  NOT NULL,
  workspace_id STRING(64)  NOT NULL,
  id           STRING(64)  NOT NULL,
  status       STRING(32)  NOT NULL DEFAULT ('pending'),
  source_type  STRING(64),
  source_uri   STRING(MAX),
  nodes_created INT64      DEFAULT (0),
  edges_created INT64      DEFAULT (0),
  error_message STRING(MAX),
  created_at   TIMESTAMP   NOT NULL DEFAULT (CURRENT_TIMESTAMP()),
  updated_at   TIMESTAMP   NOT NULL DEFAULT (CURRENT_TIMESTAMP()),
  completed_at TIMESTAMP,
) PRIMARY KEY (tenant_id, workspace_id, id)"""

_SCHEMA_MIGRATIONS_TABLE = """\
CREATE TABLE SchemaMigrations (
  version    INT64       NOT NULL,
  name       STRING(256) NOT NULL,
  applied_at TIMESTAMP   NOT NULL DEFAULT (CURRENT_TIMESTAMP()),
) PRIMARY KEY (version)"""


# ── Property Graph Definition ──────────────────────────────────────────────

_PROPERTY_GRAPH = """\
CREATE OR REPLACE PROPERTY GRAPH ConflictGraph
  NODE TABLES (
    Nodes
      KEY (tenant_id, workspace_id, id)
      DYNAMIC LABEL (label)
      DYNAMIC PROPERTIES (properties)
  )
  EDGE TABLES (
    Edges
      KEY (tenant_id, workspace_id, id)
      SOURCE KEY (tenant_id, workspace_id, source_id) REFERENCES Nodes (tenant_id, workspace_id, id)
      DESTINATION KEY (tenant_id, workspace_id, target_id) REFERENCES Nodes (tenant_id, workspace_id, id)
      DYNAMIC LABEL (type)
      DYNAMIC PROPERTIES (properties)
  )"""


# ── Indexes ────────────────────────────────────────────────────────────────

_INDEXES = [
    # Node indexes
    "CREATE INDEX Idx_Nodes_Label ON Nodes (tenant_id, workspace_id, label)",
    "CREATE INDEX Idx_Nodes_CreatedAt ON Nodes (tenant_id, workspace_id, created_at DESC)",
    "CREATE INDEX Idx_Nodes_UpdatedAt ON Nodes (tenant_id, workspace_id, updated_at DESC)",
    "CREATE NULL_FILTERED INDEX Idx_Nodes_DeletedAt ON Nodes (tenant_id, workspace_id, deleted_at)",
    # Edge indexes
    "CREATE INDEX Idx_Edges_Type ON Edges (tenant_id, workspace_id, type)",
    "CREATE INDEX Idx_Edges_Source ON Edges (tenant_id, workspace_id, source_id)",
    "CREATE INDEX Idx_Edges_Target ON Edges (tenant_id, workspace_id, target_id)",
    "CREATE INDEX Idx_Edges_SourceTarget ON Edges (tenant_id, workspace_id, source_id, target_id)",
    # Workspace indexes
    "CREATE INDEX Idx_Workspaces_Name ON Workspaces (tenant_id, name)",
    # API key lookup
    "CREATE UNIQUE INDEX Idx_APIKeys_Hash ON APIKeys (key_hash)",
    # Extraction job status
    "CREATE INDEX Idx_ExtractionJobs_Status ON ExtractionJobs (tenant_id, workspace_id, status)",
    # Usage log time range
    "CREATE INDEX Idx_UsageLogs_CreatedAt ON UsageLogs (tenant_id, created_at DESC)",
]

_VECTOR_INDEX = """\
CREATE VECTOR INDEX Idx_Nodes_Embedding
  ON Nodes(embedding)
  WHERE embedding IS NOT NULL
  OPTIONS (
    distance_type = 'COSINE',
    tree_depth = 3,
    num_leaves = 1000
  )"""


def get_ddl_statements() -> list[str]:
    """Return all DDL statements in execution order.

    Returns CREATE TABLE, CREATE PROPERTY GRAPH, CREATE INDEX, and
    CREATE VECTOR INDEX statements.
    """
    tables = [
        _NODES_TABLE,
        _EDGES_TABLE,
        _WORKSPACES_TABLE,
        _THEORY_ASSESSMENTS_TABLE,
        _API_KEYS_TABLE,
        _USAGE_LOGS_TABLE,
        _EXTRACTION_JOBS_TABLE,
        _SCHEMA_MIGRATIONS_TABLE,
    ]
    return tables + [_PROPERTY_GRAPH] + _INDEXES + [_VECTOR_INDEX]


def get_table_ddl() -> list[str]:
    """Return only CREATE TABLE statements (for migration diffing)."""
    return [
        _NODES_TABLE,
        _EDGES_TABLE,
        _WORKSPACES_TABLE,
        _THEORY_ASSESSMENTS_TABLE,
        _API_KEYS_TABLE,
        _USAGE_LOGS_TABLE,
        _EXTRACTION_JOBS_TABLE,
        _SCHEMA_MIGRATIONS_TABLE,
    ]


def get_index_ddl() -> list[str]:
    """Return only CREATE INDEX statements."""
    return _INDEXES + [_VECTOR_INDEX]
