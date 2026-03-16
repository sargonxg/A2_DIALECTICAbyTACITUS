"use client";

import { useRouter } from "next/navigation";
import Link from "next/link";
import { Plus, FolderOpen, RefreshCw, AlertCircle, Loader2 } from "lucide-react";
import { useWorkspaceList } from "@/hooks/useWorkspace";
import { WorkspaceCard } from "@/components/workspace/WorkspaceCard";

export default function WorkspacesPage() {
  const router = useRouter();
  const { workspaces, loading, error, refetch } = useWorkspaceList();

  return (
    <div className="min-h-full p-8">
      {/* Page header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-[#fafafa] mb-1">Workspaces</h1>
          <p className="text-[#a1a1aa] text-sm">
            Manage your conflict analysis workspaces.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={refetch}
            disabled={loading}
            className="p-2 rounded-md text-[#a1a1aa] hover:text-[#fafafa] hover:bg-[#27272a] transition-colors disabled:opacity-50"
            title="Refresh"
            aria-label="Refresh workspaces"
          >
            <RefreshCw size={16} className={loading ? "animate-spin" : ""} />
          </button>
          <Link
            href="/workspaces/new"
            className="inline-flex items-center gap-2 px-4 py-2 bg-teal-600 hover:bg-teal-700 text-white text-sm font-medium rounded-md transition-colors"
          >
            <Plus size={15} />
            New Workspace
          </Link>
        </div>
      </div>

      {/* Loading state */}
      {loading && (
        <div className="flex items-center justify-center py-24">
          <div className="flex flex-col items-center gap-3">
            <Loader2 size={32} className="text-teal-500 animate-spin" />
            <p className="text-[#a1a1aa] text-sm">Loading workspaces…</p>
          </div>
        </div>
      )}

      {/* Error state */}
      {!loading && error && (
        <div className="bg-[#18181b] border border-red-500/30 rounded-lg p-6">
          <div className="flex items-start gap-3">
            <AlertCircle size={20} className="text-red-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-[#fafafa] font-medium mb-1">Failed to load workspaces</p>
              <p className="text-[#a1a1aa] text-sm mb-4">{error}</p>
              <button
                onClick={refetch}
                className="inline-flex items-center gap-2 px-3 py-1.5 bg-[#27272a] hover:bg-[#3f3f46] text-[#fafafa] text-sm rounded-md transition-colors"
              >
                <RefreshCw size={13} />
                Try again
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Empty state */}
      {!loading && !error && workspaces.length === 0 && (
        <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-12 text-center">
          <FolderOpen size={40} className="text-[#52525b] mx-auto mb-4" />
          <h3 className="text-[#fafafa] font-semibold mb-2">No workspaces yet</h3>
          <p className="text-[#a1a1aa] text-sm mb-6 max-w-sm mx-auto">
            Create a workspace to begin mapping and analysing a conflict. Each workspace
            holds a full knowledge graph of actors, events, issues, and dynamics.
          </p>
          <Link
            href="/workspaces/new"
            className="inline-flex items-center gap-2 px-4 py-2 bg-teal-600 hover:bg-teal-700 text-white text-sm font-medium rounded-md transition-colors"
          >
            <Plus size={14} />
            Create your first workspace
          </Link>
        </div>
      )}

      {/* Workspace grid */}
      {!loading && !error && workspaces.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {workspaces.map((workspace) => (
            <WorkspaceCard
              key={workspace.id}
              workspace={workspace}
              onClick={() => router.push(`/workspaces/${workspace.id}`)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
