"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  FolderOpen,
  Server,
  BarChart3,
  Key,
  Users,
  Database,
  BookOpen,
  GitBranch,
  Activity,
  ArrowRight,
} from "lucide-react";
import { workspacesApi } from "@/lib/api";
import { SystemHealthCard } from "@/components/admin/SystemHealthCard";

interface SummaryStats {
  totalWorkspaces: number;
  totalNodes: number;
  totalEdges: number;
}

const QUICK_LINKS = [
  {
    label: "Workspaces",
    href: "/admin/workspaces",
    icon: FolderOpen,
    description: "Manage all conflict workspaces",
    color: "text-blue-400",
    bg: "bg-blue-500/10",
  },
  {
    label: "System",
    href: "/admin/system",
    icon: Server,
    description: "Backend and environment config",
    color: "text-green-400",
    bg: "bg-green-500/10",
  },
  {
    label: "Usage",
    href: "/admin/usage",
    icon: BarChart3,
    description: "API usage statistics",
    color: "text-yellow-400",
    bg: "bg-yellow-500/10",
  },
  {
    label: "API Keys",
    href: "/admin/api-keys",
    icon: Key,
    description: "Manage API authentication",
    color: "text-purple-400",
    bg: "bg-purple-500/10",
  },
  {
    label: "Users",
    href: "/admin/users",
    icon: Users,
    description: "Tenant and user management",
    color: "text-pink-400",
    bg: "bg-pink-500/10",
  },
  {
    label: "Data",
    href: "/admin/data",
    icon: Database,
    description: "Import, export, seed data",
    color: "text-orange-400",
    bg: "bg-orange-500/10",
  },
  {
    label: "Ontology",
    href: "/admin/ontology",
    icon: BookOpen,
    description: "Node and edge types reference",
    color: "text-teal-400",
    bg: "bg-teal-500/10",
  },
  {
    label: "Extraction",
    href: "/admin/extraction",
    icon: GitBranch,
    description: "Pipeline jobs and status",
    color: "text-indigo-400",
    bg: "bg-indigo-500/10",
  },
  {
    label: "Graph Health",
    href: "/admin/graph-health",
    icon: Activity,
    description: "Quality scores per workspace",
    color: "text-red-400",
    bg: "bg-red-500/10",
  },
];

export default function AdminOverviewPage() {
  const [stats, setStats] = useState<SummaryStats | null>(null);
  const [loadingStats, setLoadingStats] = useState(true);

  useEffect(() => {
    workspacesApi.list()
      .then((res) => {
        const ws = res.workspaces ?? [];
        setStats({
          totalWorkspaces: res.total ?? ws.length,
          totalNodes: ws.reduce((s, w) => s + (w.node_count ?? 0), 0),
          totalEdges: ws.reduce((s, w) => s + (w.edge_count ?? 0), 0),
        });
      })
      .catch(() => setStats({ totalWorkspaces: 0, totalNodes: 0, totalEdges: 0 }))
      .finally(() => setLoadingStats(false));
  }, []);

  return (
    <div className="p-8 max-w-5xl">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-[#fafafa] mb-1">Admin Overview</h1>
        <p className="text-[#a1a1aa] text-sm">
          System status, configuration, and administrative controls for DIALECTICA.
        </p>
      </div>

      {/* System health */}
      <div className="mb-8">
        <h2 className="text-[#fafafa] font-semibold text-sm mb-3 uppercase tracking-wider">
          System Health
        </h2>
        <SystemHealthCard />
      </div>

      {/* Summary stats */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        {[
          { label: "Total Workspaces", value: stats?.totalWorkspaces },
          { label: "Total Nodes", value: stats?.totalNodes },
          { label: "Total Edges", value: stats?.totalEdges },
        ].map((stat) => (
          <div
            key={stat.label}
            className="bg-[#18181b] border border-[#27272a] rounded-lg p-4"
          >
            <p className="text-[#71717a] text-xs mb-1">{stat.label}</p>
            {loadingStats ? (
              <div className="h-8 w-20 bg-[#27272a] rounded animate-pulse" />
            ) : (
              <p className="text-2xl font-bold text-[#fafafa]">
                {(stat.value ?? 0).toLocaleString()}
              </p>
            )}
          </div>
        ))}
      </div>

      {/* Quick links grid */}
      <div>
        <h2 className="text-[#fafafa] font-semibold text-sm mb-3 uppercase tracking-wider">
          Administration
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {QUICK_LINKS.map((link) => {
            const Icon = link.icon;
            return (
              <Link
                key={link.href}
                href={link.href}
                className="group bg-[#18181b] border border-[#27272a] rounded-lg p-4 hover:border-[#3f3f46] transition-colors"
              >
                <div className="flex items-start gap-3">
                  <div className={`p-2 rounded-md ${link.bg} flex-shrink-0`}>
                    <Icon size={16} className={link.color} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <p className="text-[#fafafa] text-sm font-medium">{link.label}</p>
                      <ArrowRight
                        size={14}
                        className="text-[#52525b] group-hover:text-[#a1a1aa] transition-colors"
                      />
                    </div>
                    <p className="text-[#71717a] text-xs mt-0.5">{link.description}</p>
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      </div>
    </div>
  );
}
