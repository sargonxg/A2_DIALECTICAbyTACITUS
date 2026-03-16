"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import type { ConflictDomain, ConflictScale, OntologyTier } from "@/types/ontology";
import OntologyTierSelector from "@/components/workspace/OntologyTierSelector";
import { cn } from "@/lib/utils";

const DOMAINS: ConflictDomain[] = ["interpersonal", "workplace", "commercial", "legal", "political", "armed"];
const SCALES: ConflictScale[] = ["micro", "meso", "macro", "meta"];

export default function NewWorkspacePage() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [domain, setDomain] = useState<ConflictDomain>("workplace");
  const [scale, setScale] = useState<ConflictScale>("meso");
  const [tier, setTier] = useState<OntologyTier>("standard");
  const [loading, setLoading] = useState(false);

  const handleCreate = async () => {
    setLoading(true);
    try {
      const ws = await api.createWorkspace({ name, description, domain, scale, tier });
      router.push(`/workspaces/${ws.id}`);
    } catch {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <h1 className="text-2xl font-bold text-text-primary">Create Workspace</h1>

      {/* Steps indicator */}
      <div className="flex gap-2">
        {["Details", "Domain & Scale", "Tier", "Review"].map((s, i) => (
          <div key={s} className={cn("flex-1 text-center text-xs py-1 rounded", i === step ? "bg-accent text-white" : i < step ? "bg-accent/20 text-accent" : "bg-surface-hover text-text-secondary")}>
            {s}
          </div>
        ))}
      </div>

      {step === 0 && (
        <div className="space-y-4">
          <div>
            <label className="text-sm text-text-secondary block mb-1">Name</label>
            <input value={name} onChange={(e) => setName(e.target.value)} className="input-base w-full" placeholder="e.g., Syria Civil War Analysis" />
          </div>
          <div>
            <label className="text-sm text-text-secondary block mb-1">Description</label>
            <textarea value={description} onChange={(e) => setDescription(e.target.value)} className="input-base w-full" rows={3} placeholder="Brief description..." />
          </div>
          <button onClick={() => setStep(1)} disabled={!name.trim()} className="btn-primary">Next</button>
        </div>
      )}

      {step === 1 && (
        <div className="space-y-6">
          <div>
            <label className="text-sm text-text-secondary block mb-2">Conflict Domain</label>
            <div className="grid grid-cols-3 gap-2">
              {DOMAINS.map((d) => (
                <button key={d} onClick={() => setDomain(d)} className={cn("card text-sm capitalize", domain === d ? "border-accent bg-accent/5" : "hover:border-border-hover")}>
                  {d}
                </button>
              ))}
            </div>
          </div>
          <div>
            <label className="text-sm text-text-secondary block mb-2">Conflict Scale</label>
            <div className="grid grid-cols-4 gap-2">
              {SCALES.map((s) => (
                <button key={s} onClick={() => setScale(s)} className={cn("card text-sm capitalize", scale === s ? "border-accent bg-accent/5" : "hover:border-border-hover")}>
                  {s}
                </button>
              ))}
            </div>
          </div>
          <div className="flex gap-2">
            <button onClick={() => setStep(0)} className="btn-secondary">Back</button>
            <button onClick={() => setStep(2)} className="btn-primary">Next</button>
          </div>
        </div>
      )}

      {step === 2 && (
        <div className="space-y-4">
          <OntologyTierSelector value={tier} onChange={setTier} />
          <div className="flex gap-2">
            <button onClick={() => setStep(1)} className="btn-secondary">Back</button>
            <button onClick={() => setStep(3)} className="btn-primary">Next</button>
          </div>
        </div>
      )}

      {step === 3 && (
        <div className="space-y-4">
          <div className="card space-y-2">
            <h3 className="font-semibold text-text-primary">Review</h3>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <span className="text-text-secondary">Name</span><span className="text-text-primary">{name}</span>
              <span className="text-text-secondary">Domain</span><span className="text-text-primary capitalize">{domain}</span>
              <span className="text-text-secondary">Scale</span><span className="text-text-primary capitalize">{scale}</span>
              <span className="text-text-secondary">Tier</span><span className="text-text-primary capitalize">{tier}</span>
            </div>
          </div>
          <div className="flex gap-2">
            <button onClick={() => setStep(2)} className="btn-secondary">Back</button>
            <button onClick={handleCreate} disabled={loading} className="btn-primary">
              {loading ? "Creating..." : "Create Workspace"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
