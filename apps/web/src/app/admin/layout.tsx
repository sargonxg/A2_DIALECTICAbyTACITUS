"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  FolderOpen,
  Server,
  BarChart3,
  Key,
  Users,
  Database,
  BookOpen,
  GitBranch,
  Activity,
} from "lucide-react";

interface AdminNavItem {
  label: string;
  href: string;
  icon: React.ComponentType<{ className?: string; size?: number }>;
}

const ADMIN_NAV: AdminNavItem[] = [
  { label: "Overview", href: "/admin", icon: LayoutDashboard },
  { label: "Workspaces", href: "/admin/workspaces", icon: FolderOpen },
  { label: "System", href: "/admin/system", icon: Server },
  { label: "Usage", href: "/admin/usage", icon: BarChart3 },
  { label: "API Keys", href: "/admin/api-keys", icon: Key },
  { label: "Users", href: "/admin/users", icon: Users },
  { label: "Data", href: "/admin/data", icon: Database },
  { label: "Ontology", href: "/admin/ontology", icon: BookOpen },
  { label: "Extraction", href: "/admin/extraction", icon: GitBranch },
  { label: "Graph Health", href: "/admin/graph-health", icon: Activity },
];

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  function isActive(href: string): boolean {
    if (href === "/admin") return pathname === "/admin";
    return pathname === href || pathname.startsWith(href + "/");
  }

  return (
    <div className="min-h-full flex flex-col">
      {/* Admin header banner */}
      <div className="bg-[#18181b] border-b border-[#27272a] px-8 py-3 flex items-center gap-3">
        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-teal-600/20 text-teal-400 border border-teal-600/30 tracking-wider uppercase">
          Admin
        </span>
        <span className="text-[#52525b] text-sm">System administration and configuration</span>
      </div>

      <div className="flex flex-1 min-h-0">
        {/* Admin sub-navigation */}
        <aside className="w-52 bg-[#18181b] border-r border-[#27272a] flex-shrink-0 py-4">
          <nav>
            <ul className="space-y-0.5 px-2">
              {ADMIN_NAV.map((item) => {
                const active = isActive(item.href);
                const Icon = item.icon;
                return (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      className={`flex items-center gap-2.5 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                        active
                          ? "bg-[#27272a] text-teal-400"
                          : "text-[#71717a] hover:text-[#fafafa] hover:bg-[#27272a]/50"
                      }`}
                    >
                      <Icon
                        size={14}
                        className={active ? "text-teal-400" : ""}
                      />
                      {item.label}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </nav>
        </aside>

        {/* Page content */}
        <main className="flex-1 min-w-0 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
