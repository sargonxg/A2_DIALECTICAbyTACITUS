"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useWorkspaceStore } from "@/hooks/useWorkspace";
import {
  Search,
  Bell,
  ChevronRight,
  ArrowRight,
  FileText,
  Globe2,
  HeartPulse,
  Home,
  Network,
  Workflow,
} from "lucide-react";
import { useState } from "react";

const QUICK_ACTIONS = [
  {
    label: "Landing",
    href: "/",
    detail: "Product story and demo entry point",
    icon: Home,
  },
  {
    label: "Situation Demo",
    href: "/situation-demo",
    detail: "Syria, Gutenberg, temporal graph, D3, live controls",
    icon: Globe2,
  },
  {
    label: "GraphOps Console",
    href: "/graphops",
    detail: "Ingestion, ontology, Databricks, graph writes, benchmarks",
    icon: Network,
  },
  {
    label: "Graph Health",
    href: "/admin/graph-health",
    detail: "Check graph service readiness",
    icon: HeartPulse,
  },
  {
    label: "Benchmarks",
    href: "/admin/benchmarks",
    detail: "Compare graph-grounded answers against baselines",
    icon: Workflow,
  },
  {
    label: "API Docs",
    href: "/developers/docs",
    detail: "Developer setup and endpoint reference",
    icon: FileText,
  },
];

function breadcrumbsFromPath(pathname: string, workspaceName?: string): { label: string; href: string }[] {
  const parts = pathname.split("/").filter(Boolean);
  const crumbs: { label: string; href: string }[] = [];
  let path = "";

  for (let i = 0; i < parts.length; i++) {
    path += "/" + parts[i];
    let label = parts[i].charAt(0).toUpperCase() + parts[i].slice(1);

    // Replace dynamic segments
    if (parts[i - 1] === "workspaces" && parts[i] !== "new") {
      label = workspaceName || "Workspace";
    }
    if (parts[i] === "[id]") continue;

    crumbs.push({ label: label.replace(/-/g, " "), href: path });
  }

  return crumbs;
}

export default function Header() {
  const pathname = usePathname();
  const { currentWorkspace } = useWorkspaceStore();
  const [searchOpen, setSearchOpen] = useState(false);
  const crumbs = breadcrumbsFromPath(pathname, currentWorkspace?.name);

  return (
    <header className="h-14 border-b border-border bg-background/80 backdrop-blur-sm flex items-center justify-between px-4">
      {/* Breadcrumbs */}
      <nav className="flex items-center gap-1 text-sm">
        {crumbs.length === 0 ? (
          <span className="text-text-primary font-medium">Landing</span>
        ) : (
          crumbs.map((crumb, i) => (
            <span key={crumb.href} className="flex items-center gap-1">
              {i > 0 && <ChevronRight size={14} className="text-text-secondary" />}
              <span
                className={
                  i === crumbs.length - 1
                    ? "text-text-primary font-medium"
                    : "text-text-secondary"
                }
              >
                {crumb.label}
              </span>
            </span>
          ))
        )}
      </nav>

      {/* Right side */}
      <div className="flex items-center gap-2">
        {/* Search */}
        <button
          onClick={() => setSearchOpen(!searchOpen)}
          className="btn-ghost flex items-center gap-2"
        >
          <Search size={16} />
          <span className="text-text-secondary text-xs hidden sm:inline">
            <kbd className="px-1.5 py-0.5 bg-surface rounded text-[10px] border border-border">
              &#8984;K
            </kbd>
          </span>
        </button>

        <Link href="/situation-demo" className="btn-secondary hidden items-center gap-2 md:inline-flex">
          Demo
          <ArrowRight size={14} />
        </Link>

        {/* Notifications */}
        <button className="btn-ghost relative p-2">
          <Bell size={16} />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-accent rounded-full" />
        </button>
      </div>

      {/* Command palette overlay */}
      {searchOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-50 flex items-start justify-center pt-[20vh]"
          onClick={() => setSearchOpen(false)}
        >
          <div
            className="w-full max-w-lg bg-surface border border-border rounded-lg shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center px-4 border-b border-border">
              <Search size={16} className="text-text-secondary" />
              <input
                autoFocus
                type="text"
                placeholder="Quick open demo, graph, health, docs..."
                className="w-full bg-transparent px-3 py-3 text-sm text-text-primary placeholder:text-text-secondary outline-none"
              />
            </div>
            <div className="p-2">
              <p className="px-2 py-2 text-[11px] font-semibold uppercase tracking-wide text-text-secondary">
                Demo-ready quick actions
              </p>
              <div className="grid gap-1">
                {QUICK_ACTIONS.map((action) => {
                  const Icon = action.icon;
                  return (
                    <Link
                      key={action.href}
                      href={action.href}
                      onClick={() => setSearchOpen(false)}
                      className="flex items-start gap-3 rounded-md px-3 py-2 text-left transition-colors hover:bg-surface-hover"
                    >
                      <div className="mt-0.5 rounded-md bg-accent/10 p-1.5 text-accent">
                        <Icon size={15} />
                      </div>
                      <div className="min-w-0">
                        <p className="text-sm font-medium text-text-primary">{action.label}</p>
                        <p className="mt-0.5 text-xs leading-4 text-text-secondary">{action.detail}</p>
                      </div>
                    </Link>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      )}
    </header>
  );
}
