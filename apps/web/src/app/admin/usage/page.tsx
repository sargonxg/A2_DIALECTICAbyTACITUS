"use client";

import UsageCharts from "@/components/admin/UsageCharts";

const SAMPLE_DATA = Array.from({ length: 30 }, (_, i) => ({
  date: `Day ${i + 1}`,
  api_calls: Math.floor(Math.random() * 100),
  extractions: Math.floor(Math.random() * 10),
  analyses: Math.floor(Math.random() * 20),
}));

export default function UsagePage() {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-text-primary">Usage Analytics</h2>
      <UsageCharts data={SAMPLE_DATA} />
    </div>
  );
}
