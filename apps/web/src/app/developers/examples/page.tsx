"use client";

import { useState } from "react";
import { Code2, Copy, Check } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

interface CodeExample {
  title: string;
  description: string;
  tabs: { lang: string; code: string }[];
}

const EXAMPLES: CodeExample[] = [
  {
    title: "List Workspaces",
    description: "Fetch all conflict workspaces your API key has access to.",
    tabs: [
      {
        lang: "Python",
        code: `import requests

API_URL = "${API_URL}"
API_KEY = "your-api-key"

headers = {"X-API-Key": API_KEY}
res = requests.get(f"{API_URL}/v1/workspaces", headers=headers)
res.raise_for_status()

data = res.json()
for ws in data["workspaces"]:
    print(f"{ws['id']:30} {ws['name']}")`,
      },
      {
        lang: "JavaScript",
        code: `const API_URL = "${API_URL}";
const API_KEY = "your-api-key";

const res = await fetch(\`\${API_URL}/v1/workspaces\`, {
  headers: { "X-API-Key": API_KEY },
});

if (!res.ok) throw new Error(\`HTTP \${res.status}\`);
const { workspaces } = await res.json();

workspaces.forEach((ws) => {
  console.log(ws.id, ws.name);
});`,
      },
      {
        lang: "cURL",
        code: `curl "${API_URL}/v1/workspaces" \\
  -H "X-API-Key: your-api-key" \\
  | jq '.workspaces[] | {id, name, domain}'`,
      },
    ],
  },
  {
    title: "Analyze a Conflict",
    description: "Stream an AI analysis of a workspace using the /analyze endpoint (SSE).",
    tabs: [
      {
        lang: "Python",
        code: `import requests

API_URL = "${API_URL}"
API_KEY = "your-api-key"
WORKSPACE_ID = "jcpoa-2015"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json",
    "Accept": "text/event-stream",
}
body = {
    "query": "What are the main escalation drivers?",
    "mode": "escalation",
}

with requests.post(
    f"{API_URL}/v1/workspaces/{WORKSPACE_ID}/analyze",
    headers=headers,
    json=body,
    stream=True,
) as res:
    res.raise_for_status()
    for line in res.iter_lines():
        if line.startswith(b"data: "):
            chunk = line[6:].decode()
            if chunk != "[DONE]":
                print(chunk, end="", flush=True)`,
      },
      {
        lang: "JavaScript",
        code: `const API_URL = "${API_URL}";
const API_KEY = "your-api-key";
const workspaceId = "jcpoa-2015";

const res = await fetch(
  \`\${API_URL}/v1/workspaces/\${workspaceId}/analyze\`,
  {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY,
    },
    body: JSON.stringify({
      query: "What are the main escalation drivers?",
      mode: "escalation",
    }),
  }
);

const reader = res.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  const text = decoder.decode(value);
  for (const line of text.split("\\n")) {
    if (line.startsWith("data: ")) {
      const data = line.slice(6);
      if (data !== "[DONE]") process.stdout.write(data);
    }
  }
}`,
      },
      {
        lang: "cURL",
        code: `curl -N -X POST "${API_URL}/v1/workspaces/jcpoa-2015/analyze" \\
  -H "X-API-Key: your-api-key" \\
  -H "Content-Type: application/json" \\
  -d '{"query": "What are the main escalation drivers?", "mode": "escalation"}'`,
      },
    ],
  },
  {
    title: "Get Escalation Assessment",
    description: "Retrieve the current Glasl escalation stage and trajectory for a workspace.",
    tabs: [
      {
        lang: "Python",
        code: `import requests

API_URL = "${API_URL}"
API_KEY = "your-api-key"
WORKSPACE_ID = "jcpoa-2015"

headers = {"X-API-Key": API_KEY}
res = requests.get(
    f"{API_URL}/v1/workspaces/{WORKSPACE_ID}/escalation",
    headers=headers,
)
res.raise_for_status()

data = res.json()
print(f"Stage: {data['stage_number']} — {data['stage']}")
print(f"Level: {data['level']}")
print(f"Confidence: {data['confidence']:.0%}")
print(f"Forecast: {data['forecast']['direction']}")

for signal in data.get("signals", []):
    print(f"  [{signal['severity']:.1f}] {signal['description']}")`,
      },
      {
        lang: "JavaScript",
        code: `const API_URL = "${API_URL}";
const API_KEY = "your-api-key";
const workspaceId = "jcpoa-2015";

const res = await fetch(
  \`\${API_URL}/v1/workspaces/\${workspaceId}/escalation\`,
  { headers: { "X-API-Key": API_KEY } }
);

const data = await res.json();
console.log(\`Stage \${data.stage_number}: \${data.stage}\`);
console.log(\`Confidence: \${(data.confidence * 100).toFixed(0)}%\`);
console.log(\`Forecast: \${data.forecast.direction}\`);`,
      },
      {
        lang: "cURL",
        code: `curl "${API_URL}/v1/workspaces/jcpoa-2015/escalation" \\
  -H "X-API-Key: your-api-key" \\
  | jq '{stage: .stage_number, level: .level, direction: .forecast.direction}'`,
      },
    ],
  },
  {
    title: "Trust Matrix",
    description: "Get the ABI trust scores between all actor pairs in a workspace.",
    tabs: [
      {
        lang: "Python",
        code: `import requests

API_URL = "${API_URL}"
API_KEY = "your-api-key"
WORKSPACE_ID = "hr-mediation-2023"

res = requests.get(
    f"{API_URL}/v1/workspaces/{WORKSPACE_ID}/trust",
    headers={"X-API-Key": API_KEY},
)
res.raise_for_status()
data = res.json()

print(f"Average trust: {data['average_trust']:.2f}")
if data['lowest_trust_pair']:
    a, b = data['lowest_trust_pair']
    print(f"Lowest trust pair: {a} ↔ {b}")

for dyad in sorted(data['dyads'], key=lambda d: d['overall']):
    print(f"  {dyad['trustor']:20} → {dyad['trustee']:20}  overall={dyad['overall']:.2f}")`,
      },
      {
        lang: "JavaScript",
        code: `const API_URL = "${API_URL}";
const workspaceId = "hr-mediation-2023";

const { dyads, average_trust } = await fetch(
  \`\${API_URL}/v1/workspaces/\${workspaceId}/trust\`,
  { headers: { "X-API-Key": "your-api-key" } }
).then((r) => r.json());

console.log(\`Average trust: \${average_trust.toFixed(2)}\`);
dyads
  .sort((a, b) => a.overall - b.overall)
  .forEach((d) =>
    console.log(\`\${d.trustor} → \${d.trustee}: \${d.overall.toFixed(2)}\`)
  );`,
      },
      {
        lang: "cURL",
        code: `curl "${API_URL}/v1/workspaces/hr-mediation-2023/trust" \\
  -H "X-API-Key: your-api-key" \\
  | jq '.dyads | sort_by(.overall) | .[] | {trustor, trustee, overall}'`,
      },
    ],
  },
];

