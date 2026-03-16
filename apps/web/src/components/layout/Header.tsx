"use client";

import { usePathname } from "next/navigation";
import { useWorkspaceStore } from "@/hooks/useWorkspace";
import {
  Search,
  Bell,
  ChevronRight,
} from "lucide-react";
import { useState } from "react";

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
        {crumbs.map((crumb, i) => (
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
        ))}
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
                placeholder="Search workspaces, entities, theory..."
                className="w-full bg-transparent px-3 py-3 text-sm text-text-primary placeholder:text-text-secondary outline-none"
              />
            </div>
            <div className="p-2 text-sm text-text-secondary text-center py-8">
              Start typing to search...
            </div>
          </div>
        </div>
      )}
    </header>
  );
}
