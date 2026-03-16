"use client";

import { useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Cell,
} from "recharts";
import { BarChart3, RefreshCw } from "lucide-react";

const ENDPOINT_DATA = [
  { endpoint: "/v1/workspaces", requests: 842 },
  { endpoint: "/v1/.../analyze", requests: 631 },
  { endpoint: "/v1/.../escalation", requests: 410 },
  { endpoint: "/v1/.../ripeness", requests: 298 },
  { endpoint: "/v1/.../power", requests: 254 },
  { endpoint: "/v1/.../trust", requests: 201 },
  { endpoint: "/v1/.../network", requests: 178 },
  { endpoint: "/v1/.../quality", requests: 143 },
  { endpoint: "/v1/theory", requests: 97 },
  { endpoint: "/health", requests: 62 },
];

const TENANT_DATA = [
  { tenant: "JCPOA", requests: 1204, nodes: 87, edges: 142 },
  { tenant: "HR Mediation", requests: 876, nodes: 54, edges: 89 },
  { tenant: "Commercial", requests: 632, nodes: 41, edges: 67 },
  { tenant: "default", requests: 400, nodes: 12, edges: 18 },
];

const TEAL = "#0d9488";
const TEAL_DIM = "#0d948866";

interface TooltipProps {
  active?: boolean;
  payload?: { value: number; name: string }[];
  label?: string;
}

function CustomTooltip({ active, payload, label }: TooltipProps) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-[#18181b] border border-[#27272a] rounded-md px-3 py-2 text-xs shadow-lg">
      <p className="text-[#a1a1aa] mb-1">{label}</p>
      {payload.map((p) => (
        <p key={p.name} className="text-[#fafafa] font-mono">
          {p.value.toLocaleString()} {p.name}
        </p>
      ))}
    </div>
  );
}

export function UsageCharts() {
  const [activeBar, setActiveBar] = useState<number | null>(null);

  return (
    <div className="space-y-6">
      {/* Requests per endpoint */}
      <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-5">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <BarChart3 size={16} className="text-[#71717a]" />
            <h3 className="text-[#fafafa] text-sm font-semibold">Requests by Endpoint</h3>
          </div>
          <span className="text-[#52525b] text-xs">Last 30 days (mock)</span>
        </div>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart
            data={ENDPOINT_DATA}
            layout="vertical"
            margin={{ top: 0, right: 16, bottom: 0, left: 8 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#27272a" horizontal={false} />
            <XAxis
              type="number"
              tick={{ fill: "#71717a", fontSize: 11 }}
              axisLine={{ stroke: "#27272a" }}
              tickLine={false}
            />
            <YAxis
              type="category"
              dataKey="endpoint"
              tick={{ fill: "#a1a1aa", fontSize: 10, fontFamily: "var(--font-jetbrains-mono)" }}
              axisLine={false}
              tickLine={false}
              width={130}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: "#27272a44" }} />
            <Bar
              dataKey="requests"
              radius={[0, 3, 3, 0]}
              onMouseEnter={(_, idx) => setActiveBar(idx)}
              onMouseLeave={() => setActiveBar(null)}
            >
              {ENDPOINT_DATA.map((_, idx) => (
                <Cell
                  key={idx}
                  fill={activeBar === idx ? TEAL : TEAL_DIM}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Tenant breakdown */}
      <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-5">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-[#fafafa] text-sm font-semibold">Tenant Usage Breakdown</h3>
          <button
            className="p-1.5 rounded-md text-[#71717a] hover:text-[#fafafa] hover:bg-[#27272a] transition-colors"
            title="Refresh"
            aria-label="Refresh usage data"
          >
            <RefreshCw size={14} />
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[#27272a]">
                <th className="text-left text-[#71717a] text-xs font-medium pb-2 pr-4">Workspace</th>
                <th className="text-right text-[#71717a] text-xs font-medium pb-2 pr-4">Requests</th>
                <th className="text-right text-[#71717a] text-xs font-medium pb-2 pr-4">Nodes</th>
                <th className="text-right text-[#71717a] text-xs font-medium pb-2">Edges</th>
              </tr>
            </thead>
            <tbody>
              {TENANT_DATA.map((row, i) => (
                <tr
                  key={row.tenant}
                  className={`border-b border-[#27272a]/50 ${i % 2 === 0 ? "" : "bg-[#09090b]/30"}`}
                >
                  <td className="py-2 pr-4 text-[#fafafa] font-medium">{row.tenant}</td>
                  <td className="py-2 pr-4 text-right text-[#a1a1aa] font-mono">
                    {row.requests.toLocaleString()}
                  </td>
                  <td className="py-2 pr-4 text-right text-[#a1a1aa] font-mono">{row.nodes}</td>
                  <td className="py-2 text-right text-[#a1a1aa] font-mono">{row.edges}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <ResponsiveContainer width="100%" height={140} className="mt-4">
          <BarChart data={TENANT_DATA} margin={{ top: 0, right: 0, bottom: 0, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />
            <XAxis
              dataKey="tenant"
              tick={{ fill: "#a1a1aa", fontSize: 11 }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              tick={{ fill: "#71717a", fontSize: 11 }}
              axisLine={false}
              tickLine={false}
              width={40}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: "#27272a44" }} />
            <Bar dataKey="requests" fill={TEAL} radius={[3, 3, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
