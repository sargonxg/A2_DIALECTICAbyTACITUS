"use client";

import { useEffect, useState } from "react";
import { Users, Key, Info, ArrowRight } from "lucide-react";
import Link from "next/link";

export default function UsersPage() {
  const [apiKey, setApiKey] = useState("");

  useEffect(() => {
    setApiKey(localStorage.getItem("dialectica_api_key") || "");
  }, []);

  function maskKey(key: string): string {
    if (!key) return "";
    if (key.length <= 4) return "****";
    return "****" + key.slice(-4);
  }

  return (
    <div className="p-8 max-w-3xl">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-[#fafafa] mb-1">Users & Tenants</h1>
        <p className="text-[#a1a1aa] text-sm">User and tenant management for DIALECTICA.</p>
      </div>

      {/* Current API key info */}
      <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-5 mb-6">
        <div className="flex items-center gap-2 mb-4">
          <Key size={16} className="text-[#71717a]" />
          <h2 className="text-[#fafafa] text-sm font-semibold">Current API Key</h2>
        </div>
        <div className="flex items-center gap-3 p-3 bg-[#09090b] border border-[#27272a] rounded-md mb-3">
          <Key size={13} className="text-[#52525b] flex-shrink-0" />
          <span className="text-sm font-mono text-[#a1a1aa] flex-1">
            {apiKey ? maskKey(apiKey) : <span className="text-[#52525b] italic">Not set</span>}
          </span>
        </div>
        <Link
          href="/admin/api-keys"
          className="inline-flex items-center gap-1.5 text-teal-400 text-xs hover:text-teal-300 transition-colors"
        >
          Manage API keys <ArrowRight size={12} />
        </Link>
      </div>

      {/* Placeholder notice */}
      <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-5 mb-6">
        <div className="flex items-start gap-3">
          <div className="p-2 rounded-md bg-[#27272a] flex-shrink-0">
            <Users size={16} className="text-[#71717a]" />
          </div>
          <div>
            <h3 className="text-[#fafafa] text-sm font-semibold mb-2">Full User Management</h3>
            <p className="text-[#71717a] text-sm leading-relaxed mb-3">
              Comprehensive user and tenant management — including user creation, role assignment, 
              permission scoping, and audit logs — requires backend configuration with a user 
              management service (e.g., Keycloak, Auth0, or the DIALECTICA Identity module).
            </p>
            <p className="text-[#71717a] text-sm leading-relaxed">
              In the current deployment mode, authentication is handled via API keys. Each key 
              is associated with a role (<code className="font-mono text-[#a1a1aa] text-xs">admin</code> or{" "}
              <code className="font-mono text-[#a1a1aa] text-xs">analyst</code>) configured on 
              the backend.
            </p>
          </div>
        </div>
      </div>

      {/* Role descriptions */}
      <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-5 mb-6">
        <h2 className="text-[#fafafa] text-sm font-semibold mb-4">Role Reference</h2>
        <div className="space-y-3">
          {[
            {
              role: "admin",
              color: "text-red-400 bg-red-500/10 border-red-500/20",
              desc: "Full access: read/write workspaces, manage graph data, access system configuration, import/export, manage API keys.",
            },
            {
              role: "analyst",
              color: "text-blue-400 bg-blue-500/10 border-blue-500/20",
              desc: "Read-only access to workspaces and analysis endpoints. Can run reasoning, escalation, and network analysis. Cannot modify data.",
            },
            {
              role: "viewer",
              color: "text-[#71717a] bg-[#27272a] border-[#3f3f46]",
              desc: "Read-only access to workspace list and basic graph data. No access to reasoning or admin endpoints.",
            },
          ].map((r) => (
            <div key={r.role} className="flex items-start gap-3">
              <span className={`flex-shrink-0 mt-0.5 px-2 py-0.5 rounded border text-xs font-mono font-semibold ${r.color}`}>
                {r.role}
              </span>
              <p className="text-[#71717a] text-xs leading-relaxed">{r.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Info note */}
      <div className="flex items-start gap-2 p-4 bg-[#09090b] border border-[#27272a] rounded-lg">
        <Info size={14} className="text-[#52525b] flex-shrink-0 mt-0.5" />
        <p className="text-[#52525b] text-xs leading-relaxed">
          To configure user management, set up the DIALECTICA backend with the{" "}
          <code className="font-mono text-[#71717a]">AUTH_PROVIDER</code> environment variable 
          pointing to your identity provider. See the{" "}
          <Link href="/developers/docs" className="text-teal-500 hover:text-teal-400 underline">
            API documentation
          </Link>{" "}
          for authentication configuration options.
        </p>
      </div>
    </div>
  );
}
