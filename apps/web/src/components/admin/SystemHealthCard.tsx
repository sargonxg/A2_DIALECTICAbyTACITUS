"use client";

import { Activity, Database, Cpu, Globe } from "lucide-react";
import { cn } from "@/lib/utils";

interface ServiceStatus {
  name: string;
  status: "healthy" | "degraded" | "down";
  latency_ms?: number;
}

interface Props {
  services: ServiceStatus[];
}

export default function SystemHealthCard({ services }: Props) {
  return (
    <div className="card">
      <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wider mb-3">
        <Activity size={14} className="inline mr-1" /> System Health
      </h3>
      <div className="space-y-2">
        {services.map((svc) => (
          <div key={svc.name} className="flex items-center gap-3">
            <div className={cn(
              "w-2.5 h-2.5 rounded-full",
              svc.status === "healthy" ? "bg-success" : svc.status === "degraded" ? "bg-warning" : "bg-danger",
            )} />
            <span className="text-sm text-text-primary flex-1">{svc.name}</span>
            {svc.latency_ms !== undefined && (
              <span className="font-mono text-xs text-text-secondary">{svc.latency_ms}ms</span>
            )}
            <span className={cn(
              "badge text-[10px]",
              svc.status === "healthy" ? "bg-success/10 text-success" : svc.status === "degraded" ? "bg-warning/10 text-warning" : "bg-danger/10 text-danger",
            )}>
              {svc.status}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
