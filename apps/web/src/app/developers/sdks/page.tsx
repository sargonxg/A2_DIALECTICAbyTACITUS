"use client";

import { useState } from "react";
import { Package, Copy, Check, ExternalLink, Terminal } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      onClick={() => {
        navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      }}
      className="flex items-center gap-1 p-1.5 rounded text-[#52525b] hover:text-[#a1a1aa] hover:bg-[#27272a] transition-colors"
      title="Copy"
    >
      {copied ? <Check size={12} className="text-green-400" /> : <Copy size={12} />}
    </button>
  );
}

function CodeBlock({ code, lang }: { code: string; lang: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <div className="bg-[#09090b] border border-[#27272a] rounded-lg overflow-hidden">
      <div className="flex items-center justify-between px-4 py-2 border-b border-[#27272a] bg-[#18181b]">
        <span className="text-[#52525b] text-xs font-mono">{lang}</span>
        <button
          onClick={() => {
            navigator.clipboard.writeText(code);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
          }}
          className="flex items-center gap-1 p-1 rounded text-[#52525b] hover:text-[#a1a1aa] transition-colors"
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

const PYTHON_INSTALL = `pip install dialectica-client`;

const PYTHON_USAGE = `from dialectica import DialecticaClient

client = DialecticaClient(
    api_url="${API_URL}",
    api_key="your-api-key",
)

# List workspaces
workspaces = client.workspaces.list()
for ws in workspaces:
    print(ws.name, ws.domain)

# Analyze a workspace
for chunk in client.analyze(
    workspace_id="jcpoa-2015",
    query="What are the escalation drivers?",
    mode="escalation",
):
    print(chunk, end="", flush=True)

# Get escalation stage
escalation = client.workspaces.escalation("jcpoa-2015")
print(f"Stage {escalation.stage_number}: {escalation.stage}")
print(f"Forecast: {escalation.forecast.direction}")

# Trust matrix
trust = client.workspaces.trust("hr-mediation-2023")
print(f"Average trust: {trust.average_trust:.2f}")`;

const PYTHON_ASYNC = `import asyncio
from dialectica.async_client import AsyncDialecticaClient

async def main():
    async with AsyncDialecticaClient(
        api_url="${API_URL}",
        api_key="your-api-key",
    ) as client:
        workspaces = await client.workspaces.list()
        print(f"Found {len(workspaces)} workspaces")

        # Parallel quality checks
        quality_results = await asyncio.gather(*[
            client.workspaces.quality(ws.id)
            for ws in workspaces
        ])
        for ws, q in zip(workspaces, quality_results):
            print(f"{ws.name}: {q.overall_quality:.0%}")

asyncio.run(main())`;

const TS_INSTALL = `npm install @dialectica/client
# or
yarn add @dialectica/client
# or
pnpm add @dialectica/client`;

const TS_USAGE = `import { DialecticaClient } from "@dialectica/client";

const client = new DialecticaClient({
  apiUrl: "${API_URL}",
  apiKey: process.env.DIALECTICA_API_KEY!,
});

// List workspaces
const { workspaces } = await client.workspaces.list();
console.log(\`\${workspaces.length} workspaces\`);

// Get escalation
const escalation = await client.workspaces.getEscalation("jcpoa-2015");
console.log(\`Stage \${escalation.stageNumber}: \${escalation.stage}\`);
console.log(\`Forecast: \${escalation.forecast.direction}\`);

// Stream analysis
for await (const chunk of client.workspaces.streamAnalyze("jcpoa-2015", {
  query: "What intervention would reduce escalation?",
  mode: "negotiation",
})) {
  process.stdout.write(chunk);
}`;

const TS_REACT = `"use client";

import { useEffect, useState } from "react";
import { DialecticaClient } from "@dialectica/client";

const client = new DialecticaClient({
  apiUrl: process.env.NEXT_PUBLIC_API_URL!,
  apiKey: localStorage.getItem("dialectica_api_key") ?? "",
});

export function EscalationBadge({ workspaceId }: { workspaceId: string }) {
  const [stage, setStage] = useState<number | null>(null);

  useEffect(() => {
    client.workspaces
      .getEscalation(workspaceId)
      .then((e) => setStage(e.stageNumber))
      .catch(console.error);
  }, [workspaceId]);

  if (stage === null) return <span>Loading…</span>;
  return <span>Glasl Stage {stage}</span>;
}`;

export default function SdksPage() {
  return (
    <div className="p-8 max-w-4xl">
      <div className="mb-8">
        <div className="flex items-center gap-2 mb-2">
          <Package size={18} className="text-[#71717a]" />
          <h1 className="text-2xl font-bold text-[#fafafa]">SDKs &amp; Clients</h1>
        </div>
        <p className="text-[#a1a1aa] text-sm">
          Official client libraries for Python and TypeScript/JavaScript.
        </p>
      </div>

      {/* Python SDK */}
      <div className="mb-10">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-md bg-blue-500/10">
              <span className="text-blue-400 text-sm font-bold font-mono">Py</span>
            </div>
            <div>
              <h2 className="text-[#fafafa] font-semibold text-base">Python SDK</h2>
              <p className="text-[#52525b] text-xs font-mono">dialectica-client</p>
            </div>
          </div>
          <a
            href="https://github.com/tacitus-ai/dialectica-python"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-[#27272a] hover:bg-[#3f3f46] text-[#a1a1aa] text-xs transition-colors"
          >
            <ExternalLink size={12} />
            GitHub
          </a>
        </div>

        {/* Install */}
        <div className="mb-4">
          <p className="text-[#71717a] text-xs uppercase tracking-wider mb-2">Installation</p>
          <div className="flex items-center gap-2 bg-[#09090b] border border-[#27272a] rounded-lg px-4 py-3">
            <Terminal size={14} className="text-[#52525b]" />
            <code className="text-teal-400 text-sm font-mono flex-1">{PYTHON_INSTALL}</code>
            <CopyButton text={PYTHON_INSTALL} />
          </div>
        </div>

        {/* Requirements */}
        <div className="flex gap-3 mb-4">
          {[
            { label: "Python", value: "≥ 3.9" },
            { label: "License", value: "MIT" },
            { label: "Dependencies", value: "httpx, pydantic" },
          ].map((item) => (
            <div key={item.label} className="bg-[#18181b] border border-[#27272a] rounded-md px-3 py-2 text-xs">
              <span className="text-[#52525b]">{item.label}: </span>
              <span className="text-[#a1a1aa] font-mono">{item.value}</span>
            </div>
          ))}
        </div>

        <div className="space-y-3">
          <div>
            <p className="text-[#71717a] text-xs uppercase tracking-wider mb-2">Basic Usage</p>
            <CodeBlock code={PYTHON_USAGE} lang="Python" />
          </div>
          <div>
            <p className="text-[#71717a] text-xs uppercase tracking-wider mb-2">Async Client</p>
            <CodeBlock code={PYTHON_ASYNC} lang="Python (async)" />
          </div>
        </div>
      </div>

      {/* TypeScript SDK */}
      <div className="mb-10">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-md bg-yellow-500/10">
              <span className="text-yellow-400 text-sm font-bold font-mono">TS</span>
            </div>
            <div>
              <h2 className="text-[#fafafa] font-semibold text-base">TypeScript / JavaScript SDK</h2>
              <p className="text-[#52525b] text-xs font-mono">@dialectica/client</p>
            </div>
          </div>
          <a
            href="https://github.com/tacitus-ai/dialectica-js"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-[#27272a] hover:bg-[#3f3f46] text-[#a1a1aa] text-xs transition-colors"
          >
            <ExternalLink size={12} />
            GitHub
          </a>
        </div>

        <div className="mb-4">
          <p className="text-[#71717a] text-xs uppercase tracking-wider mb-2">Installation</p>
          <div className="bg-[#09090b] border border-[#27272a] rounded-lg overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-[#27272a] bg-[#18181b]">
              <span className="text-[#52525b] text-xs font-mono">shell</span>
              <CopyButton text="npm install @dialectica/client" />
            </div>
            <pre className="p-4 text-xs font-mono text-[#a1a1aa]">
              <code>{TS_INSTALL}</code>
            </pre>
          </div>
        </div>

        <div className="flex gap-3 mb-4">
          {[
            { label: "Runtime", value: "Node ≥ 18 / Browser" },
            { label: "License", value: "MIT" },
            { label: "Exports", value: "ESM + CJS" },
          ].map((item) => (
            <div key={item.label} className="bg-[#18181b] border border-[#27272a] rounded-md px-3 py-2 text-xs">
              <span className="text-[#52525b]">{item.label}: </span>
              <span className="text-[#a1a1aa] font-mono">{item.value}</span>
            </div>
          ))}
        </div>

        <div className="space-y-3">
          <div>
            <p className="text-[#71717a] text-xs uppercase tracking-wider mb-2">Node.js / Server</p>
            <CodeBlock code={TS_USAGE} lang="TypeScript" />
          </div>
          <div>
            <p className="text-[#71717a] text-xs uppercase tracking-wider mb-2">React / Next.js</p>
            <CodeBlock code={TS_REACT} lang="TypeScript (React)" />
          </div>
        </div>
      </div>

      {/* Community note */}
      <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-5">
        <h2 className="text-[#fafafa] text-sm font-semibold mb-2">Community & Contributing</h2>
        <p className="text-[#71717a] text-sm leading-relaxed mb-3">
          SDKs are open source under the MIT license. Contributions, bug reports, and feature 
          requests are welcome via GitHub Issues.
        </p>
        <div className="flex flex-wrap gap-2">
          {[
            { label: "Python SDK Issues", href: "https://github.com/tacitus-ai/dialectica-python/issues" },
            { label: "JS SDK Issues", href: "https://github.com/tacitus-ai/dialectica-js/issues" },
            { label: "API Docs", href: "/developers/docs" },
          ].map((link) => (
            <a
              key={link.label}
              href={link.href}
              target={link.href.startsWith("http") ? "_blank" : undefined}
              rel={link.href.startsWith("http") ? "noopener noreferrer" : undefined}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-[#27272a] hover:bg-[#3f3f46] text-[#a1a1aa] hover:text-[#fafafa] text-xs transition-colors"
            >
              {link.href.startsWith("http") && <ExternalLink size={11} />}
              {link.label}
            </a>
          ))}
        </div>
      </div>
    </div>
  );
}
