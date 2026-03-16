"use client";

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from "recharts";
import { GLASL_COLORS } from "@/lib/utils";

interface DataPoint {
  date: string;
  glasl_stage: number;
  sentiment?: number;
}

interface Props {
  data: DataPoint[];
}

export default function EscalationChart({ data }: Props) {
  return (
    <div className="card">
      <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wider mb-4">Escalation Over Time</h3>
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={data} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
          <XAxis dataKey="date" tick={{ fill: "#94a3b8", fontSize: 10 }} stroke="#334155" />
          <YAxis domain={[0, 9]} ticks={[1, 2, 3, 4, 5, 6, 7, 8, 9]} tick={{ fill: "#94a3b8", fontSize: 10 }} stroke="#334155" />
          <Tooltip contentStyle={{ backgroundColor: "#0f172a", border: "1px solid #1e293b", borderRadius: "0.375rem", color: "#f1f5f9" }} />
          <ReferenceLine y={3.5} stroke={GLASL_COLORS["win-win"]} strokeDasharray="3 3" label={{ value: "Win-Win", fill: GLASL_COLORS["win-win"], fontSize: 10 }} />
          <ReferenceLine y={6.5} stroke={GLASL_COLORS["win-lose"]} strokeDasharray="3 3" label={{ value: "Win-Lose", fill: GLASL_COLORS["win-lose"], fontSize: 10 }} />
          <Line type="monotone" dataKey="glasl_stage" stroke="#f43f5e" strokeWidth={2} dot={{ fill: "#f43f5e", r: 3 }} name="Glasl Stage" />
          {data.some((d) => d.sentiment !== undefined) && (
            <Line type="monotone" dataKey="sentiment" stroke="#8b5cf6" strokeWidth={1} strokeDasharray="3 3" dot={false} name="Sentiment" />
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
