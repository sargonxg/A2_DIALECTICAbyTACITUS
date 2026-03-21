# DIALECTICA SDK Quickstart

## Python

```python
import httpx

API_URL = "http://localhost:8080"
API_KEY = "your-api-key"
headers = {"X-API-Key": API_KEY}

# Create workspace
resp = httpx.post(f"{API_URL}/v1/workspaces", headers=headers, json={
    "name": "My Analysis",
    "template_id": "warfare_political",
})
workspace = resp.json()
ws_id = workspace["workspace_id"]

# Ingest document
resp = httpx.post(f"{API_URL}/v1/workspaces/{ws_id}/extract", headers=headers, json={
    "text": "The conflict between State A and Group B escalated after the bombing...",
    "tier": "standard",
})
job = resp.json()
print(f"Extraction job: {job['job_id']} — status: {job['status']}")

# Query the graph
resp = httpx.get(f"{API_URL}/v1/workspaces/{ws_id}/graph", headers=headers, params={
    "query": "escalation trajectory",
})
graph = resp.json()

# Get analysis
resp = httpx.post(f"{API_URL}/v1/workspaces/{ws_id}/analyze", headers=headers, json={
    "query": "What is the current Glasl escalation stage?",
    "mode": "escalation",
})
analysis = resp.json()
print(analysis["response"])
```

## TypeScript

```typescript
const API_URL = "http://localhost:8080";
const headers = { "X-API-Key": "your-api-key" };

// Create workspace
const ws = await fetch(`${API_URL}/v1/workspaces`, {
  method: "POST",
  headers: { ...headers, "Content-Type": "application/json" },
  body: JSON.stringify({ name: "Analysis", template_id: "human_friction" }),
}).then(r => r.json());

// Ingest text
const job = await fetch(`${API_URL}/v1/workspaces/${ws.workspace_id}/extract`, {
  method: "POST",
  headers: { ...headers, "Content-Type": "application/json" },
  body: JSON.stringify({ text: "Employee A filed a complaint...", tier: "standard" }),
}).then(r => r.json());

console.log(`Job ${job.job_id}: ${job.status}`);
```

## cURL

```bash
# Health check
curl http://localhost:8080/health

# Create workspace
curl -X POST http://localhost:8080/v1/workspaces \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "JCPOA", "template_id": "warfare_political"}'

# Ingest document
curl -X POST http://localhost:8080/v1/workspaces/ws-1/extract \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"text": "Iran signed the JCPOA...", "tier": "full"}'

# List entities
curl http://localhost:8080/v1/workspaces/ws-1/entities \
  -H "X-API-Key: $API_KEY"

# Run analysis
curl -X POST http://localhost:8080/v1/workspaces/ws-1/analyze \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "Who are the key actors?", "mode": "general"}'

# Check extraction job status
curl http://localhost:8080/v1/workspaces/ws-1/extractions/job-id \
  -H "X-API-Key: $API_KEY"
```

## MCP Integration

Connect DIALECTICA as an MCP tool server for Claude, GPT, or any MCP-compatible LLM:

```bash
# Start MCP server
docker-compose up mcp

# Configure in Claude Code
claude mcp add dialectica --transport http --url http://localhost:8090
```

Available MCP tools:
- `query_conflict_graph` — GraphRAG retrieval + synthesis
- `get_actor_analysis` — Actor network + power dynamics
- `get_escalation_status` — Glasl stage + trajectory
- `compare_conflicts` — Cross-case structural similarity
- `ingest_document` — Extract and store
