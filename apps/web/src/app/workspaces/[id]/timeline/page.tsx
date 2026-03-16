'use client';

import { useParams } from 'next/navigation';
import { Clock } from 'lucide-react';
import { useWorkspace } from '@/hooks/useWorkspace';
import { EventTimeline } from '@/components/timeline/EventTimeline';
import { EscalationChart } from '@/components/timeline/EscalationChart';

export default function TimelinePage() {
  const params = useParams();
  const id = params.id as string;

  const { workspace } = useWorkspace(id);

  return (
    <div className="flex flex-col h-full min-h-0 bg-[#09090b]">
      {/* Page header */}
      <div className="px-6 py-4 border-b border-[#27272a] flex items-center gap-2 shrink-0">
        <Clock className="w-4 h-4 text-zinc-500" />
        <h2 className="text-sm font-semibold text-zinc-200">
          {workspace ? `${workspace.name} — Timeline` : 'Timeline'}
        </h2>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {/* Event timeline — full width */}
        <div className="rounded-xl border border-[#27272a] bg-[#18181b] overflow-hidden">
          <div className="px-5 py-3 border-b border-[#27272a]">
            <p className="text-xs font-semibold uppercase tracking-widest text-zinc-500">
              Event Timeline
            </p>
          </div>
          <EventTimeline workspaceId={id} />
        </div>

        {/* Escalation chart — below event timeline */}
        <div className="rounded-xl border border-[#27272a] bg-[#18181b] overflow-hidden">
          <div className="px-5 py-3 border-b border-[#27272a]">
            <p className="text-xs font-semibold uppercase tracking-widest text-zinc-500">
              Escalation Trajectory
            </p>
          </div>
          <EscalationChart workspaceId={id} />
        </div>
      </div>
    </div>
  );
}
