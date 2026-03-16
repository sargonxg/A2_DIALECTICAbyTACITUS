"use client";

import { useState, useCallback } from "react";
import { Send, Loader2, Copy, Check, Trash2, ChevronDown } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

type HttpMethod = "GET" | "POST" | "PUT" | "DELETE" | "PATCH";

const METHOD_COLORS: Record<HttpMethod, string> = {
  GET: "text-green-400 bg-green-500/10 border-green-500/30",
  POST: "text-blue-400 bg-blue-500/10 border-blue-500/30",
  PUT: "text-yellow-400 bg-yellow-500/10 border-yellow-500/30",
  DELETE: "text-red-400 bg-red-500/10 border-red-500/30",
  PATCH: "text-orange-400 bg-orange-500/10 border-orange-500/30",
};

const PRESET_REQUESTS = [
  { label: "List Workspaces", method: "GET" as HttpMethod, path: "/v1/workspaces", body: "" },
  { label: "Health Check", method: "GET" as HttpMethod, path: "/health", body: "" },
  { label: "List Frameworks", method: "GET" as HttpMethod, path: "/v1/theory/frameworks", body: "" },
  { label: "Create Workspace", method: "POST" as HttpMethod, path: "/v1/workspaces", body: JSON.stringify({ name: "My Conflict", domain: "diplomatic", scale: "international" }, null, 2) },
];

function getStatusColor(status: number): string {
  if (status >= 200 && status < 300) return "text-green-400";
  if (status >= 300 && status < 400) return "text-blue-400";
  if (status >= 400 && status < 500) return "text-yellow-400";
  return "text-red-400";
}

