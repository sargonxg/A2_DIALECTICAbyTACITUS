"use client";

import { useState } from "react";
import { Play, Copy } from "lucide-react";

const ENDPOINTS = [
  { label: "Health Check", method: "GET", path: "/health", body: "" },
  { label: "List Workspaces", method: "GET", path: "/v1/workspaces", body: "" },
  { label: "Create Workspace", method: "POST", path: "/v1/workspaces", body: '{\n  "name": "Test Workspace",\n  "domain": "workplace",\n  "scale": "meso",\n  "tier": "standard"\n}' },
  { label: "Extract Entities", method: "POST", path: "/v1/extract", body: '{\n  "workspace_id": "WORKSPACE_ID",\n  "text": "The two parties have reached a stalemate...",\n  "tier": "standard"\n}' },
];

export default function PlaygroundPage() {
  const [selected, setSelected] = useState(0);
  const [body, setBody] = useState(ENDPOINTS[0].body);
  const [response, setResponse] = useState<string | null>(null);

  const handleSelect = (i: number) => {
    setSelected(i);
    setBody(ENDPOINTS[i].body);
    setResponse(null);
  };

  const handleSend = async () => {
    const ep = ENDPOINTS[selected];
    setResponse(`// Response from ${ep.method} ${ep.path}\n// (Connect to running API to see real responses)\n{\n  "status": "ok"\n}`);
  };

  const ep = ENDPOINTS[selected];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-text-primary flex items-center gap-2">
        <Play size={24} /> API Playground
      </h1>

      <div className="flex gap-2 flex-wrap">
        {ENDPOINTS.map((e, i) => (
          <button key={i} onClick={() => handleSelect(i)} className={`badge ${i === selected ? "bg-accent/20 text-accent" : "bg-surface-hover text-text-secondary"}`}>
            {e.label}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className={`badge font-mono text-[10px] ${ep.method === "GET" ? "bg-accent/10 text-accent" : "bg-warning/10 text-warning"}`}>{ep.method}</span>
            <code className="text-sm text-text-primary font-mono">{ep.path}</code>
          </div>
          {ep.body && <textarea value={body} onChange={(e) => setBody(e.target.value)} rows={10} className="input-base w-full font-mono text-sm" />}
          <button onClick={handleSend} className="btn-primary flex items-center gap-2">
            <Play size={14} /> Send Request
          </button>
        </div>

        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-text-secondary">Response</span>
            {response && <button className="btn-ghost text-xs"><Copy size={12} /> Copy</button>}
          </div>
          <pre className="card font-mono text-sm text-text-primary overflow-auto h-64">
            {response || "// Send a request to see the response"}
          </pre>
        </div>
      </div>
    </div>
  );
}
