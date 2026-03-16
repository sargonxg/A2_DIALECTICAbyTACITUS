'use client';

import React, { useEffect, useState } from 'react';
import { useParams, usePathname, useRouter } from 'next/navigation';
import Link from 'next/link';
import { workspacesApi, type Workspace } from '@/lib/api';
import {
  LayoutDashboard,
  GitFork,
  Clock,
  BarChart3,
  Upload,
  Settings,
  Users,
  GitBranch,
  ChevronRight,
  Loader2,
} from 'lucide-react';

interface TabConfig {
  label: string;
  href: string;
  icon: React.ReactNode;
  exact?: boolean;
}

function buildTabs(id: string): TabConfig[] {
  const base = `/workspaces/${id}`;
  return [
    { label: 'Overview',  href: base,              icon: <LayoutDashboard size={15} />, exact: true },
    { label: 'Graph',     href: `${base}/graph`,    icon: <GitFork size={15} /> },
    { label: 'Timeline',  href: `${base}/timeline`, icon: <Clock size={15} /> },
    { label: 'Analysis',  href: `${base}/analysis`, icon: <BarChart3 size={15} /> },
    { label: 'Actors',    href: `${base}/actors`,   icon: <Users size={15} /> },
    { label: 'Causal',    href: `${base}/causal`,   icon: <GitBranch size={15} /> },
    { label: 'Ingest',    href: `${base}/ingest`,   icon: <Upload size={15} /> },
    { label: 'Settings',  href: `${base}/settings`, icon: <Settings size={15} /> },
  ];
}

function SkeletonHeader() {
  return (
    <div className="border-b border-[#27272a] px-6 py-4 animate-pulse">
      <div className="flex items-center gap-2 mb-4">
        <div className="h-4 w-24 bg-[#27272a] rounded" />
        <ChevronRight size={14} className="text-zinc-600" />
        <div className="h-4 w-40 bg-[#27272a] rounded" />
      </div>
      <div className="h-7 w-64 bg-[#27272a] rounded mb-1" />
      <div className="h-4 w-48 bg-[#27272a] rounded" />
    </div>
  );
}

export default function WorkspaceLayout({ children }: { children: React.ReactNode }) {
  const params = useParams();
  const id = params.id as string;
  const pathname = usePathname();
  const router = useRouter();

  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    workspacesApi.get(id)
      .then(setWorkspace)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, [id]);

  const tabs = buildTabs(id);

  const isActive = (tab: TabConfig): boolean => {
    if (tab.exact) return pathname === tab.href;
    return pathname.startsWith(tab.href);
  };

  return (
    <div className="flex flex-col h-full min-h-screen">
      {/* Workspace Header */}
      {loading ? (
        <SkeletonHeader />
      ) : error ? (
        <div className="border-b border-[#27272a] px-6 py-4">
          <p className="text-red-400 text-sm">Failed to load workspace: {error}</p>
          <button
            onClick={() => router.push('/workspaces')}
            className="mt-2 text-xs text-zinc-500 hover:text-zinc-300 underline"
          >
            Back to workspaces
          </button>
        </div>
      ) : workspace ? (
        <div className="border-b border-[#27272a] px-6 pt-5 pb-0 bg-[#09090b]">
          {/* Breadcrumb */}
          <nav className="flex items-center gap-1.5 text-xs text-zinc-500 mb-3">
            <Link href="/workspaces" className="hover:text-zinc-300 transition-colors">
              Workspaces
            </Link>
            <ChevronRight size={12} />
            <span className="text-zinc-400">{workspace.name}</span>
          </nav>

          {/* Title row */}
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-xl font-semibold text-zinc-100 leading-tight">
                {workspace.name}
              </h1>
              <div className="flex items-center gap-3 mt-1.5">
                <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-[#27272a] text-zinc-400 border border-[#3f3f46]">
                  {workspace.domain}
                </span>
                <span className="text-xs text-zinc-500">{workspace.scale}</span>
                <span
                  className={`text-xs font-medium px-2 py-0.5 rounded-full border ${
                    workspace.status === 'active'
                      ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                      : workspace.status === 'archived'
                      ? 'bg-zinc-500/10 text-zinc-400 border-zinc-500/30'
                      : 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                  }`}
                >
                  {workspace.status}
                </span>
                {workspace.glasl_stage != null && (
                  <span className="text-xs text-zinc-500">
                    Glasl Stage{' '}
                    <span className="text-zinc-300 font-medium">{workspace.glasl_stage}</span>
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Tab navigation */}
          <nav className="flex items-end gap-0 mt-4 -mb-px overflow-x-auto">
            {tabs.map((tab) => {
              const active = isActive(tab);
              return (
                <Link
                  key={tab.href}
                  href={tab.href}
                  className={`flex items-center gap-1.5 px-4 py-2.5 text-sm font-medium border-b-2 whitespace-nowrap transition-colors ${
                    active
                      ? 'border-violet-500 text-zinc-100'
                      : 'border-transparent text-zinc-500 hover:text-zinc-300 hover:border-zinc-600'
                  }`}
                >
                  {tab.icon}
                  {tab.label}
                </Link>
              );
            })}
          </nav>
        </div>
      ) : null}

      {/* Page content */}
      <div className="flex-1 overflow-auto">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <Loader2 size={28} className="animate-spin text-zinc-600" />
          </div>
        ) : (
          children
        )}
      </div>
    </div>
  );
}