function CodeBlock({ code, lang }: { code: string; lang: string }) {
  const [copied, setCopied] = useState(false);

  function handleCopy() {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <div className="bg-[#09090b] border border-[#27272a] rounded-lg overflow-hidden">
      <div className="flex items-center justify-between px-4 py-2 border-b border-[#27272a] bg-[#18181b]">
        <span className="text-[#52525b] text-xs font-mono">{lang}</span>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1 p-1 rounded text-[#52525b] hover:text-[#a1a1aa] transition-colors"
          title="Copy code"
        >
          {copied ? <Check size={12} className="text-green-400" /> : <Copy size={12} />}
          <span className="text-xs">{copied ? "Copied" : "Copy"}</span>
        </button>
      </div>
      <pre className="p-4 text-xs font-mono text-[#a1a1aa] overflow-x-auto leading-relaxed">
        <code>{code}</code>
      </pre>
    </div>
  );
}

function ExampleCard({ example }: { example: CodeExample }) {
  const [activeTab, setActiveTab] = useState(0);

  return (
    <div className="bg-[#18181b] border border-[#27272a] rounded-lg overflow-hidden">
      <div className="px-5 py-4 border-b border-[#27272a]">
        <h3 className="text-[#fafafa] text-sm font-semibold mb-1">{example.title}</h3>
        <p className="text-[#71717a] text-xs">{example.description}</p>
      </div>
      <div className="p-4">
        <div className="flex gap-1 mb-3">
          {example.tabs.map((tab, i) => (
            <button
              key={tab.lang}
              onClick={() => setActiveTab(i)}
              className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
                activeTab === i
                  ? "bg-[#27272a] text-[#fafafa]"
                  : "text-[#71717a] hover:text-[#a1a1aa] hover:bg-[#27272a]/50"
              }`}
            >
              {tab.lang}
            </button>
          ))}
        </div>
        <CodeBlock code={example.tabs[activeTab].code} lang={example.tabs[activeTab].lang} />
      </div>
    </div>
  );
}

export default function ExamplesPage() {
  return (
    <div className="p-8 max-w-4xl">
      <div className="mb-8">
        <div className="flex items-center gap-2 mb-2">
          <Code2 size={18} className="text-[#71717a]" />
          <h1 className="text-2xl font-bold text-[#fafafa]">Code Examples</h1>
        </div>
        <p className="text-[#a1a1aa] text-sm">
          Ready-to-run examples in Python, JavaScript, and cURL. Replace{" "}
          <code className="font-mono text-[#fafafa] text-xs bg-[#18181b] border border-[#27272a] rounded px-1.5 py-0.5">your-api-key</code>{" "}
          with your actual key from the{" "}
          <a href="/developers/keys" className="text-teal-400 hover:text-teal-300 underline">
            API Keys page
          </a>.
        </p>
      </div>

      <div className="space-y-6">
        {EXAMPLES.map((ex) => (
          <ExampleCard key={ex.title} example={ex} />
        ))}
      </div>
    </div>
  );
}
