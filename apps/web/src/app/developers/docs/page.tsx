"use client";

import { FileCode } from "lucide-react";

const ENDPOINTS = [
  { method: "GET", path: "/health", desc: "Health check" },
  { method: "POST", path: "/v1/workspaces", desc: "Create workspace" },
  { method: "GET", path: "/v1/workspaces", desc: "List workspaces" },
  { method: "GET", path: "/v1/workspaces/:id", desc: "Get workspace" },
  { method: "POST", path: "/v1/extract", desc: "Extract entities from text" },
  { method: "GET", path: "/v1/workspaces/:id/graph", desc: "Get full graph" },
  { method: "GET", path: "/v1/workspaces/:id/entities", desc: "List entities" },
  { method: "POST", path: "/v1/analyze", desc: "Run conflict analysis" },
  { method: "GET", path: "/v1/analyze/stream", desc: "Streaming analysis (SSE)" },
  { method: "GET", path: "/v1/theory/frameworks", desc: "List theory frameworks" },
  { method: "POST", path: "/v1/theory/match", desc: "Match theory to workspace" },
  { method: "GET", path: "/v1/theory/graph", desc: "Theory knowledge graph" },
];

export default function DocsPage() {
  return (
    <div className="max-w-3xl space-y-6">
      <h1 className="text-2xl font-bold text-text-primary flex items-center gap-2">
        <FileCode size={24} /> API Documentation
      </h1>

      <div className="card">
        <h3 className="font-semibold text-text-primary mb-2">Authentication</h3>
        <p className="text-sm text-text-secondary mb-2">All requests require an API key in the <code className="text-accent bg-accent/10 px-1 rounded">X-API-Key</code> header.</p>
        <pre className="text-sm font-mono text-text-primary bg-background rounded p-3">
          {`curl -H "X-API-Key: your-api-key" https://api.dialectica.tacitus.ai/v1/workspaces`}
        </pre>
      </div>

      <div className="card">
        <h3 className="font-semibold text-text-primary mb-3">Endpoints</h3>
        <div className="space-y-2">
          {ENDPOINTS.map((ep) => (
            <div key={ep.path + ep.method} className="flex items-center gap-3 text-sm">
              <span className={`badge font-mono text-[10px] w-14 text-center ${ep.method === "GET" ? "bg-accent/10 text-accent" : "bg-warning/10 text-warning"}`}>
                {ep.method}
              </span>
              <code className="text-text-primary font-mono flex-1">{ep.path}</code>
              <span className="text-text-secondary">{ep.desc}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="card">
        <h3 className="font-semibold text-text-primary mb-2">Rate Limits</h3>
        <div className="text-sm text-text-secondary space-y-1">
          <p>Default: 60 requests/minute</p>
          <p>Extraction: 10 requests/minute</p>
          <p>Analysis: 20 requests/minute</p>
        </div>
      </div>
    </div>
  );
}
