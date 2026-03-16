"use client";

import { useState } from "react";
import { BookOpen, ChevronDown, ChevronRight } from "lucide-react";

type HttpMethod = "GET" | "POST" | "PUT" | "DELETE" | "PATCH";

interface Param {
  name: string;
  in: "path" | "query" | "body";
  type: string;
  required: boolean;
  description: string;
}

interface Endpoint {
  method: HttpMethod;
  path: string;
  summary: string;
  description: string;
  params: Param[];
  responseExample?: string;
}

interface EndpointGroup {
  tag: string;
  description: string;
  endpoints: Endpoint[];
}

const METHOD_COLORS: Record<HttpMethod, string> = {
  GET: "text-green-400 bg-green-500/10 border-green-500/30",
  POST: "text-blue-400 bg-blue-500/10 border-blue-500/30",
  PUT: "text-yellow-400 bg-yellow-500/10 border-yellow-500/30",
  DELETE: "text-red-400 bg-red-500/10 border-red-500/30",
  PATCH: "text-orange-400 bg-orange-500/10 border-orange-500/30",
};

const API_SPEC: EndpointGroup[] = [
  {
    tag: "Workspaces",
    description: "Manage conflict workspaces — the top-level containers for all graph data.",
    endpoints: [
      {
        method: "GET",
        path: "/v1/workspaces",
        summary: "List all workspaces",
        description: "Returns a paginated list of all workspaces the API key has access to.",
        params: [
          { name: "limit", in: "query", type: "integer", required: false, description: "Max results to return (default 100)" },
          { name: "offset", in: "query", type: "integer", required: false, description: "Pagination offset" },
        ],
        responseExample: `{ "workspaces": [...], "total": 3 }`,
      },
      {
        method: "POST",
        path: "/v1/workspaces",
        summary: "Create a workspace",
        description: "Creates a new workspace with the given metadata.",
        params: [
          { name: "name", in: "body", type: "string", required: true, description: "Human-readable workspace name" },
          { name: "domain", in: "body", type: "string", required: true, description: "Conflict domain: diplomatic, commercial, organizational, interpersonal" },
          { name: "scale", in: "body", type: "string", required: true, description: "Scale: international, national, organizational, interpersonal" },
        ],
      },
      {
        method: "GET",
        path: "/v1/workspaces/{id}",
        summary: "Get workspace",
        description: "Returns metadata for a single workspace.",
        params: [
          { name: "id", in: "path", type: "string", required: true, description: "Workspace ID" },
        ],
      },
      {
        method: "DELETE",
        path: "/v1/workspaces/{id}",
        summary: "Delete workspace",
        description: "Permanently deletes a workspace and all its graph data.",
        params: [
          { name: "id", in: "path", type: "string", required: true, description: "Workspace ID" },
        ],
      },
    ],
  },
  {
    tag: "Graph",
    description: "Read and write nodes and edges in the conflict knowledge graph.",
    endpoints: [
      {
        method: "GET",
        path: "/v1/workspaces/{id}/nodes",
        summary: "List nodes",
        description: "Returns all nodes in a workspace, optionally filtered by label.",
        params: [
          { name: "id", in: "path", type: "string", required: true, description: "Workspace ID" },
          { name: "label", in: "query", type: "string", required: false, description: "Filter by node label (Actor, Issue, Event, etc.)" },
        ],
        responseExample: `{ "nodes": [{ "id": "...", "label": "Actor", "name": "...", "properties": {} }] }`,
      },
      {
        method: "POST",
        path: "/v1/workspaces/{id}/nodes",
        summary: "Add node",
        description: "Creates a new node in the workspace graph.",
        params: [
          { name: "id", in: "path", type: "string", required: true, description: "Workspace ID" },
          { name: "label", in: "body", type: "string", required: true, description: "Node label (Actor, Issue, Event, etc.)" },
          { name: "name", in: "body", type: "string", required: true, description: "Display name" },
          { name: "properties", in: "body", type: "object", required: false, description: "Additional node properties" },
        ],
      },
      {
        method: "GET",
        path: "/v1/workspaces/{id}/edges",
        summary: "List edges",
        description: "Returns all edges in a workspace.",
        params: [
          { name: "id", in: "path", type: "string", required: true, description: "Workspace ID" },
        ],
        responseExample: `{ "edges": [{ "id": "...", "type": "OPPOSES", "source_id": "...", "target_id": "...", "properties": {} }] }`,
      },
      {
        method: "POST",
        path: "/v1/workspaces/{id}/edges",
        summary: "Add edge",
        description: "Creates a new directed edge between two nodes.",
        params: [
          { name: "id", in: "path", type: "string", required: true, description: "Workspace ID" },
          { name: "type", in: "body", type: "string", required: true, description: "Edge type (OPPOSES, TRUSTS, SUPPORTS, etc.)" },
          { name: "source_id", in: "body", type: "string", required: true, description: "Source node ID" },
          { name: "target_id", in: "body", type: "string", required: true, description: "Target node ID" },
          { name: "properties", in: "body", type: "object", required: false, description: "Edge properties (weight, confidence, etc.)" },
        ],
      },
    ],
  },
  {
    tag: "Reasoning",
    description: "Conflict analysis, escalation assessment, trust mapping, and network analysis.",
    endpoints: [
      {
        method: "POST",
        path: "/v1/workspaces/{id}/analyze",
        summary: "Analyze conflict (streaming)",
        description: "Stream an AI-powered conflict analysis response. Returns SSE stream. Mode controls the analysis lens.",
        params: [
          { name: "id", in: "path", type: "string", required: true, description: "Workspace ID" },
          { name: "query", in: "body", type: "string", required: true, description: "Natural language analysis question" },
          { name: "mode", in: "body", type: "string", required: false, description: "Analysis mode: general, escalation, ripeness, negotiation" },
        ],
      },
      {
        method: "GET",
        path: "/v1/workspaces/{id}/escalation",
        summary: "Escalation assessment",
        description: "Returns the current Glasl stage, trajectory forecast, and escalation signals.",
        params: [
          { name: "id", in: "path", type: "string", required: true, description: "Workspace ID" },
        ],
        responseExample: `{ "stage": "stage_4", "stage_number": 4, "level": "moderate", "confidence": 0.82, "signals": [...], "forecast": { "direction": "escalating" } }`,
      },
      {
        method: "GET",
        path: "/v1/workspaces/{id}/ripeness",
        summary: "Ripeness for resolution",
        description: "Returns MHS/MEO ripeness scores indicating readiness for negotiated settlement.",
        params: [
          { name: "id", in: "path", type: "string", required: true, description: "Workspace ID" },
        ],
        responseExample: `{ "mhs_score": 0.6, "meo_score": 0.55, "overall_score": 0.58, "is_ripe": false }`,
      },
      {
        method: "GET",
        path: "/v1/workspaces/{id}/power",
        summary: "Power map",
        description: "Returns power asymmetry analysis between actor dyads.",
        params: [
          { name: "id", in: "path", type: "string", required: true, description: "Workspace ID" },
        ],
      },
      {
        method: "GET",
        path: "/v1/workspaces/{id}/trust",
        summary: "Trust matrix",
        description: "Returns trust scores between all actor pairs using ABI model (Ability, Benevolence, Integrity).",
        params: [
          { name: "id", in: "path", type: "string", required: true, description: "Workspace ID" },
        ],
      },
      {
        method: "GET",
        path: "/v1/workspaces/{id}/network",
        summary: "Network metrics",
        description: "Returns centrality, community detection, polarisation index, and broker actors.",
        params: [
          { name: "id", in: "path", type: "string", required: true, description: "Workspace ID" },
        ],
      },
      {
        method: "GET",
        path: "/v1/workspaces/{id}/quality",
        summary: "Graph quality dashboard",
        description: "Returns data quality scores: completeness, consistency, coverage, and recommendations.",
        params: [
          { name: "id", in: "path", type: "string", required: true, description: "Workspace ID" },
        ],
        responseExample: `{ "overall_quality": 0.74, "completeness": { "score": 0.8, "tier": "good" }, "recommendations": [...] }`,
      },
    ],
  },
  {
    tag: "Theory",
    description: "Access the built-in conflict theory framework library.",
    endpoints: [
      {
        method: "GET",
        path: "/v1/theory/frameworks",
        summary: "List frameworks",
        description: "Returns all available conflict theory frameworks (Glasl, Fisher/Ury, Kriesberg, etc.).",
        params: [],
        responseExample: `{ "frameworks": [{ "id": "glasl", "name": "Glasl Escalation Model", "author": "Friedrich Glasl", "year": 1982 }] }`,
      },
      {
        method: "GET",
        path: "/v1/theory/frameworks/{id}",
        summary: "Get framework",
        description: "Returns detailed information about a specific conflict theory framework.",
        params: [
          { name: "id", in: "path", type: "string", required: true, description: "Framework ID (e.g. glasl, fisher-ury)" },
        ],
      },
    ],
  },
  {
    tag: "Health",
    description: "System health and status endpoints.",
    endpoints: [
      {
        method: "GET",
        path: "/health",
        summary: "Health check",
        description: "Returns API status, version, and graph backend type.",
        params: [],
        responseExample: `{ "status": "ok", "version": "1.0.0", "graph_backend": "neo4j" }`,
      },
    ],
  },
];

