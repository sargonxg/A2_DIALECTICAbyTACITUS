"use client";

import Link from "next/link";
import { Users, LayoutDashboard, Database, Layers, Cpu, Heart, BarChart3, Settings, Shield } from "lucide-react";

const SECTIONS = [
  { href: "/admin/users", icon: Users, label: "Users", desc: "Manage users and tenants" },
  { href: "/admin/workspaces", icon: LayoutDashboard, label: "Workspaces", desc: "All workspaces across tenants" },
  { href: "/admin/data", icon: Database, label: "Data", desc: "Import/export bulk data" },
  { href: "/admin/ontology", icon: Layers, label: "Ontology", desc: "Browse node and edge types" },
  { href: "/admin/extraction", icon: Cpu, label: "Extraction", desc: "Pipeline monitoring" },
  { href: "/admin/graph-health", icon: Heart, label: "Graph Health", desc: "Consistency checks" },
  { href: "/admin/usage", icon: BarChart3, label: "Usage", desc: "API analytics" },
  { href: "/admin/system", icon: Settings, label: "System", desc: "Service health" },
  { href: "/admin/api-keys", icon: Shield, label: "API Keys", desc: "Manage all keys" },
];

export default function AdminDashboard() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {SECTIONS.map((s) => (
        <Link key={s.href} href={s.href}>
          <div className="card-hover flex items-start gap-3">
            <s.icon size={20} className="text-accent mt-0.5" />
            <div>
              <h3 className="font-semibold text-text-primary">{s.label}</h3>
              <p className="text-sm text-text-secondary">{s.desc}</p>
            </div>
          </div>
        </Link>
      ))}
    </div>
  );
}
