'use client';

export default function SDKsPage() {
  return (
    <div className="p-6 space-y-8 max-w-4xl">
      <h1 className="text-2xl font-bold text-white">SDKs & Client Libraries</h1>

      <section className="space-y-4">
        <h2 className="text-lg font-semibold text-white">Python SDK</h2>
        <pre className="bg-[#0d0d0f] border border-[#27272a] rounded-lg p-4 text-sm font-mono text-green-400">
          pip install dialectica-client
        </pre>
        <pre className="bg-[#0d0d0f] border border-[#27272a] rounded-lg p-4 text-sm font-mono text-green-400">
{`from dialectica import DialecticaClient

client = DialecticaClient(
    api_url="http://localhost:8080",
    api_key="your-api-key",
)

# List workspaces
workspaces = client.workspaces.list()

# Analyze
response = client.analyze(
    workspace_id="ws-123",
    query="What is the escalation trajectory?",
    mode="escalation",
)`}
        </pre>
      </section>

      <section className="space-y-4">
        <h2 className="text-lg font-semibold text-white">JavaScript / TypeScript SDK</h2>
        <pre className="bg-[#0d0d0f] border border-[#27272a] rounded-lg p-4 text-sm font-mono text-green-400">
          npm install @dialectica/client
        </pre>
        <pre className="bg-[#0d0d0f] border border-[#27272a] rounded-lg p-4 text-sm font-mono text-green-400">
{`import { DialecticaClient } from '@dialectica/client';

const client = new DialecticaClient({
  apiUrl: 'http://localhost:8080',
  apiKey: 'your-api-key',
});

const workspaces = await client.workspaces.list();
const escalation = await client.reasoning.getEscalation(workspaceId);`}
        </pre>
      </section>

      <section className="bg-[#18181b] border border-[#27272a] rounded-lg p-4">
        <p className="text-[#a1a1aa] text-sm">
          SDK packages are not yet published to PyPI / npm. The API client source
          is available in <code className="font-mono text-teal-400">apps/web/src/lib/api.ts</code> and
          can be used as a reference implementation for custom integrations.
        </p>
      </section>
    </div>
  );
}