function MethodBadge({ method }: { method: HttpMethod }) {
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded border text-xs font-mono font-semibold ${METHOD_COLORS[method]}`}>
      {method}
    </span>
  );
}

function EndpointCard({ endpoint }: { endpoint: Endpoint }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="border border-[#27272a] rounded-lg overflow-hidden">
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center gap-3 px-4 py-3 bg-[#18181b] hover:bg-[#27272a]/30 text-left transition-colors"
      >
        <MethodBadge method={endpoint.method} />
        <code className="text-[#fafafa] text-xs font-mono flex-1">{endpoint.path}</code>
        <span className="text-[#71717a] text-xs hidden sm:block">{endpoint.summary}</span>
        {open ? (
          <ChevronDown size={14} className="text-[#52525b] flex-shrink-0" />
        ) : (
          <ChevronRight size={14} className="text-[#52525b] flex-shrink-0" />
        )}
      </button>
      {open && (
        <div className="border-t border-[#27272a] p-4 bg-[#09090b]">
          <p className="text-[#a1a1aa] text-sm mb-4">{endpoint.description}</p>
          {endpoint.params.length > 0 && (
            <div className="mb-4">
              <p className="text-[#71717a] text-xs uppercase tracking-wider mb-2">Parameters</p>
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b border-[#27272a]">
                      <th className="text-left text-[#52525b] font-medium pb-1.5 pr-4">Name</th>
                      <th className="text-left text-[#52525b] font-medium pb-1.5 pr-4">In</th>
                      <th className="text-left text-[#52525b] font-medium pb-1.5 pr-4">Type</th>
                      <th className="text-left text-[#52525b] font-medium pb-1.5 pr-4">Required</th>
                      <th className="text-left text-[#52525b] font-medium pb-1.5">Description</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#27272a]/50">
                    {endpoint.params.map((p) => (
                      <tr key={p.name}>
                        <td className="py-1.5 pr-4"><code className="text-teal-400 font-mono">{p.name}</code></td>
                        <td className="py-1.5 pr-4 text-[#71717a]">{p.in}</td>
                        <td className="py-1.5 pr-4 text-[#71717a] font-mono">{p.type}</td>
                        <td className="py-1.5 pr-4">
                          {p.required ? (
                            <span className="text-red-400">yes</span>
                          ) : (
                            <span className="text-[#52525b]">no</span>
                          )}
                        </td>
                        <td className="py-1.5 text-[#71717a]">{p.description}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
          {endpoint.responseExample && (
            <div>
              <p className="text-[#71717a] text-xs uppercase tracking-wider mb-2">Response Example</p>
              <pre className="bg-[#18181b] border border-[#27272a] rounded-md p-3 text-xs font-mono text-[#a1a1aa] overflow-x-auto">
                <code>{endpoint.responseExample}</code>
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function DocsPage() {
  const [openGroups, setOpenGroups] = useState<Record<string, boolean>>(
    Object.fromEntries(API_SPEC.map((g) => [g.tag, true]))
  );

  function toggleGroup(tag: string) {
    setOpenGroups((prev) => ({ ...prev, [tag]: !prev[tag] }));
  }

  return (
    <div className="p-8 max-w-4xl">
      <div className="mb-8">
        <div className="flex items-center gap-2 mb-2">
          <BookOpen size={18} className="text-[#71717a]" />
          <h1 className="text-2xl font-bold text-[#fafafa]">API Reference</h1>
        </div>
        <p className="text-[#a1a1aa] text-sm">
          DIALECTICA REST API v1. All endpoints require an <code className="font-mono text-[#fafafa] text-xs bg-[#18181b] border border-[#27272a] rounded px-1.5 py-0.5">X-API-Key</code> header.
        </p>
      </div>

      <div className="space-y-8">
        {API_SPEC.map((group) => (
          <div key={group.tag}>
            <button
              onClick={() => toggleGroup(group.tag)}
              className="flex items-center gap-2 mb-3 group"
            >
              {openGroups[group.tag] ? (
                <ChevronDown size={16} className="text-teal-500" />
              ) : (
                <ChevronRight size={16} className="text-[#52525b]" />
              )}
              <h2 className="text-[#fafafa] font-semibold text-base">{group.tag}</h2>
              <span className="text-[#52525b] text-xs font-mono">({group.endpoints.length})</span>
            </button>
            {openGroups[group.tag] && (
              <>
                <p className="text-[#71717a] text-xs mb-4 pl-6">{group.description}</p>
                <div className="space-y-2 pl-6">
                  {group.endpoints.map((ep) => (
                    <EndpointCard key={`${ep.method}-${ep.path}`} endpoint={ep} />
                  ))}
                </div>
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
