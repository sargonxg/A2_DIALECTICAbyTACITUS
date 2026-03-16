"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  FolderOpen,
  MessageSquare,
  BookOpen,
  Network,
  GitCompare,
  Code2,
  Settings,
} from "lucide-react";

interface NavItem {
  label: string;
  href: string;
  icon: React.ComponentType<{ className?: string; size?: number }>;
}

const NAV_ITEMS: NavItem[] = [
  { label: "Dashboard", href: "/", icon: LayoutDashboard },
  { label: "Workspaces", href: "/workspaces", icon: FolderOpen },
  { label: "Ask", href: "/ask", icon: MessageSquare },
  { label: "Theory", href: "/theory", icon: BookOpen },
  { label: "Explore", href: "/explore", icon: Network },
  { label: "Compare", href: "/compare", icon: GitCompare },
  { label: "Developers", href: "/developers", icon: Code2 },
  { label: "Admin", href: "/admin", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  function isActive(href: string): boolean {
    if (href === "/") {
      return pathname === "/";
    }
    return pathname === href || pathname.startsWith(href + "/");
  }

  return (
    <aside className="fixed left-0 top-0 h-full w-64 bg-[#18181b] border-r border-[#27272a] flex flex-col z-40">
      {/* Logo */}
      <div className="px-6 py-5 border-b border-[#27272a]">
        <div className="flex flex-col gap-0.5">
          <span className="text-teal-500 font-bold text-lg tracking-wide leading-none">
            DIALECTICA
          </span>
          <span className="text-[#a1a1aa] text-xs tracking-widest uppercase leading-none">
            by TACITUS
          </span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 overflow-y-auto">
        <ul className="space-y-1">
          {NAV_ITEMS.map((item) => {
            const active = isActive(item.href);
            const Icon = item.icon;

            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={`
                    flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors
                    ${
                      active
                        ? "bg-[#27272a] text-teal-500"
                        : "text-[#a1a1aa] hover:text-white hover:bg-[#27272a]/50"
                    }
                  `}
                >
                  <Icon
                    size={16}
                    className={active ? "text-teal-500" : ""}
                  />
                  {item.label}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Footer */}
      <div className="px-6 py-4 border-t border-[#27272a]">
        <p className="text-[#a1a1aa] text-xs">
          v1.0.0 &mdash; Conflict Intelligence
        </p>
      </div>
    </aside>
  );
}
