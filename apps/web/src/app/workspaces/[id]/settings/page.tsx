"use client";

import { useParams, useRouter } from "next/navigation";
import { useWorkspaceDetail } from "@/hooks/useApi";
import { api } from "@/lib/api";
import { Trash2 } from "lucide-react";

export default function SettingsPage() {
  const { id } = useParams();
  const router = useRouter();
  const { data: workspace } = useWorkspaceDetail(id as string);

  const handleDelete = async () => {
    if (!confirm("Are you sure you want to delete this workspace? This action cannot be undone.")) return;
    await api.deleteWorkspace(id as string);
    router.push("/workspaces");
  };

  return (
    <div className="max-w-2xl space-y-6">
      <h2 className="text-lg font-semibold text-text-primary">Settings</h2>

      {workspace && (
        <div className="card space-y-4">
          <div>
            <label className="text-sm text-text-secondary">Name</label>
            <p className="text-text-primary">{workspace.name}</p>
          </div>
          <div>
            <label className="text-sm text-text-secondary">Domain</label>
            <p className="text-text-primary capitalize">{workspace.domain}</p>
          </div>
          <div>
            <label className="text-sm text-text-secondary">Tier</label>
            <p className="text-text-primary capitalize">{workspace.tier}</p>
          </div>
        </div>
      )}

      <div className="card border-danger/30">
        <h3 className="font-semibold text-danger mb-2">Danger Zone</h3>
        <p className="text-sm text-text-secondary mb-4">Deleting a workspace removes all its data permanently.</p>
        <button onClick={handleDelete} className="btn-danger flex items-center gap-2">
          <Trash2 size={16} /> Delete Workspace
        </button>
      </div>
    </div>
  );
}
