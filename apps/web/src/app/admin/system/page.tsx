"use client";

import SystemHealthCard from "@/components/admin/SystemHealthCard";

export default function SystemPage() {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-text-primary">System Status</h2>
      <SystemHealthCard services={[
        { name: "API Server", status: "healthy", latency_ms: 12 },
        { name: "Spanner Database", status: "healthy", latency_ms: 8 },
        { name: "Gemini API", status: "healthy", latency_ms: 250 },
        { name: "Pub/Sub", status: "healthy", latency_ms: 15 },
      ]} />
    </div>
  );
}
