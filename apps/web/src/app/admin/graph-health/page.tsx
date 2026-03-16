"use client";

import { useEffect, useState, useCallback } from "react";
import { workspacesApi, reasoningApi, type Workspace, type QualityDashboard } from "@/lib/api";
import { Activity, RefreshCw, Loader2, AlertTriangle, ChevronDown, ChevronUp } from "lucide-react";

function QualityBadge({ score }: { score: number }) {
  const pct = Math.round(score * 100);
  const color =
    pct >= 80 ? "text-green-400 bg-green-500/10 border-green-500/20" :
    pct >= 60 ? "text-yellow-400 bg-yellow-500/10 border-yellow-500/20" :
               "text-red-400 bg-red-500/10 border-red-500/20";
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded border text-xs font-mono font-semibold ${color}`}>
      {pct}%
    </span>
  );
}

function QualityBar({ score }: { score: number }) {
  const pct = Math.round(score * 100);
  const color = pct >= 80 ? "bg-green-500" : pct >= 60 ? "bg-yellow-500" : "bg-red-500";
  return (
    <div className="w-full h-1.5 bg-[#27272a] rounded-full overflow-hidden">
      <div className={`h-full rounded-full transition-all duration-500 ${color}`} style={{ width: `${pct}%` }} />
    </div>
  );
}

interface WorkspaceQuality {
  workspace: Workspace;
  quality: QualityDashboard | null;
  loading: boolean;
  error: string | null;
  expanded: boolean;
}

export default function GraphHealthPage() {
  const [items, setItems] = useState<WorkspaceQuality[]>([]);
  const [loadingWs, setLoadingWs] = useState(true);
  const [wsError, setWsError] = useState<string | null>(null);

  const fetchAll = useCallback(async () => {
    setLoadingWs(true);
    setWsError(null);
    try {
      const res = await workspacesApi.list();
      const initial: WorkspaceQuality[] = (res.workspaces ?? []).map((ws) => ({
        workspace: ws,
        quality: null,
        loading: true,
        error: null,
        expanded: false,
      }));
      setItems(initial);

      for (const ws of res.workspaces ?? []) {
        reasoningApi.getQuality(ws.id)
          .then((q) => {
            setItems((prev) =>
              prev.map((item) =>
                item.workspace.id === ws.id ? { ...item, quality: q, loading: false } : item
              )
            );
          })
          .catch((err) => {
            setItems((prev) =>
              prev.map((item) =>
                item.workspace.id === ws.id
                  ? { ...item, error: err.message, loading: false }
                  : item
              )
            );
          });
      }
    } catch (err) {
      setWsError(err instanceof Error ? err.message : "Failed to load workspaces");
    } finally {
      setLoadingWs(false);
    }
  }, []);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  function toggleExpand(id: string) {
    setItems((prev) =>
      prev.map((item) =>
        item.workspace.id === id ? { ...item, expanded: !item.expanded } : item
      )
    );
  }

  return (
    <div className="p-8 max-w-4xl">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-[#fafafa] mb-1">Graph Health</h1>
          <p className="text-[#a1a1aa] text-sm">Quality scores and diagnostics for all workspaces.</p>
        </div>
        <button
          onClick={fetchAll}
          disabled={loadingWs}
          className="p-2 rounded-md text-[#71717a] hover:text-[#fafafa] hover:bg-[#27272a] transition-colors disabled:opacity-50"
          aria-label="Refresh"
        >
          <RefreshCw size={14} className={loadingWs ? "animate-spin" : ""} />
        </button>
      </div>

      {wsError && (
        <div className="flex items-center gap-2 p-3 bg-red-500/10 border border-red-500/20 rounded-lg mb-6 text-red-400 text-sm">
          <AlertTriangle size={14} /> {wsError}
        </div>
      )}

      {loadingWs && !items.length ? (
        <div className="flex items-center gap-2 text-[#71717a] text-sm">
          <Loader2 size={14} className="animate-spin" /> Loading workspaces…
        </div>
      ) : !items.length ? (
        <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-12 text-center">
          <Activity size={32} className="text-[#3f3f46] mx-auto mb-3" />
          <p className="text-[#71717a] text-sm">No workspaces found. Create workspaces first.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {items.map((item) => (
            <div key={item.workspace.id} className="bg-[#18181b] border border-[#27272a] rounded-lg overflow-hidden">
              <button
                onClick={() => toggleExpand(item.workspace.id)}
                className="w-full flex items-center gap-4 p-4 hover:bg-[#27272a]/20 transition-colors text-left"
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <p className="text-[#fafafa] text-sm font-medium truncate">{item.workspace.name}</p>
                    <span className="text-[#52525b] text-xs capitalize">{item.workspace.domain}</span>
                  </div>
                  {item.loading ? (
                    <div className="flex items-center gap-1.5 text-[#52525b] text-xs">
                      <Loader2 size={11} className="animate-spin" /> Loading quality data…
                    </div>
                  ) : item.error ? (
                    <div className="flex items-center gap-1.5 text-red-400/70 text-xs">
                      <AlertTriangle size={11} /> {item.error}
                    </div>
                  ) : item.quality ? (
                    <QualityBar score={item.quality.overall_quality} />
                  ) : null}
                </div>
                <div className="flex items-center gap-3 flex-shrink-0">
                  {item.quality && <QualityBadge score={item.quality.overall_quality} />}
                  {item.expanded ? (
                    <ChevronUp size={14} className="text-[#52525b]" />
                  ) : (
                    <ChevronDown size={14} className="text-[#52525b]" />
                  )}
                </div>
              </button>

              {item.expanded && item.quality && (
                <div className="border-t border-[#27272a] p-4">
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-4">
                    {[
                      { label: "Completeness", value: item.quality.completeness.score, tier: item.quality.completeness.tier },
                      { label: "Consistency", value: item.quality.consistency.score, tier: null },
                      { label: "Coverage", value: item.quality.coverage.score, tier: null },
                      { label: "Orphan Nodes", value: null, raw: item.quality.completeness.orphan_nodes.toString(), tier: null },
                    ].map((metric) => (
                      <div key={metric.label}>
                        <p className="text-[#71717a] text-xs mb-1">{metric.label}</p>
                        {metric.value !== null ? (
                          <div className="flex items-center gap-2">
                            <QualityBadge score={metric.value} />
                            {metric.tier && <span className="text-[#52525b] text-xs capitalize">{metric.tier}</span>}
                          </div>
                        ) : (
                          <p className="text-[#a1a1aa] text-sm font-mono">{metric.raw}</p>
                        )}
                      </div>
                    ))}
                  </div>

                  {item.quality.recommendations.length > 0 && (
                    <div>
                      <p className="text-[#71717a] text-xs mb-2">Recommendations</p>
                      <ul className="space-y-1">
                        {item.quality.recommendations.map((rec, i) => (
                          <li key={i} className="flex items-start gap-2 text-xs text-[#a1a1aa]">
                            <span className="text-teal-500 mt-0.5">•</span>
                            {rec}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {item.quality.completeness.missing_node_types.length > 0 && (
                    <div className="mt-3">
                      <p className="text-[#71717a] text-xs mb-2">Missing Node Types</p>
                      <div className="flex flex-wrap gap-1.5">
                        {item.quality.completeness.missing_node_types.map((t) => (
                          <span key={t} className="px-2 py-0.5 rounded bg-[#09090b] border border-[#27272a] text-[#71717a] text-xs font-mono">{t}</span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
