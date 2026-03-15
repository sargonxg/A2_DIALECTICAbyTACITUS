"""
GraphClient Interface — Abstract base class for all graph database backends.

Defines the contract that SpannerGraphClient and Neo4jGraphClient must implement.
All methods are async. All operations are scoped by tenant_id for multi-tenancy.

Operations:
  initialize_schema(): Create tables, indexes, property graph
  upsert_node(): Insert or update a ConflictPrimitive node
  upsert_edge(): Insert or update a ConflictRelationship edge
  delete_node(): Soft or hard delete a node
  get_node(): Retrieve a single node by ID
  get_workspace_nodes(): List nodes in a workspace (optionally filtered by label)
  get_workspace_edges(): List edges in a workspace
  traverse(): N-hop subgraph traversal from a starting node
  vector_search(): Semantic similarity search using embeddings
  execute_query(): Execute raw GQL (Spanner) or Cypher (Neo4j) query
  get_workspace_stats(): Node/edge counts, density metrics
"""
from __future__ import annotations

# TODO: Implement in Prompt 5
# from abc import ABC, abstractmethod
