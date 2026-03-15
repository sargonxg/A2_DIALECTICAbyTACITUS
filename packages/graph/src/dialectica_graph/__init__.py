"""
DIALECTICA Graph Package — Database abstraction layer.

Provides a swappable GraphClient interface implemented by:
  SpannerGraphClient: Google Cloud Spanner Graph (primary, GCP-native)
  Neo4jGraphClient: Neo4j Aura (secondary, GDS algorithms)

Configure via GRAPH_BACKEND env var: "spanner" (default) or "neo4j".
"""
