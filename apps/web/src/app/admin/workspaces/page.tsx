'use client';
import { useEffect, useState } from 'react';
import { workspacesApi, Workspace } from '@/lib/api';
import Link from 'next/link';
import { Trash2, ExternalLink } from 'lucide-react';

export default function AdminWorkspacesPage() {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [loading, setLoading] = useState(true);

  const load = () => {
    workspacesApi.list().then(r => {
      setWorkspaces(r.workspaces || []);
      setLoading(false);
    }).catch(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const handleDelete = async (id: string, name: string) => {
    if (!confirm(`Delete workspace "${name}"? This cannot be undone.`)) return;
    await workspacesApi.delete(id).catch(() => {});
    load();
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-white">All Workspaces</h1>
        <Link href="/workspaces/new" className="bg-teal-600 hover:bg-teal-700 text-white px-4 py-2 rounded-lg text-sm">
          + New Workspace
        </Link>
      </div>
      {loading ? (
        <p className="text-[#a1a1aa]">Loading…</p>
      ) : (
        <div className="bg-[#18181b] border border-[#27272a] rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead className="border-b border-[#27272a]">
              <tr>
                <th className="text-left px-4 py-3 text-[#a1a1aa] font-medium">Name</th>
                <th className="text-left px-4 py-3 text-[#a1a1aa] font-medium">Domain</th>
                <th className="text-left px-4 py-3 text-[#a1a1aa] font-medium">Scale</th>
                <th className="text-left px-4 py-3 text-[#a1a1aa] font-medium">Nodes</th>
                <th className="text-right px-4 py-3 text-[#a1a1aa] font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {workspaces.map(ws => (
                <tr key={ws.id} className="border-b border-[#27272a]/50 hover:bg-[#27272a]/30">
                  <td className="px-4 py-3 text-white">{ws.name}</td>
                  <td className="px-4 py-3 text-[#a1a1aa]">{ws.domain}</td>
                  <td className="px-4 py-3 text-[#a1a1aa]">{ws.scale}</td>
                  <td className="px-4 py-3 text-[#a1a1aa]">{ws.node_count ?? '—'}</td>
                  <td className="px-4 py-3 text-right flex justify-end gap-2">
                    <Link href={`/workspaces/${ws.id}`} className="text-teal-500 hover:text-teal-400 p-1">
                      <ExternalLink size={14} />
                    </Link>
                    <button onClick={() => handleDelete(ws.id, ws.name)} className="text-red-400 hover:text-red-300 p-1">
                      <Trash2 size={14} />
                    </button>
                  </td>
                </tr>
              ))}
              {workspaces.length === 0 && (
                <tr><td colSpan={5} className="px-4 py-8 text-center text-[#a1a1aa]">No workspaces found.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
