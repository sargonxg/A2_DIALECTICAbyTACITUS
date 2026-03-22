"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useWorkspaceStore } from "@/hooks/useWorkspace";
import {
  LayoutDashboard,
  MessageSquare,
  GitCompare,
  Globe,
  BookOpen,
  BookMarked,
  FileCode,
  Play,
  Key,
  Package,
  Code2,
  Users,
  Database,
  Layers,
  Cpu,
  Heart,
  BarChart3,
  Settings,
  ChevronLeft,
  ChevronRight,
  Shield,
  User,
  LogOut,
} from "lucide-react";

interface NavItem {
  label: string;
  href: string;
  icon: React.ElementType;
}

interface NavGroup {
  title: string;
  items: NavItem[];
}

const NAV_GROUPS: NavGroup[] = [
  {
    title: "WORKBENCH",
    items: [
      { label: "Workspaces", href: "/workspaces", icon: LayoutDashboard },
      { label: "Ask", href: "/ask", icon: MessageSquare },
      { label: "Compare", href: "/compare", icon: GitCompare },
      { label: "Explore", href: "/explore", icon: Globe },
    ],
  },
  {
    title: "THEORY",
    items: [
      { label: "Frameworks", href: "/theory", icon: BookOpen },
      { label: "Glossary", href: "/theory?tab=glossary", icon: BookMarked },
    ],
  },
  {
    title: "DEVELOPERS",
    items: [
      { label: "API Docs", href: "/developers/docs", icon: FileCode },
      { label: "Playground", href: "/developers/playground", icon: Play },
      { label: "API Keys", href: "/developers/keys", icon: Key },
      { label: "SDKs", href: "/developers/sdks", icon: Package },
      { label: "Examples", href: "/developers/examples", icon: Code2 },
    ],
  },
  {
    title: "ADMIN",
    items: [
      { label: "System Health", href: "/admin/system", icon: Settings },
      { label: "Graph Explorer", href: "/admin/graph", icon: Database },
      { label: "Architecture", href: "/admin/architecture", icon: Layers },
      { label: "Users", href: "/admin/users", icon: Users },
      { label: "Workspaces", href: "/admin/workspaces", icon: LayoutDashboard },
      { label: "Data", href: "/admin/data", icon: Database },
      { label: "Ontology", href: "/admin/ontology", icon: Layers },
      { label: "Extraction", href: "/admin/extraction", icon: Cpu },
      { label: "Graph Health", href: "/admin/graph-health", icon: Heart },
      { label: "Usage", href: "/admin/usage", icon: BarChart3 },
      { label: "API Keys", href: "/admin/api-keys", icon: Shield },
    ],
  },
];

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const pathname = usePathname();
  const { currentWorkspace } = useWorkspaceStore();

  return (
    <aside
      className={cn(
        "flex flex-col h-screen bg-background border-r border-border transition-all duration-200",
        collapsed ? "w-16" : "w-[280px]",
      )}
    >
      {/* Logo */}
      <div className="flex items-center justify-between px-4 h-14 border-b border-border">
        {!collapsed && (
          <Link href="/" className="flex items-center gap-2">
            <span className="text-accent font-mono font-bold text-lg">DIALECTICA</span>
            <span className="text-text-secondary text-xs font-mono">TACITUS&#x25F3;</span>
          </Link>
        )}
        {collapsed && (
          <Link href="/" className="mx-auto">
            <span className="text-accent font-mono font-bold text-lg">D</span>
          </Link>
        )}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="btn-ghost p-1"
        >
          {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </button>
      </div>

      {/* Workspace indicator */}
      {currentWorkspace && !collapsed && (
        <div className="px-4 py-2 border-b border-border">
          <p className="text-xs text-text-secondary">Current Workspace</p>
          <p className="text-sm text-text-primary truncate font-medium">
            {currentWorkspace.name}
          </p>
        </div>
      )}

      {/* Nav groups */}
      <nav className="flex-1 overflow-y-auto py-2 space-y-4">
        {NAV_GROUPS.map((group) => (
          <div key={group.title}>
            {!collapsed && (
              <p className="px-4 py-1 text-[10px] font-semibold text-text-secondary tracking-widest uppercase">
                {group.title}
              </p>
            )}
            <ul className="space-y-0.5 px-2">
              {group.items.map((item) => {
                const active = pathname === item.href || pathname.startsWith(item.href + "/");
                return (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      className={cn(
                        "flex items-center gap-3 px-2 py-1.5 rounded-md text-sm transition-colors",
                        active
                          ? "bg-accent/10 text-accent"
                          : "text-text-secondary hover:text-text-primary hover:bg-surface-hover",
                        collapsed && "justify-center",
                      )}
                      title={collapsed ? item.label : undefined}
                    >
                      <item.icon size={18} />
                      {!collapsed && <span>{item.label}</span>}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </nav>

      {/* User */}
      <div className="border-t border-border p-2">
        <div
          className={cn(
            "flex items-center gap-3 px-2 py-2 rounded-md",
            collapsed && "justify-center",
          )}
        >
          <div className="w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center">
            <User size={16} className="text-accent" />
          </div>
          {!collapsed && (
            <div className="flex-1 min-w-0">
              <p className="text-sm text-text-primary truncate">Analyst</p>
              <p className="text-xs text-text-secondary">admin</p>
            </div>
          )}
          {!collapsed && (
            <button className="btn-ghost p-1" title="Sign out">
              <LogOut size={16} />
            </button>
          )}
        </div>
      </div>
    </aside>
  );
}
