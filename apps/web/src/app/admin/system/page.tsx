"use client";

import { SystemHealthCard } from "@/components/admin/SystemHealthCard";
import { Server, Globe, Shield, Info } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

const ENV_CONFIG = [
  {
    key: "NEXT_PUBLIC_API_URL",
    value: API_URL,
    description: "Backend API base URL",
  },
  {
    key: "NODE_ENV",
    value: process.env.NODE_ENV || "development",
    description: "Runtime environment",
  },
  {
    key: "NEXT_PUBLIC_APP_NAME",
    value: process.env.NEXT_PUBLIC_APP_NAME || "DIALECTICA",
    description: "Application name",
  },
];

export default function SystemPage() {
  return (
    <div className="p-8 max-w-4xl">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-[#fafafa] mb-1">System</h1>
        <p className="text-[#a1a1aa] text-sm">
          Backend configuration, environment variables, and API connectivity.
        </p>
      </div>

      {/* Health card */}
      <div className="mb-8">
        <h2 className="text-[#fafafa] font-semibold text-xs uppercase tracking-wider mb-3">
          API Health
        </h2>
        <SystemHealthCard />
      </div>

      {/* API connection info */}
      <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-5 mb-6">
        <div className="flex items-center gap-2 mb-4">
          <Globe size={16} className="text-[#71717a]" />
          <h2 className="text-[#fafafa] text-sm font-semibold">API Connection</h2>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <p className="text-[#71717a] text-xs mb-1">API URL</p>
            <p className="text-[#fafafa] text-sm font-mono bg-[#09090b] border border-[#27272a] rounded px-3 py-1.5">
              {API_URL}
            </p>
          </div>
          <div>
            <p className="text-[#71717a] text-xs mb-1">Authentication</p>
            <p className="text-[#a1a1aa] text-sm font-mono bg-[#09090b] border border-[#27272a] rounded px-3 py-1.5">
              X-API-Key header
            </p>
          </div>
        </div>
      </div>

      {/* Graph backend info */}
      <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-5 mb-6">
        <div className="flex items-center gap-2 mb-4">
          <Server size={16} className="text-[#71717a]" />
          <h2 className="text-[#fafafa] text-sm font-semibold">Graph Backend</h2>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <p className="text-[#71717a] text-xs mb-1">Type</p>
            <p className="text-[#a1a1aa] text-sm">Retrieved from /health endpoint</p>
          </div>
          <div>
            <p className="text-[#71717a] text-xs mb-1">Supported Backends</p>
            <p className="text-[#a1a1aa] text-sm">neo4j, memgraph, in-memory</p>
          </div>
          <div>
            <p className="text-[#71717a] text-xs mb-1">Protocol</p>
            <p className="text-[#a1a1aa] text-sm">Bolt / HTTP REST</p>
          </div>
        </div>
      </div>

      {/* Environment variables */}
      <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-5 mb-6">
        <div className="flex items-center gap-2 mb-4">
          <Shield size={16} className="text-[#71717a]" />
          <h2 className="text-[#fafafa] text-sm font-semibold">Environment (Public)</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[#27272a]">
                <th className="text-left text-[#71717a] text-xs font-medium pb-2 pr-6">Variable</th>
                <th className="text-left text-[#71717a] text-xs font-medium pb-2 pr-6">Value</th>
                <th className="text-left text-[#71717a] text-xs font-medium pb-2">Description</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#27272a]/50">
              {ENV_CONFIG.map((row) => (
                <tr key={row.key}>
                  <td className="py-2.5 pr-6">
                    <code className="text-teal-400 text-xs font-mono">{row.key}</code>
                  </td>
                  <td className="py-2.5 pr-6">
                    <code className="text-[#a1a1aa] text-xs font-mono">{row.value}</code>
                  </td>
                  <td className="py-2.5 text-[#71717a] text-xs">{row.description}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="flex items-start gap-2 mt-4 p-3 bg-[#09090b] rounded-md border border-[#27272a]">
          <Info size={14} className="text-[#52525b] flex-shrink-0 mt-0.5" />
          <p className="text-[#52525b] text-xs">
            Only <code className="font-mono">NEXT_PUBLIC_</code> prefixed variables are
            exposed to the browser. Sensitive backend credentials are server-side only and
            not shown here.
          </p>
        </div>
      </div>

      {/* Configuration table */}
      <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-5">
        <h2 className="text-[#fafafa] text-sm font-semibold mb-4">Application Configuration</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[#27272a]">
                <th className="text-left text-[#71717a] text-xs font-medium pb-2 pr-6">Setting</th>
                <th className="text-left text-[#71717a] text-xs font-medium pb-2">Value</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#27272a]/50">
              {[
                { setting: "Framework", value: "Next.js 15 (App Router)" },
                { setting: "API Auth Method", value: "API Key (X-API-Key header)" },
                { setting: "API Key Storage", value: "localStorage (dialectica_api_key)" },
                { setting: "Default Mode", value: "Client-side rendering" },
                { setting: "Graph Visualization", value: "d3-force / canvas" },
                { setting: "Charts", value: "Recharts 2.x" },
              ].map((row) => (
                <tr key={row.setting}>
                  <td className="py-2.5 pr-6 text-[#a1a1aa] text-xs">{row.setting}</td>
                  <td className="py-2.5">
                    <code className="text-[#fafafa] text-xs font-mono">{row.value}</code>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
