"""
Neo4j Graph Client — GraphClient implementation for Neo4j Aura.

Uses:
  - neo4j Python driver (Bolt protocol)
  - Cypher queries (vs GQL for Spanner)
  - db.index.vector.queryNodes() for vector search
  - MATCH path = (n)-[*1..@hops]->(m) for traversal

Multi-tenant: All Cypher queries include {tenant_id: $tid} property filter.
Use when Neo4j Graph Data Science algorithms are needed (community detection, etc.).
"""
from __future__ import annotations

# TODO: Implement in Prompt 5
# from neo4j import AsyncGraphDatabase
# from dialectica_graph.interface import GraphClient
