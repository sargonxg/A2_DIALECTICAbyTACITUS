# Using DIALECTICA with Claude Desktop

DIALECTICA provides an MCP (Model Context Protocol) server with 5 conflict intelligence tools.

## Setup

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "dialectica": {
      "command": "python",
      "args": ["-m", "dialectica_mcp.server"],
      "env": {
        "GRAPH_BACKEND": "neo4j",
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USER": "neo4j",
        "NEO4J_PASSWORD": "your-password"
      }
    }
  }
}
```

For Neo4j Aura (production):
```json
{
  "mcpServers": {
    "dialectica": {
      "command": "python",
      "args": ["-m", "dialectica_mcp.server"],
      "env": {
        "GRAPH_BACKEND": "neo4j",
        "NEO4J_URI": "neo4j+s://xxxxx.databases.neo4j.io",
        "NEO4J_USER": "neo4j",
        "NEO4J_PASSWORD": "your-aura-password"
      }
    }
  }
}
```

## Available Tools

| Tool | Description |
|------|-------------|
| `query_conflict_graph` | GraphRAG retrieval + synthesis on conflict knowledge graphs |
| `get_actor_analysis` | Actor network, alliances, oppositions, and power dynamics |
| `get_escalation_status` | Glasl stage, velocity, trajectory, and direction |
| `compare_conflicts` | Structural similarity between two conflict workspaces |
| `ingest_document` | Extract conflict entities from text into the knowledge graph |

## Prerequisites

```bash
pip install dialectica-ontology dialectica-graph dialectica-extraction dialectica-reasoning
pip install mcp
```

## Testing

```bash
python -m dialectica_mcp.server
```
