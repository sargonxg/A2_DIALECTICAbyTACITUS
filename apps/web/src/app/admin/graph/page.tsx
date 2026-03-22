"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Network,
  RefreshCw,
  ExternalLink,
  Database,
  Layers,
  GitBranch,
  ChevronDown,
  ChevronRight,
  Circle,
  AlertTriangle,
  CheckCircle2,
} from "lucide-react";
import { cn, NODE_COLORS } from "@/lib/utils";

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */

interface WorkspaceSummary {
  id: string;
  name: string;
  node_count?: number;
  edge_count?: number;
  created_at?: string;
}

/* ------------------------------------------------------------------ */
/*  Ontology data                                                      */
/* ------------------------------------------------------------------ */

const NODE_TYPES: { type: string; label: string; description: string }[] = [
  { type: "actor", label: "Actor", description: "Person, group, organization, or state involved in a conflict" },
  { type: "conflict", label: "Conflict", description: "Central conflict node with Glasl stage and status" },
  { type: "event", label: "Event", description: "Timestamped occurrence that advances or de-escalates a conflict" },
  { type: "issue", label: "Issue", description: "Substantive, procedural, or psychological matter in dispute" },
  { type: "interest", label: "Interest", description: "Underlying need, desire, or concern of a party" },
  { type: "norm", label: "Norm", description: "Legal rule, social norm, or organizational policy governing behavior" },
  { type: "process", label: "Process", description: "Formal or informal procedure for managing the conflict" },
  { type: "outcome", label: "Outcome", description: "Result, agreement, or state produced by a conflict process" },
  { type: "narrative", label: "Narrative", description: "Frame, story, or interpretive lens applied to the conflict" },
  { type: "emotional_state", label: "Emotional State", description: "Emotion experienced by a party (Plutchik wheel)" },
  { type: "trust_state", label: "Trust State", description: "Trust level between parties (Mayer/Davis/Schoorman)" },
  { type: "power_dynamic", label: "Power Dynamic", description: "Power asymmetry (French & Raven bases)" },
  { type: "location", label: "Location", description: "Geographic context for events or actors" },
  { type: "evidence", label: "Evidence", description: "Document, testimony, or artifact supporting claims" },
  { type: "role", label: "Role", description: "Functional role (mediator, advocate, witness, etc.)" },
];

const EDGE_TYPES: { type: string; description: string }[] = [
  { type: "PARTY_TO", description: "Actor is a party to a conflict" },
  { type: "CAUSED", description: "One event caused another" },
  { type: "PART_OF", description: "Issue or sub-entity belongs to a conflict" },
  { type: "PARTICIPATES_IN", description: "Actor participates in a process" },
  { type: "RESOLVED_THROUGH", description: "Conflict managed via a process" },
  { type: "HAS_POWER_OVER", description: "Power asymmetry between actors" },
  { type: "HAS_INTEREST", description: "Actor holds an interest" },
  { type: "PERFORMED", description: "Actor performed an event" },
  { type: "TARGETED", description: "Event targeted an actor" },
  { type: "GOVERNS", description: "Norm governs a conflict or process" },
  { type: "EXPERIENCES", description: "Actor experiences an emotional state" },
  { type: "HAS_TRUST_STATE", description: "Actor has a trust relationship" },
  { type: "HELD_BY", description: "Power dynamic held by an actor" },
  { type: "MOTIVATED", description: "Emotional state motivated an event" },
  { type: "ALLIES_WITH", description: "Coalition relationship between actors" },
  { type: "OPPOSES", description: "Opposition relationship between actors" },
  { type: "ESCALATES_TO", description: "Conflict escalates to a new stage" },
  { type: "MEDIATES", description: "Actor mediates a conflict" },
  { type: "CONSTRAINS", description: "Norm or factor constrains options" },
  { type: "LEVERAGES", description: "Actor uses leverage in a conflict" },
];

const TIER_LEVELS = [
  {
    tier: "Lite",
    description: "Quick extraction for simple disputes",
    includes: ["actor", "conflict", "event", "issue", "interest"],
    color: "#22c55e",
  },
  {
    tier: "Standard",
    description: "Full extraction for workplace and commercial disputes",
    includes: [
      "actor", "conflict", "event", "issue", "interest",
      "norm", "process", "outcome", "emotional_state", "trust_state", "power_dynamic",
    ],
    color: "#3b82f6",
  },
  {
    tier: "Deep",
    description: "Exhaustive analysis for geopolitical and complex multi-party conflicts",
    includes: [
      "actor", "conflict", "event", "issue", "interest",
      "norm", "process", "outcome", "emotional_state", "trust_state", "power_dynamic",
      "narrative", "location", "evidence", "role",
    ],
    color: "#a855f7",
  },
];