export default function PlaygroundPage() {
  const [method, setMethod] = useState<HttpMethod>("GET");
  const [path, setPath] = useState("/v1/workspaces");
  const [body, setBody] = useState("");
  const [response, setResponse] = useState<string | null>(null);
  const [responseStatus, setResponseStatus] = useState<number | null>(null);
  const [responseTime, setResponseTime] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [showPresets, setShowPresets] = useState(false);

  const send = useCallback(async () => {
    setLoading(true);
    setError(null);
    setResponse(null);
    setResponseStatus(null);
    setResponseTime(null);

    const apiKey = localStorage.getItem("dialectica_api_key") || "";
    const start = performance.now();

    try {
      const opts: RequestInit = {
        method,
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": apiKey,
        },
      };
      if (method !== "GET" && method !== "DELETE" && body.trim()) {
        opts.body = body;
      }

      const url = `${API_URL}${path.startsWith("/") ? path : "/" + path}`;
      const res = await fetch(url, opts);
      const elapsed = Math.round(performance.now() - start);
      setResponseTime(elapsed);
      setResponseStatus(res.status);

      const text = await res.text();
      try {
        const parsed = JSON.parse(text);
        setResponse(JSON.stringify(parsed, null, 2));
      } catch {
        setResponse(text);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
      setResponseTime(Math.round(performance.now() - start));
    } finally {
      setLoading(false);
    }
  }, [method, path, body]);

  function handleCopy() {
    if (!response) return;
    navigator.clipboard.writeText(response);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  function applyPreset(preset: (typeof PRESET_REQUESTS)[0]) {
    setMethod(preset.method);
    setPath(preset.path);
    setBody(preset.body);
    setShowPresets(false);
  }

  return (
    <div className="p-8 max-w-5xl">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-[#fafafa] mb-1">API Playground</h1>
        <p className="text-[#a1a1aa] text-sm">
          Make live requests to the DIALECTICA API. Your stored API key is used automatically.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Request panel */}
        <div className="space-y-4">
          <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-[#fafafa] text-sm font-semibold">Request</h2>
              <div className="relative">
                <button
                  onClick={() => setShowPresets((v) => !v)}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-[#27272a] hover:bg-[#3f3f46] text-[#a1a1aa] text-xs transition-colors"
                >
                  Presets <ChevronDown size={12} />
                </button>
                {showPresets && (
                  <div className="absolute right-0 top-8 z-10 bg-[#18181b] border border-[#27272a] rounded-lg shadow-xl min-w-48 overflow-hidden">
                    {PRESET_REQUESTS.map((preset) => (
                      <button
                        key={preset.label}
                        onClick={() => applyPreset(preset)}
                        className="w-full flex items-center gap-2 px-3 py-2.5 hover:bg-[#27272a] text-left transition-colors"
                      >
                        <span className={`text-xs font-mono font-semibold px-1.5 py-0.5 rounded border ${METHOD_COLORS[preset.method]}`}>
                          {preset.method}
                        </span>
                        <span className="text-[#a1a1aa] text-xs truncate">{preset.label}</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Method + path */}
            <div className="flex gap-2 mb-3">
              <div className="relative">
                <select
                  value={method}
                  onChange={(e) => setMethod(e.target.value as HttpMethod)}
                  className="appearance-none bg-[#09090b] border border-[#27272a] rounded-md pl-3 pr-7 py-2 text-sm font-mono focus:outline-none focus:border-teal-600 cursor-pointer"
                  style={{ color: method === "GET" ? "#4ade80" : method === "POST" ? "#60a5fa" : method === "DELETE" ? "#f87171" : "#fbbf24" }}
                >
                  {(["GET", "POST", "PUT", "PATCH", "DELETE"] as HttpMethod[]).map((m) => (
                    <option key={m} value={m} className="text-[#fafafa] bg-[#09090b]">{m}</option>
                  ))}
                </select>
                <ChevronDown size={12} className="absolute right-2 top-1/2 -translate-y-1/2 text-[#52525b] pointer-events-none" />
              </div>
              <input
                type="text"
                value={path}
                onChange={(e) => setPath(e.target.value)}
                placeholder="/v1/workspaces"
                className="flex-1 bg-[#09090b] border border-[#27272a] rounded-md px-3 py-2 text-sm text-[#fafafa] placeholder-[#52525b] font-mono focus:outline-none focus:border-teal-600"
              />
            </div>

            {/* API URL display */}
            <p className="text-[#52525b] text-xs font-mono mb-3 truncate">
              {API_URL}{path}
            </p>

            {/* Body */}
            {method !== "GET" && method !== "DELETE" && (
              <div>
                <p className="text-[#71717a] text-xs mb-1.5">Request Body (JSON)</p>
                <textarea
                  value={body}
                  onChange={(e) => setBody(e.target.value)}
                  rows={8}
                  placeholder='{"key": "value"}'
                  className="w-full bg-[#09090b] border border-[#27272a] rounded-md px-3 py-2 text-xs text-[#a1a1aa] placeholder-[#52525b] font-mono focus:outline-none focus:border-teal-600 resize-y"
                />
              </div>
            )}

            <button
              onClick={send}
              disabled={loading}
              className="mt-3 w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-md bg-teal-600 hover:bg-teal-500 text-white text-sm font-medium transition-colors disabled:opacity-60"
            >
              {loading ? <Loader2 size={14} className="animate-spin" /> : <Send size={14} />}
              {loading ? "Sending…" : "Send Request"}
            </button>
          </div>
        </div>

        {/* Response panel */}
        <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-[#fafafa] text-sm font-semibold">Response</h2>
            <div className="flex items-center gap-3">
              {responseStatus !== null && (
                <span className={`text-xs font-mono font-semibold ${getStatusColor(responseStatus)}`}>
                  HTTP {responseStatus}
                </span>
              )}
              {responseTime !== null && (
                <span className="text-[#52525b] text-xs font-mono">{responseTime}ms</span>
              )}
              {response && (
                <button
                  onClick={handleCopy}
                  className="p-1.5 rounded-md text-[#71717a] hover:text-[#fafafa] hover:bg-[#27272a] transition-colors"
                  title="Copy response"
                >
                  {copied ? <Check size={12} className="text-green-400" /> : <Copy size={12} />}
                </button>
              )}
              {response && (
                <button
                  onClick={() => { setResponse(null); setResponseStatus(null); setResponseTime(null); }}
                  className="p-1.5 rounded-md text-[#71717a] hover:text-[#fafafa] hover:bg-[#27272a] transition-colors"
                  title="Clear response"
                >
                  <Trash2 size={12} />
                </button>
              )}
            </div>
          </div>

          {loading ? (
            <div className="flex items-center gap-2 text-[#71717a] text-sm py-8">
              <Loader2 size={14} className="animate-spin" /> Waiting for response…
            </div>
          ) : error ? (
            <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-md">
              <p className="text-red-400 text-xs font-mono">{error}</p>
            </div>
          ) : response ? (
            <div className="bg-[#09090b] border border-[#27272a] rounded-md overflow-hidden">
              <pre className="p-4 text-xs font-mono text-[#a1a1aa] overflow-auto max-h-[500px] leading-relaxed">
                <code>{response}</code>
              </pre>
            </div>
          ) : (
            <div className="py-12 text-center">
              <p className="text-[#52525b] text-sm">Response will appear here</p>
              <p className="text-[#3f3f46] text-xs mt-1">Send a request to get started</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
