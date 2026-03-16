"use client";

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

interface UsagePoint {
  date: string;
  api_calls: number;
  extractions: number;
  analyses: number;
}

interface Props {
  data: UsagePoint[];
}

export default function UsageCharts({ data }: Props) {
  return (
    <div className="card">
      <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wider mb-4">API Usage (30 days)</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
          <XAxis dataKey="date" tick={{ fill: "#94a3b8", fontSize: 10 }} stroke="#334155" />
          <YAxis tick={{ fill: "#94a3b8", fontSize: 10 }} stroke="#334155" />
          <Tooltip contentStyle={{ backgroundColor: "#0f172a", border: "1px solid #1e293b", borderRadius: "0.375rem", color: "#f1f5f9" }} />
          <Bar dataKey="api_calls" fill="#14b8a6" name="API Calls" radius={[2, 2, 0, 0]} />
          <Bar dataKey="extractions" fill="#f59e0b" name="Extractions" radius={[2, 2, 0, 0]} />
          <Bar dataKey="analyses" fill="#8b5cf6" name="Analyses" radius={[2, 2, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
