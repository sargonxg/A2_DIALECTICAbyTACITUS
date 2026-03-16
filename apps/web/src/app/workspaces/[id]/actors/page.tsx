"use client";

import { useParams } from "next/navigation";
import { useEntities } from "@/hooks/useGraph";
import { Users } from "lucide-react";

export default function ActorsPage() {
  const { id } = useParams();
  const { data, isLoading } = useEntities(id as string, "actor");

  const actors = data?.items ?? [];

  return (
    <div className="space-y-6">
      <h2 className="text-lg font-semibold text-text-primary flex items-center gap-2">
        <Users size={20} /> Actors
      </h2>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[1, 2, 3, 4].map((i) => <div key={i} className="card h-24 animate-pulse bg-surface-hover" />)}
        </div>
      ) : actors.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-text-secondary">No actors extracted yet. Ingest documents to populate.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {actors.map((actor: Record<string, unknown>) => (
            <div key={actor.id as string} className="card-hover">
              <h3 className="font-semibold text-text-primary">{actor.name as string}</h3>
              <p className="text-sm text-text-secondary capitalize">{actor.actor_type as string}</p>
              {actor.description ? <p className="text-xs text-text-secondary mt-1">{String(actor.description)}</p> : null}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
