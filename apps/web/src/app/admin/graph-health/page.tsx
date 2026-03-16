'use client';
import { useEffect, useState } from 'react';
import { workspacesApi, reasoningApi, Workspace, QualityDashboard } from '@/lib/api';

function QualityBar({ score, label }: { score: number; label: string }) {
  const pct = Math.round(score * 100);
  const color = score >= 0.7 ? '#22c55e' : score >= 0.4 ? '#eab308' : '#ef4444';
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs">
        <span className="text-[#a1a1aa]">{label}</span>
        <span style={{ color }}>{pct}%</span>
      </div>
      <div className="h-1.5 bg-[#27272a] rounded-full overflow-hidden">
        <div className="h-full rounded-full transition-all" style={{ width: `${pct}%`, backgroundColor: color }} />
      </div>
    </div>
  );
}

export default function GraphHealthPage() {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [quality, setQuality] = useState<Record<string, QualityDashboard>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    workspacesApi.list().then((r) => {
      setWorkspaces(r.workspaces || []);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const loadQuality = async (id: string) => {
    try {
      const q = await reasoningApi.getQuality(id);
      setQuality((prev) => ({ ...prev, [id]: q }));
    } catch {}
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-white">Graph Health</h1>
      {loading ? (
        <div className="text-[#a1a1aa]">Loading workspaces…</div>
      ) : (
        <div className="space-y-4">
          {workspaces.map((ws) => (
            <div key={ws.id} className="bg-[#18181b] border border-[#27272a] rounded-lg p-4">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <div className="font-medium text-white">{ws.name}</div>
                  <div className="text-xs text-[#a1a1aa]">{ws.id}</div>
                </div>
                {!quality[ws.id] && (
                  <button
                    onClick={() => loadQuality(ws.id)}
                    className="text-xs text-teal-500 hover:text-teal-400 border border-teal-600 px-2 py-1 rounded"
                  >
                    Assess
                  </button>
                )}
                {quality[ws.id] && (
                  <span className={`text-sm font-bold ${quality[ws.id].overall_quality >= 0.7 ? 'text-green-400' : quality[ws.id].overall_quality >= 0.4 ? 'text-yellow-400' : 'text-red-400'}`}>
                    {Math.round(quality[ws.id].overall_quality * 100)}%
                  </span>
                )}
              </div>
              {quality[ws.id] && (
                <div className="grid grid-cols-3 gap-4">
                  <QualityBar score={quality[ws.id].completeness.score} label="Completeness" />
                  <QualityBar score={quality[ws.id].consistency.score} label="Consistency" />
                  <QualityBar score={quality[ws.id].coverage.score} label="Coverage" />
                </div>
              )}
            </div>
          ))}
          {workspaces.length === 0 && (
            <p className="text-[#a1a1aa]">No workspaces found.</p>
          )}
        </div>
      )}
    </div>
  );
}
