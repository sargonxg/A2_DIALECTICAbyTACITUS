'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  Settings,
  Save,
  Trash2,
  AlertTriangle,
  Loader2,
  Hash,
  Layers,
  Network,
  X,
  Check,
} from 'lucide-react';
import { useWorkspace } from '@/hooks/useWorkspace';
import { useGraphData } from '@/hooks/useGraph';
import { workspacesApi } from '@/lib/api';

const DOMAINS = ['interpersonal', 'workplace', 'commercial', 'legal', 'political', 'armed', 'other'];
const SCALES  = ['micro', 'meso', 'macro', 'meta'];

export default function SettingsPage() {
  const params  = useParams();
  const id      = params.id as string;
  const router  = useRouter();

  const { workspace, loading, error } = useWorkspace(id);
  const { nodes, edges } = useGraphData(id);

  const [name,   setName]   = useState('');
  const [domain, setDomain] = useState('');
  const [scale,  setScale]  = useState('');

  const [saving,        setSaving]        = useState(false);
  const [saveError,     setSaveError]     = useState<string | null>(null);
  const [saveSuccess,   setSaveSuccess]   = useState(false);

  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteText,        setDeleteText]        = useState('');
  const [deleting,          setDeleting]          = useState(false);
  const [deleteError,       setDeleteError]       = useState<string | null>(null);

  useEffect(() => {
    if (workspace) {
      setName(workspace.name);
      setDomain(workspace.domain);
      setScale(workspace.scale);
    }
  }, [workspace]);

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    setSaving(true);
    setSaveError(null);
    setSaveSuccess(false);
    try {
      // workspacesApi does not have update yet; call via internal request pattern
      const apiKey =
        typeof window !== 'undefined'
          ? localStorage.getItem('dialectica_api_key') || ''
          : '';
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'}/v1/workspaces/${id}`,
        {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
            'X-API-Key': apiKey,
          },
          body: JSON.stringify({ name: name.trim(), domain, scale }),
        },
      );
      if (!res.ok) {
        const text = await res.text().catch(() => res.statusText);
        throw new Error(text);
      }
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      setSaveError(err instanceof Error ? err.message : 'Failed to save');
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete() {
    if (deleteText !== workspace?.name) return;
    setDeleting(true);
    setDeleteError(null);
    try {
      await workspacesApi.delete(id);
      router.push('/workspaces');
    } catch (err) {
      setDeleteError(err instanceof Error ? err.message : 'Delete failed');
      setDeleting(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-48">
        <Loader2 className="w-7 h-7 text-zinc-600 animate-spin" />
      </div>
    );
  }

  if (error || !workspace) {
    return (
      <div className="p-6">
        <p className="text-sm text-red-400">{error ?? 'Workspace not found'}</p>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-2xl space-y-8">
      {/* Header */}
      <div className="flex items-center gap-2">
        <Settings className="w-5 h-5 text-zinc-400" />
        <h2 className="text-lg font-semibold text-zinc-100">Workspace Settings</h2>
      </div>

      {/* Edit form */}
      <form onSubmit={handleSave} className="rounded-xl border border-[#27272a] bg-[#18181b] p-5 space-y-5">
        <h3 className="text-xs font-semibold uppercase tracking-widest text-zinc-500">
          General
        </h3>

        {/* Name */}
        <div className="space-y-1.5">
          <label className="text-sm font-medium text-zinc-300" htmlFor="ws-name">
            Name
          </label>
          <input
            id="ws-name"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full rounded-lg border border-[#27272a] bg-[#09090b] px-3 py-2 text-sm text-zinc-100 placeholder-zinc-600 focus:border-violet-500/60 focus:outline-none focus:ring-1 focus:ring-violet-500/30 transition-colors"
            placeholder="Workspace name"
          />
        </div>

        {/* Domain */}
        <div className="space-y-1.5">
          <label className="text-sm font-medium text-zinc-300" htmlFor="ws-domain">
            Domain
          </label>
          <select
            id="ws-domain"
            value={domain}
            onChange={(e) => setDomain(e.target.value)}
            className="w-full rounded-lg border border-[#27272a] bg-[#09090b] px-3 py-2 text-sm text-zinc-100 focus:border-violet-500/60 focus:outline-none focus:ring-1 focus:ring-violet-500/30 transition-colors"
          >
            {DOMAINS.map((d) => (
              <option key={d} value={d} className="bg-[#09090b] capitalize">
                {d}
              </option>
            ))}
          </select>
        </div>

        {/* Scale */}
        <div className="space-y-1.5">
          <label className="text-sm font-medium text-zinc-300" htmlFor="ws-scale">
            Scale
          </label>
          <select
            id="ws-scale"
            value={scale}
            onChange={(e) => setScale(e.target.value)}
            className="w-full rounded-lg border border-[#27272a] bg-[#09090b] px-3 py-2 text-sm text-zinc-100 focus:border-violet-500/60 focus:outline-none focus:ring-1 focus:ring-violet-500/30 transition-colors"
          >
            {SCALES.map((s) => (
              <option key={s} value={s} className="bg-[#09090b] capitalize">
                {s}
              </option>
            ))}
          </select>
        </div>

        {saveError && (
          <p className="text-sm text-red-400">{saveError}</p>
        )}

        <div className="flex items-center gap-3">
          <button
            type="submit"
            disabled={saving || !name.trim()}
            className="inline-flex items-center gap-2 rounded-lg bg-violet-600 hover:bg-violet-700 disabled:opacity-50 px-4 py-2 text-sm font-medium text-white transition-colors"
          >
            {saving ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Save className="w-3.5 h-3.5" />}
            {saving ? 'Saving…' : 'Save Changes'}
          </button>
          {saveSuccess && (
            <span className="flex items-center gap-1.5 text-sm text-emerald-400">
              <Check className="w-3.5 h-3.5" /> Saved
            </span>
          )}
        </div>
      </form>

      {/* API reference */}
      <div className="rounded-xl border border-[#27272a] bg-[#18181b] p-5 space-y-4">
        <h3 className="text-xs font-semibold uppercase tracking-widest text-zinc-500">
          API Reference
        </h3>
        <div className="space-y-2">
          <div className="flex items-start gap-3 rounded-lg border border-[#27272a] bg-[#09090b] px-3 py-2.5">
            <Hash className="w-3.5 h-3.5 text-zinc-500 mt-0.5 shrink-0" />
            <div>
              <p className="text-[10px] uppercase tracking-widest text-zinc-500 font-medium">Workspace ID</p>
              <p className="text-xs text-zinc-200 font-mono mt-0.5 break-all">{workspace.id}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Raw graph stats */}
      <div className="rounded-xl border border-[#27272a] bg-[#18181b] p-5 space-y-4">
        <h3 className="text-xs font-semibold uppercase tracking-widest text-zinc-500">
          Raw Graph Statistics
        </h3>
        <div className="grid grid-cols-2 gap-3">
          <div className="rounded-lg border border-[#27272a] bg-zinc-900/40 px-4 py-3 flex items-center gap-3">
            <Layers className="w-5 h-5 text-violet-400" />
            <div>
              <p className="text-2xl font-bold text-zinc-100">{nodes.length}</p>
              <p className="text-xs text-zinc-500">Total Nodes</p>
            </div>
          </div>
          <div className="rounded-lg border border-[#27272a] bg-zinc-900/40 px-4 py-3 flex items-center gap-3">
            <Network className="w-5 h-5 text-teal-400" />
            <div>
              <p className="text-2xl font-bold text-zinc-100">{edges.length}</p>
              <p className="text-xs text-zinc-500">Total Edges</p>
            </div>
          </div>
        </div>

        {/* Node breakdown */}
        {nodes.length > 0 && (
          <div className="space-y-1.5">
            {Object.entries(
              nodes.reduce<Record<string, number>>((acc, n) => {
                acc[n.label] = (acc[n.label] ?? 0) + 1;
                return acc;
              }, {}),
            )
              .sort(([, a], [, b]) => b - a)
              .map(([label, count]) => (
                <div key={label} className="flex items-center gap-3">
                  <span className="text-xs text-zinc-400 capitalize w-28 shrink-0">{label}</span>
                  <div className="flex-1 h-1.5 rounded-full bg-zinc-800 overflow-hidden">
                    <div
                      className="h-full rounded-full bg-violet-600/60"
                      style={{ width: `${(count / nodes.length) * 100}%` }}
                    />
                  </div>
                  <span className="text-xs tabular-nums text-zinc-500 w-8 text-right">{count}</span>
                </div>
              ))}
          </div>
        )}
      </div>

      {/* Danger zone */}
      <div className="rounded-xl border border-red-500/30 bg-red-500/5 p-5 space-y-4">
        <h3 className="text-xs font-semibold uppercase tracking-widest text-red-500">
          Danger Zone
        </h3>

        {!showDeleteConfirm ? (
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="text-sm font-medium text-zinc-200">Delete this workspace</p>
              <p className="text-xs text-zinc-500 mt-0.5">
                Permanently removes the workspace and all graph data. This action cannot be undone.
              </p>
            </div>
            <button
              onClick={() => setShowDeleteConfirm(true)}
              className="inline-flex items-center gap-2 rounded-lg border border-red-500/40 bg-red-500/10 hover:bg-red-500/20 px-4 py-2 text-sm font-medium text-red-400 transition-colors shrink-0"
            >
              <Trash2 className="w-3.5 h-3.5" />
              Delete Workspace
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-start gap-2">
              <AlertTriangle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
              <p className="text-sm text-zinc-300">
                Type <span className="font-semibold text-zinc-100">{workspace.name}</span> to confirm deletion.
              </p>
            </div>
            <input
              type="text"
              value={deleteText}
              onChange={(e) => setDeleteText(e.target.value)}
              placeholder={workspace.name}
              className="w-full rounded-lg border border-red-500/30 bg-[#09090b] px-3 py-2 text-sm text-zinc-100 placeholder-zinc-700 focus:border-red-500/60 focus:outline-none focus:ring-1 focus:ring-red-500/30 transition-colors"
            />
            {deleteError && (
              <p className="text-sm text-red-400">{deleteError}</p>
            )}
            <div className="flex items-center gap-3">
              <button
                onClick={handleDelete}
                disabled={deleteText !== workspace.name || deleting}
                className="inline-flex items-center gap-2 rounded-lg bg-red-600 hover:bg-red-700 disabled:opacity-40 px-4 py-2 text-sm font-medium text-white transition-colors"
              >
                {deleting ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Trash2 className="w-3.5 h-3.5" />}
                {deleting ? 'Deleting…' : 'Confirm Delete'}
              </button>
              <button
                onClick={() => { setShowDeleteConfirm(false); setDeleteText(''); setDeleteError(null); }}
                className="inline-flex items-center gap-1.5 text-sm text-zinc-500 hover:text-zinc-300 transition-colors"
              >
                <X className="w-3.5 h-3.5" /> Cancel
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
