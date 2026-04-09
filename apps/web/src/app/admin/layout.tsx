"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Shield,
  Settings,
  Network,
  Layers,
  Users,
  LayoutDashboard,
  Database,
  Cpu,
  Heart,
  BarChart3,
  ExternalLink,
  Target,
} from "lucide-react";
import { cn } from "@/lib/utils";

const ADMIN_NAV = [
  { href: "/admin", label: "Overview", icon: LayoutDashboard },
  { href: "/admin/system", label: "System Health", icon: Settings },
  { href: "/admin/graph", label: "Graph Explorer", icon: Network },
  { href: "/admin/architecture", label: "Architecture", icon: Layers },
  { href: "/admin/users", label: "Users", icon: Users },
  { href: "/admin/workspaces", label: "Workspaces", icon: LayoutDashboard },
  { href: "/admin/data", label: "Data", icon: Database },
  { href: "/admin/ontology", label: "Ontology", icon: Layers },
  { href: "/admin/extraction", label: "Extraction", icon: Cpu },
  { href: "/admin/graph-health", label: "Graph Health", icon: Heart },
  { href: "/admin/benchmarks", label: "Benchmarks", icon: Target },
  { href: "/admin/usage", label: "Usage", icon: BarChart3 },
  { href: "/admin/api-keys", label: "API Keys", icon: Shield },
];

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border pb-3">
        <div className="flex items-center gap-2">
          <Shield size={20} className="text-danger" />
          <h1 className="text-lg font-bold text-text-primary">Administration</h1>
        </div>
        <a
          href="https://tacitus.me"
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs text-text-secondary hover:text-accent transition-colors flex items-center gap-1"
        >
          tacitus.me <ExternalLink size={10} />
        </a>
      </div>

      {/* Secondary nav tabs */}
      <div className="flex flex-wrap gap-1 border-b border-border pb-2 -mt-1">
        {ADMIN_NAV.map((item) => {
          const isActive =
            item.href === "/admin"
              ? pathname === "/admin"
              : pathname === item.href || pathname.startsWith(item.href + "/");
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-xs transition-colors",
                isActive
                  ? "bg-accent/10 text-accent font-medium"
                  : "text-text-secondary hover:text-text-primary hover:bg-surface-hover",
              )}
            >
              <item.icon size={12} />
              {item.label}
            </Link>
          );
        })}
      </div>

      {/* Content */}
      {children}
    </div>
  );
}