/* ------------------------------------------------------------------ */
/*  Page                                                               */
/* ------------------------------------------------------------------ */

export default function GraphExplorerPage() {
  const [workspaces, setWorkspaces] = useState<WorkspaceSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedSection, setExpandedSection] = useState<string>("ontology");

  const getApiUrl = useCallback(() => {
    return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";
  }, []);

  const fetchWorkspaces = useCallback(async () => {
    setLoading(true);
    setError(null);
    const apiUrl = getApiUrl();
    try {
      const apiKey =
        typeof window !== "undefined" ? localStorage.getItem("dialectica_api_key") : null;
      const headers: Record<string, string> = apiKey ? { "X-API-Key": apiKey } : {};
      const res = await fetch(`${apiUrl}/v1/workspaces`, {
        headers,
        signal: AbortSignal.timeout(8000),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      const list = Array.isArray(data) ? data : data.workspaces || data.items || [];
      setWorkspaces(list);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch workspaces");
      setWorkspaces([]);
    } finally {
      setLoading(false);
    }
  }, [getApiUrl]);

  useEffect(() => {
    fetchWorkspaces();
  }, [fetchWorkspaces]);

  const toggleSection = (section: string) => {
    setExpandedSection((prev) => (prev === section ? "" : section));
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-text-primary flex items-center gap-2">
          <Network size={20} className="text-accent" />
          Graph Explorer
        </h2>
        <a
          href="https://tacitus.me"
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs text-text-secondary hover:text-accent transition-colors flex items-center gap-1"
        >
          tacitus.me <ExternalLink size={10} />
        </a>
      </div>

      {/* ---- Workspaces ---- */}
      <div className="card space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-text-primary flex items-center gap-2">
            <Database size={16} className="text-accent" />
            Workspaces
          </h3>
          <button
            onClick={fetchWorkspaces}
            disabled={loading}
            className="btn-secondary flex items-center gap-2 text-xs"
          >
            <RefreshCw size={14} className={cn(loading && "animate-spin")} />
            Refresh
          </button>
        </div>

        {error && (
          <div className="flex items-center gap-2 px-3 py-2 bg-warning/10 border border-warning/20 rounded-lg text-sm text-warning">
            <AlertTriangle size={14} />
            <span>
              Cannot load workspaces — backend may be offline. Start with{" "}
              <code className="font-mono text-xs">make dev-local</code>
            </span>
          </div>
        )}

        {!error && workspaces.length === 0 && !loading && (
          <div className="text-center py-8 text-text-secondary text-sm">
            No workspaces found. Run <code className="font-mono text-xs text-accent">make seed</code> to load sample data.
          </div>
        )}

        {workspaces.length > 0 && (
          <div className="space-y-2">
            {workspaces.map((ws) => (
              <div
                key={ws.id}
                className="flex items-center justify-between bg-background rounded-lg border border-border p-3 hover:border-border-hover transition-colors"
              >
                <div className="flex items-center gap-3">
                  <CheckCircle2 size={14} className="text-success shrink-0" />
                  <div>
                    <p className="text-sm font-medium text-text-primary">{ws.name || ws.id}</p>
                    <p className="text-xs text-text-secondary font-mono">{ws.id}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  {ws.node_count !== undefined && (
                    <div className="text-right">
                      <p className="text-sm font-mono text-text-primary">{ws.node_count}</p>
                      <p className="text-[10px] text-text-secondary">nodes</p>
                    </div>
                  )}
                  {ws.edge_count !== undefined && (
                    <div className="text-right">
                      <p className="text-sm font-mono text-text-primary">{ws.edge_count}</p>
                      <p className="text-[10px] text-text-secondary">edges</p>
                    </div>
                  )}
                  <a
                    href="https://console.neo4j.io"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-ghost text-xs flex items-center gap-1"
                    title="Open in Neo4j Aura Console"
                  >
                    <Database size={12} />
                    Neo4j
                    <ExternalLink size={10} />
                  </a>
                </div>
              </div>
            ))}
          </div>
        )}

        {loading && (
          <div className="text-center py-4">
            <RefreshCw size={16} className="animate-spin text-accent mx-auto" />
            <p className="text-xs text-text-secondary mt-2">Loading workspaces...</p>
          </div>
        )}
      </div>

      {/* ---- Ontology: Node Types ---- */}
      <div className="card space-y-3">
        <button
          onClick={() => toggleSection("ontology")}
          className="w-full flex items-center justify-between"
        >
          <h3 className="font-semibold text-text-primary flex items-center gap-2">
            <Layers size={16} className="text-accent" />
            Conflict Grammar Ontology — 15 Node Types
          </h3>
          {expandedSection === "ontology" ? (
            <ChevronDown size={16} className="text-text-secondary" />
          ) : (
            <ChevronRight size={16} className="text-text-secondary" />
          )}
        </button>

        {expandedSection === "ontology" && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
            {NODE_TYPES.map((nt) => (
              <div
                key={nt.type}
                className="flex items-start gap-3 bg-background rounded-lg border border-border p-3"
              >
                <Circle
                  size={12}
                  className="shrink-0 mt-0.5"
                  style={{ color: NODE_COLORS[nt.type] || "#94a3b8", fill: NODE_COLORS[nt.type] || "#94a3b8" }}
                />
                <div>
                  <p className="text-sm font-medium text-text-primary">{nt.label}</p>
                  <p className="text-xs text-text-secondary leading-relaxed">{nt.description}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ---- Edge Types ---- */}
      <div className="card space-y-3">
        <button
          onClick={() => toggleSection("edges")}
          className="w-full flex items-center justify-between"
        >
          <h3 className="font-semibold text-text-primary flex items-center gap-2">
            <GitBranch size={16} className="text-accent" />
            Relationship Types — 20 Edge Types
          </h3>
          {expandedSection === "edges" ? (
            <ChevronDown size={16} className="text-text-secondary" />
          ) : (
            <ChevronRight size={16} className="text-text-secondary" />
          )}
        </button>

        {expandedSection === "edges" && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {EDGE_TYPES.map((et) => (
              <div
                key={et.type}
                className="flex items-center gap-3 bg-background rounded-lg border border-border px-3 py-2"
              >
                <code className="text-xs font-mono text-accent shrink-0 min-w-[140px]">
                  {et.type}
                </code>
                <span className="text-xs text-text-secondary">{et.description}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ---- Tier Levels ---- */}
      <div className="card space-y-3">
        <button
          onClick={() => toggleSection("tiers")}
          className="w-full flex items-center justify-between"
        >
          <h3 className="font-semibold text-text-primary flex items-center gap-2">
            <Layers size={16} className="text-accent" />
            Extraction Tiers — 3 Levels
          </h3>
          {expandedSection === "tiers" ? (
            <ChevronDown size={16} className="text-text-secondary" />
          ) : (
            <ChevronRight size={16} className="text-text-secondary" />
          )}
        </button>

        {expandedSection === "tiers" && (
          <div className="space-y-3">
            {TIER_LEVELS.map((tier) => (
              <div
                key={tier.tier}
                className="rounded-lg border p-4 space-y-2"
                style={{ borderColor: `${tier.color}30`, backgroundColor: `${tier.color}05` }}
              >
                <div className="flex items-center gap-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: tier.color }}
                  />
                  <h4 className="font-semibold text-text-primary text-sm">{tier.tier}</h4>
                  <span className="text-xs text-text-secondary">
                    ({tier.includes.length} node types)
                  </span>
                </div>
                <p className="text-xs text-text-secondary">{tier.description}</p>
                <div className="flex flex-wrap gap-1.5">
                  {tier.includes.map((nodeType) => (
                    <span
                      key={nodeType}
                      className="badge text-[10px]"
                      style={{
                        backgroundColor: `${NODE_COLORS[nodeType] || "#94a3b8"}15`,
                        color: NODE_COLORS[nodeType] || "#94a3b8",
                      }}
                    >
                      {nodeType.replace(/_/g, " ")}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ---- Footer ---- */}
      <div className="text-center text-xs text-text-secondary/50 pt-4 border-t border-border">
        DIALECTICA by{" "}
        <a
          href="https://tacitus.me"
          target="_blank"
          rel="noopener noreferrer"
          className="text-accent hover:text-accent-hover transition-colors"
        >
          TACITUS
        </a>{" "}
        — Neo4j Aura is the primary graph database
      </div>
    </div>
  );
}
