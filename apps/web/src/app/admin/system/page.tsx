"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Activity,
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Clock,
  Server,
  Database,
  Cpu,
  Layers,
  ArrowRight,
  ExternalLink,
  Shield,
  Zap,
  Brain,
  Users,
  GitBranch,
} from "lucide-react";
import { cn } from "@/lib/utils";

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */

interface ServiceHealth {
  name: string;
  status: "healthy" | "degraded" | "down" | "unknown";
  latency_ms?: number;
  details?: string;
}

interface HealthResponse {
  status: string;
  version?: string;
  uptime_seconds?: number;
  neo4j?: { status: string; latency_ms?: number };
  redis?: { status: string; latency_ms?: number };
  timestamp?: string;
}

type StatusColor = "green" | "yellow" | "red" | "gray";

function statusToColor(status: string): StatusColor {
  if (status === "healthy" || status === "ok" || status === "connected") return "green";
  if (status === "degraded" || status === "slow") return "yellow";
  if (status === "down" || status === "error" || status === "disconnected") return "red";
  return "gray";
}

const STATUS_STYLES: Record<StatusColor, { dot: string; badge: string; text: string }> = {
  green: { dot: "bg-success", badge: "bg-success/10 text-success", text: "text-success" },
  yellow: { dot: "bg-warning", badge: "bg-warning/10 text-warning", text: "text-warning" },
  red: { dot: "bg-danger", badge: "bg-danger/10 text-danger", text: "text-danger" },
  gray: { dot: "bg-text-secondary", badge: "bg-surface-active text-text-secondary", text: "text-text-secondary" },
};

/* ------------------------------------------------------------------ */
/*  Architecture layers                                                */
/* ------------------------------------------------------------------ */

const ARCHITECTURE_LAYERS = [
  {
    number: 1,
    name: "Neural Ingestion",
    color: "#3b82f6",
    steps: ["GLiNER NER", "Gemini 2.5 Flash", "Pydantic validation"],
    icon: Brain,
  },
  {
    number: 2,
    name: "Symbolic Representation",
    color: "#6366f1",
    steps: ["Conflict Grammar", "Neo4j Graph", "15 node types, 20 edge types"],
    icon: Database,
  },
  {
    number: 3,
    name: "Reasoning & Inference",
    color: "#f59e0b",
    steps: ["25+ symbolic rules", "GNN/KGE neural", "Human validates"],
    icon: Zap,
  },
  {
    number: 4,
    name: "Decision Support",
    color: "#10b981",
    steps: ["6 AI agents", "MCP server"],
    icon: Users,
  },
];

/* ------------------------------------------------------------------ */
/*  Page                                                               */
/* ------------------------------------------------------------------ */

