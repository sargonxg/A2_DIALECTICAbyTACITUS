'use client';

import { useParams } from 'next/navigation';
import { Layers, Network, Upload } from 'lucide-react';
import { useWorkspace } from '@/hooks/useWorkspace';
import { useGraphData } from '@/hooks/useGraph';
import { DocumentUpload } from '@/components/extraction/DocumentUpload';
import { ExtractionProgress } from '@/components/extraction/ExtractionProgress';
import { ExtractionReview } from '@/components/extraction/ExtractionReview';

export default function IngestPage() {
  const params = useParams();
  const id = params.id as string;

  const { workspace } = useWorkspace(id);
  const { nodes, edges, refetch } = useGraphData(id);

  // Group node counts by label
  const nodeCounts = nodes.reduce<Record<string, number>>((acc, node) => {
    acc[node.label] = (acc[node.label] ?? 0) + 1;
    return acc;
  }, {});

  const nodeTypes = Object.entries(nodeCounts).sort(([, a], [, b]) => b - a);

  return (
    <div className="p-6 max-w-4xl space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-zinc-100">Document Ingestion</h2>
          <p className="text-sm text-zinc-500 mt-0.5">
            Upload documents to extract and populate the knowledge graph
            {workspace ? ` for "${workspace.name}"` : ''}.
          </p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5">
            <Layers className="w-3.5 h-3.5 text-zinc-500" />
            <span className="text-sm text-zinc-400">
              <span className="text-zinc-200 font-semibold">{nodes.length}</span> nodes
            </span>
          </div>
          <div className="flex items-center gap-1.5">
            <Network className="w-3.5 h-3.5 text-zinc-500" />
            <span className="text-sm text-zinc-400">
              <span className="text-zinc-200 font-semibold">{edges.length}</span> edges
            </span>
          </div>
        </div>
      </div>

      {/* Node counts by type */}
      {nodeTypes.length > 0 && (
        <div className="rounded-xl border border-[#27272a] bg-[#18181b] p-4">
          <p className="text-xs font-semibold uppercase tracking-widest text-zinc-500 mb-3">
            Graph Composition
          </p>
          <div className="flex flex-wrap gap-2">
            {nodeTypes.map(([label, count]) => (
              <div
                key={label}
                className="flex items-center gap-1.5 rounded-lg border border-[#27272a] bg-zinc-900/40 px-3 py-1.5"
              >
                <span className="text-xs capitalize text-zinc-400">{label}</span>
                <span className="text-xs font-bold text-zinc-200">{count}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Upload component */}
      <div className="rounded-xl border border-[#27272a] bg-[#18181b] overflow-hidden">
        <div className="px-5 py-3 border-b border-[#27272a] flex items-center gap-2">
          <Upload className="w-3.5 h-3.5 text-zinc-500" />
          <p className="text-xs font-semibold uppercase tracking-widest text-zinc-500">
            Upload Documents
          </p>
        </div>
        <div className="p-5">
          <DocumentUpload workspaceId={id} onSuccess={refetch} />
        </div>
      </div>

      {/* Extraction progress */}
      <ExtractionProgress workspaceId={id} />

      {/* Extraction review */}
      <ExtractionReview workspaceId={id} onAccepted={refetch} />
    </div>
  );
}
