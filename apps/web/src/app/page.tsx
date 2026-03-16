"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  FolderOpen,
  Activity,
  Cpu,
  BookOpen,
  Plus,
  MessageSquare,
  ArrowRight,
  Zap,
} from "lucide-react";
import { workspacesApi, theoryApi } from "@/lib/api";
import type { Workspace } from "@/lib/api";
import { WorkspaceCard } from "@/components/workspace/WorkspaceCard";

interface Stats {
  totalWorkspaces: number;
  activeConflicts: number;
  eventsProcessed: number;
  frameworksLoaded: number;
}

export default function HomePage() {
  const router = useRouter();

  const [stats, setStats] = useState<Stats>({
    totalWorkspaces: 0,
    activeConflicts: 0,
    eventsProcessed: 0,
    frameworksLoaded: 0,
  });
  const [recentWorkspaces, setRecentWorkspaces] = useState<Workspace[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadDashboard() {
      setLoading(true);
      try {
        const [workspacesResult, frameworksResult] = await Promise.allSettled([
          workspacesApi.list(),
          theoryApi.listFrameworks(),
        ]);

        let totalWorkspaces = 0;
        let recent: Workspace[] = [];
        let activeConflicts = 0;
        let eventsProcessed = 0;

        if (workspacesResult.status === "fulfilled") {
          const workspaces = workspacesResult.value.workspaces ?? [];
          totalWorkspaces = workspacesResult.value.total ?? workspaces.length;

          // Sort by updated_at descending, take last 3
          recent = [...workspaces]
            .sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())
            .slice(0, 3);

          // Derive active conflicts (glasl stage >= 4) and events
          activeConflicts = workspaces.filter(
            (w) => w.glasl_stage !== undefined && w.glasl_stage >= 4,
          ).length;

          eventsProcessed = workspaces.reduce(
            (sum, w) => sum + (w.node_count ?? 0),
            0,
          );
        }

        let frameworksLoaded = 0;
        if (frameworksResult.status === "fulfilled") {
          frameworksLoaded = frameworksResult.value.frameworks?.length ?? 0;
        }

        setStats({
          totalWorkspaces,
          activeConflicts,
          eventsProcessed,
          frameworksLoaded,
        });
        setRecentWorkspaces(recent);
      } catch {
        // Silently fail — stats show zeroes
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, []);

  const statCards = [
    {
      label: "Total Workspaces",
      value: stats.totalWorkspaces,
      icon: FolderOpen,
      color: "text-blue-400",
      bg: "bg-blue-500/10",
    },
    {
      label: "Active Conflicts",
      value: stats.activeConflicts,
      icon: Activity,
      color: "text-red-400",
      bg: "bg-red-500/10",
    },
    {
      label: "Nodes Ingested",
      value: stats.eventsProcessed,
      icon: Cpu,
      color: "text-teal-400",
      bg: "bg-teal-500/10",
    },
    {
      label: "Frameworks Loaded",
      value: stats.frameworksLoaded,
      icon: BookOpen,
      color: "text-violet-400",
      bg: "bg-violet-500/10",
    },
  ];

  return (
    <div className="min-h-full p-8">
      {/* Hero */}
      <div className="mb-10">
        <div className="flex items-center gap-2 mb-3">
          <Zap size={14} className="text-teal-500" />
          <span className="text-teal-500 text-xs font-medium tracking-widest uppercase">
            Conflict Intelligence Platform
          </span>
        </div>
        <h1 className="text-4xl font-bold text-[#fafafa] mb-3 tracking-tight">
          DIALECTICA
        </h1>
        <p className="text-[#a1a1aa] text-lg max-w-xl leading-relaxed">
          The Universal Data Layer for{" "}
          <span className="text-teal-500 font-medium">Human Friction</span>.
          Map, analyse, and navigate conflict with graph-native intelligence.
        </p>
        <div className="flex items-center gap-3 mt-6">
          <Link
            href="/workspaces/new"
            className="inline-flex items-center gap-2 px-4 py-2 bg-teal-600 hover:bg-teal-700 text-white text-sm font-medium rounded-md transition-colors"
          >
            <Plus size={15} />
            New Workspace
          </Link>
          <Link
            href="/ask"
            className="inline-flex items-center gap-2 px-4 py-2 bg-[#27272a] hover:bg-[#3f3f46] text-[#fafafa] text-sm font-medium rounded-md transition-colors"
          >
            <MessageSquare size={15} />
            Ask the Graph
          </Link>
          <Link
            href="/theory"
            className="inline-flex items-center gap-2 px-4 py-2 bg-[#27272a] hover:bg-[#3f3f46] text-[#fafafa] text-sm font-medium rounded-md transition-colors"
          >
            <BookOpen size={15} />
            Browse Theory
          </Link>
        </div>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-10">
        {statCards.map((card) => {
          const Icon = card.icon;
          return (
            <div
              key={card.label}
              className="bg-[#18181b] border border-[#27272a] rounded-lg p-4"
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-[#a1a1aa] text-xs font-medium">
                  {card.label}
                </span>
                <div className={`p-1.5 rounded-md ${card.bg}`}>
                  <Icon size={14} className={card.color} />
                </div>
              </div>
              <div className="text-2xl font-bold text-[#fafafa]">
                {loading ? (
                  <span className="inline-block w-10 h-7 bg-[#27272a] rounded animate-pulse" />
                ) : (
                  card.value.toLocaleString()
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Recent workspaces */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-[#fafafa] font-semibold text-base">
            Recent Workspaces
          </h2>
          <Link
            href="/workspaces"
            className="inline-flex items-center gap-1 text-teal-500 hover:text-teal-400 text-sm transition-colors"
          >
            View all
            <ArrowRight size={14} />
          </Link>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                className="bg-[#18181b] border border-[#27272a] rounded-lg p-4 h-40 animate-pulse"
              />
            ))}
          </div>
        ) : recentWorkspaces.length === 0 ? (
          <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-8 text-center">
            <FolderOpen size={32} className="text-[#52525b] mx-auto mb-3" />
            <p className="text-[#a1a1aa] text-sm mb-4">
              No workspaces yet. Create your first conflict workspace to get started.
            </p>
            <Link
              href="/workspaces/new"
              className="inline-flex items-center gap-2 px-4 py-2 bg-teal-600 hover:bg-teal-700 text-white text-sm font-medium rounded-md transition-colors"
            >
              <Plus size={14} />
              New Workspace
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {recentWorkspaces.map((ws) => (
              <WorkspaceCard
                key={ws.id}
                workspace={ws}
                onClick={() => router.push(`/workspaces/${ws.id}`)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
