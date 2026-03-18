"use client";

import Link from "next/link";
import { Code2, Network, Brain, Layers, ArrowRight } from "lucide-react";

const FEATURES = [
  { icon: Network, title: "Entity Extraction", desc: "Extract conflict entities from text using Gemini + GLiNER" },
  { icon: Code2, title: "Graph Queries", desc: "Query and traverse conflict knowledge graphs" },
  { icon: Brain, title: "Conflict Analysis", desc: "AI-powered analysis with 15 theory frameworks" },
  { icon: Layers, title: "Theory Assessment", desc: "Match conflicts to theoretical frameworks" },
];

const SNIPPETS = {
  python: `from dialectica import Client

client = Client(api_key="your-key")
ws = client.workspaces.create(
    name="Syria Analysis",
    domain="armed", scale="macro", tier="full"
)
result = client.extract(ws.id, text="...")
analysis = client.analyze(ws.id, query="What is the escalation level?")`,
  curl: `curl -X POST https://api.dialectica.tacitus.ai/v1/workspaces \\
  -H "X-API-Key: your-key" \\
  -H "Content-Type: application/json" \\
  -d '{"name":"Syria Analysis","domain":"armed","scale":"macro","tier":"full"}'`,
};

export default function DevelopersPage() {
  return (
    <div className="space-y-8">
      <div className="text-center max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold text-text-primary mb-2">Build on DIALECTICA</h1>
        <p className="text-text-secondary">The conflict analysis API for researchers, mediators, and developers.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-3xl mx-auto">
        {FEATURES.map((f) => (
          <div key={f.title} className="card">
            <f.icon size={20} className="text-accent mb-2" />
            <h3 className="font-semibold text-text-primary">{f.title}</h3>
            <p className="text-sm text-text-secondary">{f.desc}</p>
          </div>
        ))}
      </div>

      <div className="max-w-3xl mx-auto space-y-4">
        <h2 className="text-lg font-semibold text-text-primary">Quick Start</h2>
        <div className="card">
          <p className="text-xs text-text-secondary mb-2 font-mono">Python</p>
          <pre className="text-sm text-text-primary font-mono overflow-x-auto whitespace-pre">{SNIPPETS.python}</pre>
        </div>
        <div className="card">
          <p className="text-xs text-text-secondary mb-2 font-mono">curl</p>
          <pre className="text-sm text-text-primary font-mono overflow-x-auto whitespace-pre">{SNIPPETS.curl}</pre>
        </div>
      </div>

      <div className="flex gap-4 justify-center">
        <Link href="/developers/docs" className="btn-primary flex items-center gap-2">API Docs <ArrowRight size={16} /></Link>
        <Link href="/developers/playground" className="btn-secondary">Playground</Link>
        <Link href="/developers/keys" className="btn-secondary">Get API Key</Link>
      </div>
    </div>
  );
}