export default function SystemPage() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [services, setServices] = useState<ServiceHealth[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastCheck, setLastCheck] = useState<Date | null>(null);

  const getApiUrl = useCallback(() => {
    if (process.env.NEXT_PUBLIC_API_URL) return process.env.NEXT_PUBLIC_API_URL;
    if (typeof window !== "undefined") {
      return `${window.location.protocol}//${window.location.host}/api/health`;
    }
    return "http://localhost:8080";
  }, []);

  const checkHealth = useCallback(async () => {
    setLoading(true);
    setError(null);
    const apiUrl = getApiUrl();
    const healthUrl = apiUrl.endsWith("/health") ? apiUrl : `${apiUrl}/health`;

    try {
      const res = await fetch(healthUrl, { signal: AbortSignal.timeout(8000) });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data: HealthResponse = await res.json();
      setHealth(data);

      const svcList: ServiceHealth[] = [
        {
          name: "API Server",
          status: data.status === "healthy" || data.status === "ok" ? "healthy" : "degraded",
          details: data.version ? `v${data.version}` : undefined,
        },
        {
          name: "Neo4j Database",
          status: data.neo4j?.status === "connected" || data.neo4j?.status === "healthy" || data.neo4j?.status === "ok"
            ? "healthy"
            : data.neo4j?.status === "degraded" ? "degraded" : data.neo4j ? "down" : "unknown",
          latency_ms: data.neo4j?.latency_ms,
          details: data.neo4j?.status,
        },
        {
          name: "Redis Cache",
          status: data.redis?.status === "connected" || data.redis?.status === "healthy" || data.redis?.status === "ok"
            ? "healthy"
            : data.redis?.status === "degraded" ? "degraded" : data.redis ? "down" : "unknown",
          latency_ms: data.redis?.latency_ms,
          details: data.redis?.status,
        },
      ];
      setServices(svcList);
      setLastCheck(new Date());
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Unknown error";
      setError(msg);
      setHealth(null);
      setServices([
        { name: "API Server", status: "down", details: msg },
        { name: "Neo4j Database", status: "unknown" },
        { name: "Redis Cache", status: "unknown" },
      ]);
      setLastCheck(new Date());
    } finally {
      setLoading(false);
    }
  }, [getApiUrl]);

  useEffect(() => {
    checkHealth();
  }, [checkHealth]);

  const overallStatus: StatusColor = error
    ? "red"
    : services.every((s) => s.status === "healthy")
      ? "green"
      : services.some((s) => s.status === "down")
        ? "red"
        : services.some((s) => s.status === "degraded")
          ? "yellow"
          : "gray";

  const uptimeFormatted = health?.uptime_seconds
    ? (() => {
        const s = health.uptime_seconds;
        const d = Math.floor(s / 86400);
        const h = Math.floor((s % 86400) / 3600);
        const m = Math.floor((s % 3600) / 60);
        if (d > 0) return `${d}d ${h}h ${m}m`;
        if (h > 0) return `${h}h ${m}m`;
        return `${m}m`;
      })()
    : null;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-text-primary flex items-center gap-2">
          <Activity size={20} className="text-accent" />
          System Health
        </h2>
        <div className="flex items-center gap-3">
          {lastCheck && (
            <span className="text-xs text-text-secondary flex items-center gap-1">
              <Clock size={12} />
              Last check: {lastCheck.toLocaleTimeString()}
            </span>
          )}
          <button
            onClick={checkHealth}
            disabled={loading}
            className="btn-secondary flex items-center gap-2 text-xs"
          >
            <RefreshCw size={14} className={cn(loading && "animate-spin")} />
            Refresh
          </button>
        </div>
      </div>

      {/* ---- Overall Status Banner ---- */}
      <div
        className={cn(
          "rounded-lg border p-4 flex items-center gap-4",
          overallStatus === "green" && "bg-success/5 border-success/20",
          overallStatus === "yellow" && "bg-warning/5 border-warning/20",
          overallStatus === "red" && "bg-danger/5 border-danger/20",
          overallStatus === "gray" && "bg-surface border-border",
        )}
      >
        <div className={cn("w-4 h-4 rounded-full", STATUS_STYLES[overallStatus].dot)} />
        <div className="flex-1">
          <p className={cn("font-semibold", STATUS_STYLES[overallStatus].text)}>
            {overallStatus === "green" && "All Systems Operational"}
            {overallStatus === "yellow" && "Partial Degradation"}
            {overallStatus === "red" && (error ? "Backend Offline" : "Service Outage")}
            {overallStatus === "gray" && "Checking..."}
          </p>
          {error && (
            <p className="text-xs text-text-secondary mt-1">
              Could not reach API at{" "}
              <code className="text-xs font-mono bg-surface-active px-1 rounded">
                {getApiUrl()}
              </code>
            </p>
          )}
        </div>
        {uptimeFormatted && (
          <div className="text-right">
            <p className="text-xs text-text-secondary">Uptime</p>
            <p className="text-sm font-mono text-text-primary">{uptimeFormatted}</p>
          </div>
        )}
        {health?.version && (
          <div className="text-right">
            <p className="text-xs text-text-secondary">Version</p>
            <p className="text-sm font-mono text-text-primary">v{health.version}</p>
          </div>
        )}
      </div>

      {/* ---- Backend Offline Instructions ---- */}
      {error && (
        <div className="card space-y-3">
          <h3 className="font-semibold text-text-primary flex items-center gap-2">
            <AlertTriangle size={16} className="text-warning" />
            Backend Offline — Getting Started
          </h3>
          <div className="space-y-2 text-sm text-text-secondary">
            <p>The DIALECTICA API is not reachable. To start the backend locally:</p>
            <div className="bg-background rounded-lg border border-border p-3 font-mono text-xs space-y-1">
              <p className="text-accent">
                # 1. Start services with Docker Compose
              </p>
              <p className="text-text-primary">make dev-local</p>
              <p className="text-accent mt-2">
                # 2. Seed sample data
              </p>
              <p className="text-text-primary">make seed</p>
              <p className="text-accent mt-2">
                # 3. API will be available at
              </p>
              <p className="text-text-primary">http://localhost:8080/docs</p>
            </div>
            <p>
              Or set{" "}
              <code className="text-xs font-mono bg-surface-active px-1 rounded">
                NEXT_PUBLIC_API_URL
              </code>{" "}
              to your deployed Cloud Run URL.
            </p>
            <p className="mt-2">
              Learn more at{" "}
              <a
                href="https://tacitus.me"
                target="_blank"
                rel="noopener noreferrer"
                className="text-accent hover:text-accent-hover transition-colors"
              >
                tacitus.me
                <ExternalLink size={12} className="inline ml-1" />
              </a>
            </p>
          </div>
        </div>
      )}

      {/* ---- Service Cards ---- */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {services.map((svc) => {
          const color = statusToColor(svc.status);
          const styles = STATUS_STYLES[color];
          const IconComponent =
            svc.name === "API Server" ? Server : svc.name.includes("Neo4j") ? Database : Cpu;
          return (
            <div key={svc.name} className="card space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <IconComponent size={16} className="text-text-secondary" />
                  <span className="text-sm font-medium text-text-primary">{svc.name}</span>
                </div>
                <span className={cn("badge text-[10px]", styles.badge)}>{svc.status}</span>
              </div>
              <div className="flex items-center gap-3">
                <div className={cn("w-2.5 h-2.5 rounded-full", styles.dot)} />
                <div className="flex-1">
                  {svc.latency_ms !== undefined && (
                    <span className="font-mono text-xs text-text-secondary">
                      {svc.latency_ms}ms
                    </span>
                  )}
                  {svc.details && (
                    <span className="text-xs text-text-secondary ml-2">{svc.details}</span>
                  )}
                </div>
                {svc.status === "healthy" && <CheckCircle2 size={16} className="text-success" />}
                {svc.status === "degraded" && (
                  <AlertTriangle size={16} className="text-warning" />
                )}
                {svc.status === "down" && <XCircle size={16} className="text-danger" />}
              </div>
            </div>
          );
        })}
      </div>

      {/* ---- Architecture Layers ---- */}
      <div className="card space-y-4">
        <h3 className="font-semibold text-text-primary flex items-center gap-2">
          <Layers size={16} className="text-accent" />
          Backend Architecture — 4 Layers
        </h3>
        <p className="text-xs text-text-secondary">
          The neurosymbolic pipeline processes conflict data through four distinct layers.{" "}
          <a
            href="https://tacitus.me"
            target="_blank"
            rel="noopener noreferrer"
            className="text-accent hover:text-accent-hover transition-colors"
          >
            Learn more at tacitus.me
            <ExternalLink size={10} className="inline ml-1" />
          </a>
        </p>
        <div className="space-y-3">
          {ARCHITECTURE_LAYERS.map((layer, i) => {
            const LayerIcon = layer.icon;
            return (
              <div key={layer.number} className="relative">
                <div
                  className="rounded-lg border p-4 flex items-start gap-4"
                  style={{ borderColor: `${layer.color}30`, backgroundColor: `${layer.color}08` }}
                >
                  <div
                    className="w-10 h-10 rounded-lg flex items-center justify-center shrink-0 font-bold text-sm"
                    style={{ backgroundColor: `${layer.color}20`, color: layer.color }}
                  >
                    {layer.number}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <LayerIcon size={14} style={{ color: layer.color }} />
                      <h4 className="font-semibold text-text-primary text-sm">{layer.name}</h4>
                    </div>
                    <div className="flex flex-wrap gap-2 mt-2">
                      {layer.steps.map((step, si) => (
                        <span key={step} className="flex items-center gap-1">
                          <span
                            className="badge text-[10px]"
                            style={{
                              backgroundColor: `${layer.color}15`,
                              color: layer.color,
                            }}
                          >
                            {step}
                          </span>
                          {si < layer.steps.length - 1 && (
                            <ArrowRight size={10} className="text-text-secondary" />
                          )}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
                {i < ARCHITECTURE_LAYERS.length - 1 && (
                  <div className="flex justify-center py-1">
                    <div className="w-px h-3 bg-border" />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* ---- Quick Links ---- */}
      <div className="card space-y-3">
        <h3 className="font-semibold text-text-primary flex items-center gap-2">
          <GitBranch size={16} className="text-accent" />
          Quick Links
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
          {[
            { label: "TACITUS Website", href: "https://tacitus.me", external: true },
            { label: "API Docs (Swagger)", href: `${getApiUrl()}/docs`, external: true },
            { label: "Architecture", href: "/admin/architecture", external: false },
            { label: "Graph Explorer", href: "/admin/graph", external: false },
          ].map((link) => (
            <a
              key={link.label}
              href={link.href}
              target={link.external ? "_blank" : undefined}
              rel={link.external ? "noopener noreferrer" : undefined}
              className="flex items-center gap-2 px-3 py-2 bg-background rounded-lg border border-border hover:border-border-hover hover:bg-surface-hover transition-colors text-sm text-text-secondary hover:text-text-primary"
            >
              {link.label}
              {link.external && <ExternalLink size={12} className="ml-auto shrink-0" />}
              {!link.external && <ArrowRight size={12} className="ml-auto shrink-0" />}
            </a>
          ))}
        </div>
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
        — The Universal Data Layer for Human Friction
      </div>
    </div>
  );
}
