'use client';
import { useParams } from 'next/navigation';
import { CausalChainViz } from '@/components/graph/CausalChainViz';
import { useEffect, useState } from 'react';

interface CausalData {
  chains: { root: string; depth: number; has_cycle: boolean; length: number }[];
  root_causes: { event_id: string; description: string; downstream: number }[];
}

export default function CausalPage() {
  const params = useParams();
  const id = params.id as string;
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';
  const [data, setData] = useState<CausalData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const apiKey = localStorage.getItem('dialectica_api_key') || '';
    fetch(`${apiUrl}/v1/workspaces/${id}/causation`, {
      headers: { 'X-API-Key': apiKey },
    })
      .then((r) => r.json())
      .then(setData)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [id, apiUrl]);

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-xl font-bold text-white">Causal Analysis</h1>
      <CausalChainViz workspaceId={id} />

      {!loading && data && (
        <div className="grid grid-cols-2 gap-6">
          <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-4">
            <h3 className="font-semibold text-white mb-3">Root Causes ({data.root_causes.length})</h3>
            <div className="space-y-2">
              {data.root_causes.map((rc) => (
                <div key={rc.event_id} className="border border-[#27272a] rounded p-2">
                  <div className="text-sm text-white truncate">{rc.description}</div>
                  <div className="text-xs text-[#a1a1aa] mt-1">{rc.downstream} downstream effects</div>
                </div>
              ))}
              {data.root_causes.length === 0 && <p className="text-[#a1a1aa] text-sm">No root causes identified.</p>}
            </div>
          </div>
          <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-4">
            <h3 className="font-semibold text-white mb-3">Causal Chains ({data.chains.length})</h3>
            <div className="space-y-2">
              {data.chains.map((c, i) => (
                <div key={i} className="border border-[#27272a] rounded p-2 flex justify-between items-center">
                  <span className="text-sm text-[#a1a1aa] font-mono truncate">{c.root}</span>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <span className="text-xs text-[#a1a1aa]">depth {c.depth}</span>
                    {c.has_cycle && <span className="text-xs bg-red-900/50 text-red-400 px-1.5 py-0.5 rounded">cycle</span>}
                  </div>
                </div>
              ))}
              {data.chains.length === 0 && <p className="text-[#a1a1aa] text-sm">No causal chains found.</p>}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
