"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { BookOpen, FileText, Plus, RefreshCw } from "lucide-react";
import { api } from "@/lib/api";

interface Doc {
  id: string;
  title: string;
  word_count: number;
  ingested_at: string;
  extraction_tier: string;
  extraction_model: string;
  nodes_extracted: number;
  edges_extracted: number;
  errors: number;
  job_id: string;
  source_kind: string;
  gutenberg_book_id: string | null;
}

interface CorpusResponse {
  workspace_id: string;
  total_documents: number;
  total_words: number;
  total_nodes: number;
  total_edges: number;
  documents: Doc[];
}

export default function CorpusLibraryPage() {
  const { id } = useParams();
  const workspaceId = id as string;
  const [data, setData] = useState<CorpusResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    setLoading(true);
    setError(null);
    api
      .listCorpusDocuments(workspaceId)
      .then((res) => setData(res as CorpusResponse))
      .catch((e: unknown) => setError(e instanceof Error ? e.message : "Failed to load"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
    // Refresh every 5s while the page is open so newly-finished jobs appear.
    const interval = setInterval(load, 5000);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [workspaceId]);

  return (
    <div className="max-w-5xl space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-text-primary">Corpus Library</h2>
          <p className="text-xs text-text-secondary">
            Source documents ingested into this workspace.
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={load}
            className="btn-ghost flex items-center gap-1.5 text-sm"
            aria-label="Refresh"
          >
            <RefreshCw size={14} /> Refresh
          </button>
          <Link
            href={`/workspaces/${workspaceId}/ingest`}
            className="btn-primary flex items-center gap-1.5 text-sm"
          >
            <Plus size={14} /> Ingest source
          </Link>
        </div>
      </div>

      {data && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <Stat label="Documents" value={data.total_documents} />
          <Stat label="Total words" value={data.total_words.toLocaleString()} />
          <Stat label="Nodes extracted" value={data.total_nodes} />
          <Stat label="Edges extracted" value={data.total_edges} />
        </div>
      )}

      {loading && !data && (
        <div className="text-xs text-text-secondary">Loading…</div>
      )}
      {error && <div className="text-sm text-danger">{error}</div>}

      {data && data.documents.length === 0 && !loading && (
        <div className="card p-8 text-center space-y-3">
          <BookOpen size={28} className="mx-auto text-text-secondary" />
          <p className="text-sm text-text-primary">No source documents yet.</p>
          <p className="text-xs text-text-secondary">
            Pick a Project Gutenberg classic or upload your own document to seed this workspace.
          </p>
          <Link
            href={`/workspaces/${workspaceId}/ingest`}
            className="btn-primary inline-flex items-center gap-1.5 text-sm"
          >
            <Plus size={14} /> Ingest your first source
          </Link>
        </div>
      )}

      {data && data.documents.length > 0 && (
        <div className="card overflow-hidden p-0">
          <table className="w-full text-sm">
            <thead className="bg-surface text-text-secondary text-xs">
              <tr>
                <th className="text-left px-3 py-2 font-medium">Title</th>
                <th className="text-left px-3 py-2 font-medium">Source</th>
                <th className="text-right px-3 py-2 font-medium">Words</th>
                <th className="text-right px-3 py-2 font-medium">Nodes</th>
                <th className="text-right px-3 py-2 font-medium">Edges</th>
                <th className="text-left px-3 py-2 font-medium">Tier</th>
                <th className="text-left px-3 py-2 font-medium">Ingested</th>
              </tr>
            </thead>
            <tbody>
              {data.documents.map((d) => (
                <tr
                  key={`${d.job_id}-${d.id}`}
                  className="border-t border-border hover:bg-surface/50"
                >
                  <td className="px-3 py-2 text-text-primary flex items-center gap-2">
                    {d.source_kind === "gutenberg" ? (
                      <BookOpen size={12} className="text-text-secondary" />
                    ) : (
                      <FileText size={12} className="text-text-secondary" />
                    )}
                    {d.title}
                  </td>
                  <td className="px-3 py-2 text-text-secondary">
                    {d.source_kind === "gutenberg" && d.gutenberg_book_id
                      ? `Gutenberg #${d.gutenberg_book_id}`
                      : d.source_kind}
                  </td>
                  <td className="px-3 py-2 text-right tabular-nums">
                    {d.word_count.toLocaleString()}
                  </td>
                  <td className="px-3 py-2 text-right tabular-nums">{d.nodes_extracted}</td>
                  <td className="px-3 py-2 text-right tabular-nums">{d.edges_extracted}</td>
                  <td className="px-3 py-2 text-text-secondary">{d.extraction_tier}</td>
                  <td className="px-3 py-2 text-text-secondary">
                    {formatDate(d.ingested_at)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="card p-3">
      <div className="text-[10px] uppercase tracking-wide text-text-secondary">{label}</div>
      <div className="text-lg font-semibold text-text-primary tabular-nums">{value}</div>
    </div>
  );
}

function formatDate(iso: string): string {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}
