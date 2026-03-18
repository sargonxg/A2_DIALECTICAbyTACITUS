"use client";

import { useEffect } from "react";
import { useParams, usePathname } from "next/navigation";
import Link from "next/link";
import { useWorkspaceDetail } from "@/hooks/useApi";
import { useWorkspaceStore } from "@/hooks/useWorkspace";
import { cn } from "@/lib/utils";

const TABS = [
  { label: "Overview", href: "" },
  { label: "Graph", href: "/graph" },
  { label: "Ingest", href: "/ingest" },
  { label: "Actors", href: "/actors" },
  { label: "Timeline", href: "/timeline" },
  { label: "Causal", href: "/causal" },
  { label: "Analysis", href: "/analysis" },
  { label: "Settings", href: "/settings" },
];

export default function WorkspaceLayout({ children }: { children: React.ReactNode }) {
  const params = useParams();
  const pathname = usePathname();
  const id = params.id as string;
  const { data: workspace } = useWorkspaceDetail(id);
  const { setCurrentWorkspace } = useWorkspaceStore();

  useEffect(() => {
    if (workspace) setCurrentWorkspace(workspace);
    return () => setCurrentWorkspace(null);
  }, [workspace, setCurrentWorkspace]);

  const basePath = `/workspaces/${id}`;

  return (
    <div className="space-y-4">
      {workspace && (
        <div>
          <h1 className="text-xl font-bold text-text-primary">{workspace.name}</h1>
          <p className="text-sm text-text-secondary">
            {workspace.domain} &middot; {workspace.scale} &middot; {workspace.tier} tier &middot; {workspace.node_count} nodes
          </p>
        </div>
      )}

      <nav className="flex gap-1 border-b border-border pb-px overflow-x-auto">
        {TABS.map((tab) => {
          const href = `${basePath}${tab.href}`;
          const active = tab.href === "" ? pathname === basePath : pathname.startsWith(href);
          return (
            <Link key={tab.href} href={href} className={cn(
              "px-3 py-2 text-sm whitespace-nowrap border-b-2 transition-colors",
              active ? "border-accent text-accent" : "border-transparent text-text-secondary hover:text-text-primary",
            )}>
              {tab.label}
            </Link>
          );
        })}
      </nav>

      {children}
    </div>
  );
}
