'use client';

const EXAMPLES = [
  {
    title: 'List all workspaces',
    python: `import requests
r = requests.get("http://localhost:8080/v1/workspaces",
    headers={"X-API-Key": "your-key"})
print(r.json())`,
    js: `const res = await fetch('/v1/workspaces', {
  headers: { 'X-API-Key': 'your-key' }
});
const { workspaces } = await res.json();`,
    curl: `curl -H "X-API-Key: your-key" \\
  http://localhost:8080/v1/workspaces`,
  },
  {
    title: 'Analyze a conflict (streaming)',
    python: `import requests

resp = requests.post(
    f"http://localhost:8080/v1/workspaces/{workspace_id}/analyze",
    headers={"X-API-Key": "your-key"},
    json={"query": "What is the escalation trajectory?", "mode": "escalation"},
    stream=True,
)
for line in resp.iter_lines():
    if line.startswith(b"data: "):
        print(line[6:].decode())`,
    js: `const res = await fetch(\`/v1/workspaces/\${id}/analyze\`, {
  method: 'POST',
  headers: { 'X-API-Key': 'your-key', 'Content-Type': 'application/json' },
  body: JSON.stringify({ query: 'What is the escalation?', mode: 'escalation' }),
});
const reader = res.body.getReader();
// read SSE stream...`,
    curl: `curl -X POST \\
  -H "X-API-Key: your-key" \\
  -H "Content-Type: application/json" \\
  -d '{"query":"What is the escalation?","mode":"escalation"}' \\
  http://localhost:8080/v1/workspaces/{id}/analyze`,
  },
  {
    title: 'Get escalation assessment',
    python: `r = requests.get(
    f"http://localhost:8080/v1/workspaces/{workspace_id}/escalation",
    headers={"X-API-Key": "your-key"},
)
assessment = r.json()
print(f"Stage: {assessment['stage_number']}, Level: {assessment['level']}")`,
    js: `const data = await fetch(\`/v1/workspaces/\${id}/escalation\`, {
  headers: { 'X-API-Key': 'your-key' }
}).then(r => r.json());
console.log(data.stage_number, data.level);`,
    curl: `curl -H "X-API-Key: your-key" \\
  http://localhost:8080/v1/workspaces/{id}/escalation`,
  },
];

function CodeBlock({ code, lang }: { code: string; lang: string }) {
  return (
    <div>
      <div className="text-xs text-[#71717a] mb-1">{lang}</div>
      <pre className="bg-[#0d0d0f] border border-[#27272a] rounded p-3 text-xs font-mono text-green-400 overflow-x-auto whitespace-pre">
        {code}
      </pre>
    </div>
  );
}

export default function ExamplesPage() {
  return (
    <div className="p-6 space-y-8 max-w-4xl">
      <h1 className="text-2xl font-bold text-white">Code Examples</h1>
      {EXAMPLES.map((ex) => (
        <section key={ex.title} className="space-y-3">
          <h2 className="text-base font-semibold text-white border-b border-[#27272a] pb-2">{ex.title}</h2>
          <div className="grid grid-cols-1 gap-3">
            <CodeBlock code={ex.python} lang="Python" />
            <CodeBlock code={ex.js} lang="JavaScript" />
            <CodeBlock code={ex.curl} lang="cURL" />
          </div>
        </section>
      ))}
    </div>
  );
}
