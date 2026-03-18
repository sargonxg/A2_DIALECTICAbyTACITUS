"use client";

import PipelineMonitor from "@/components/admin/PipelineMonitor";

export default function ExtractionPage() {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-text-primary">Extraction Pipeline</h2>
      <PipelineMonitor jobs={[]} />
    </div>
  );
}
