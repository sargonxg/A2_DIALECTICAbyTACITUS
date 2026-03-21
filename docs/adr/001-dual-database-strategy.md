# ADR-001: Dual Database Strategy (FalkorDB + Neo4j)

**Status:** Accepted
**Date:** 2025-01-15

## Context
DIALECTICA requires both fast tenant-isolated graph operations and advanced graph analytics (community detection, centrality, pathfinding). No single graph database optimally serves both needs.

## Decision
Use FalkorDB for tenant-facing operations (graph-per-tenant isolation, Redis-protocol compatibility, fast Cypher) and Neo4j for analytics (GDS algorithms, Leiden community detection, APOC utilities). Sync via Pub/Sub events.

## Consequences
- **Positive:** Each database optimized for its workload; tenant isolation is native in FalkorDB; GDS algorithms available in Neo4j
- **Negative:** Operational complexity of two databases; eventual consistency between them; sync logic required
- **Migration path:** If FalkorDB adds GDS-equivalent algorithms, consolidate to single DB
