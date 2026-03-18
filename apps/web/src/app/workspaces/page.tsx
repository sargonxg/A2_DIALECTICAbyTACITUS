"use client";

import { useState } from "react";
import Link from "next/link";
import { useWorkspaces } from "@/hooks/useApi";
import WorkspaceCard from "@/components/workspace/WorkspaceCard";
import { Plus, Search } from "lucide-react";

export default function WorkspacesPage() {
  const [search, setSearch] = useState("");
  const { data, isLoading } = useWorkspaces();

  const workspaces = (data?.items ?? []).filter(
    (ws) => !search || ws.name.toLowerCase().includes(search.toLowerCase()),
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-text-primary">Workspaces</h1>
        <Link href="/workspaces/new" className="btn-primary flex items-center gap-2">
          <Plus size={16} /> Create Workspace
        </Link>
      </div>

      <div className="relative max-w-sm">
        <Search size={14} className="absolute left-3 top-2.5 text-text-secondary" />
        <input type="text" placeholder="Search workspaces..." value={search} onChange={(e) => setSearch(e.target.value)} className="input-base w-full pl-9" />
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => <div key={i} className="card h-32 animate-pulse bg-surface-hover" />)}
        </div>
      ) : workspaces.length === 0 ? (
        <div className="text-center py-16">
          <p className="text-text-secondary">No workspaces yet.</p>
          <Link href="/workspaces/new" className="text-accent hover:underline text-sm mt-2 inline-block">Create your first workspace</Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {workspaces.map((ws) => <WorkspaceCard key={ws.id} workspace={ws} />)}
        </div>
      )}
    </div>
  );
}
