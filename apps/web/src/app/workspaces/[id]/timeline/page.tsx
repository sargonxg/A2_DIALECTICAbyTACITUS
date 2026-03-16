"use client";

import { useParams } from "next/navigation";
import EscalationChart from "@/components/timeline/EscalationChart";

const SAMPLE_DATA = [
  { date: "2024-01", glasl_stage: 2, sentiment: 0.3 },
  { date: "2024-03", glasl_stage: 3, sentiment: -0.1 },
  { date: "2024-05", glasl_stage: 4, sentiment: -0.4 },
  { date: "2024-07", glasl_stage: 5, sentiment: -0.6 },
  { date: "2024-09", glasl_stage: 4, sentiment: -0.3 },
];

export default function TimelinePage() {
  const { id } = useParams();

  return (
    <div className="space-y-6">
      <h2 className="text-lg font-semibold text-text-primary">Timeline</h2>
      <EscalationChart data={SAMPLE_DATA} />
      <div className="card text-center py-12">
        <p className="text-text-secondary">Event timeline visualization will populate as events are extracted.</p>
      </div>
    </div>
  );
}
