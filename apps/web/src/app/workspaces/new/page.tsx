"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ChevronLeft, Loader2, AlertCircle } from "lucide-react";
import { workspacesApi } from "@/lib/api";

const DOMAINS = [
  { value: "interpersonal", label: "Interpersonal" },
  { value: "workplace", label: "Workplace" },
  { value: "commercial", label: "Commercial" },
  { value: "legal", label: "Legal" },
  { value: "political", label: "Political" },
  { value: "armed", label: "Armed" },
] as const;

const SCALES = [
  { value: "micro", label: "Micro", description: "Individuals or small groups" },
  { value: "meso", label: "Meso", description: "Organisations or communities" },
  { value: "macro", label: "Macro", description: "Nations or large populations" },
  { value: "meta", label: "Meta", description: "Civilisational or systemic" },
] as const;

type Domain = (typeof DOMAINS)[number]["value"];
type Scale = (typeof SCALES)[number]["value"];

export default function NewWorkspacePage() {
  const router = useRouter();

  const [name, setName] = useState("");
  const [domain, setDomain] = useState<Domain>("political");
  const [scale, setScale] = useState<Scale>("macro");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!name.trim()) {
      setError("Workspace name is required.");
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      const workspace = await workspacesApi.create({
        name: name.trim(),
        domain,
        scale,
      });
      router.push(`/workspaces/${workspace.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create workspace. Please try again.");
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-full p-8 max-w-2xl">
      {/* Back link */}
      <Link
        href="/workspaces"
        className="inline-flex items-center gap-1.5 text-[#a1a1aa] hover:text-[#fafafa] text-sm mb-8 transition-colors"
      >
        <ChevronLeft size={15} />
        Back to Workspaces
      </Link>

      {/* Page header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-[#fafafa] mb-1">New Workspace</h1>
        <p className="text-[#a1a1aa] text-sm">
          Create a workspace to begin mapping a conflict as a knowledge graph.
        </p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} noValidate>
        <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-6 space-y-6">

          {/* Name */}
          <div>
            <label
              htmlFor="workspace-name"
              className="block text-[#fafafa] text-sm font-medium mb-1.5"
            >
              Workspace Name
              <span className="text-red-400 ml-1" aria-hidden="true">*</span>
            </label>
            <input
              id="workspace-name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. South China Sea Dispute 2024"
              required
              disabled={submitting}
              className="w-full bg-[#09090b] border border-[#27272a] rounded-md px-3 py-2 text-sm text-[#fafafa] placeholder-[#52525b] focus:outline-none focus:border-teal-600 transition-colors disabled:opacity-50"
            />
          </div>

          {/* Domain */}
          <div>
            <label
              htmlFor="workspace-domain"
              className="block text-[#fafafa] text-sm font-medium mb-1.5"
            >
              Conflict Domain
            </label>
            <select
              id="workspace-domain"
              value={domain}
              onChange={(e) => setDomain(e.target.value as Domain)}
              disabled={submitting}
              className="w-full bg-[#09090b] border border-[#27272a] rounded-md px-3 py-2 text-sm text-[#fafafa] focus:outline-none focus:border-teal-600 transition-colors disabled:opacity-50 appearance-none cursor-pointer"
            >
              {DOMAINS.map((d) => (
                <option key={d.value} value={d.value}>
                  {d.label}
                </option>
              ))}
            </select>
            <p className="text-[#52525b] text-xs mt-1.5">
              The primary arena in which this conflict occurs.
            </p>
          </div>

          {/* Scale */}
          <div>
            <span className="block text-[#fafafa] text-sm font-medium mb-2">
              Conflict Scale
            </span>
            <div className="grid grid-cols-2 gap-2">
              {SCALES.map((s) => (
                <label
                  key={s.value}
                  className={`
                    flex flex-col gap-0.5 p-3 rounded-md border cursor-pointer transition-colors
                    ${
                      scale === s.value
                        ? "border-teal-600 bg-teal-600/10"
                        : "border-[#27272a] hover:border-[#3f3f46] bg-[#09090b]"
                    }
                    ${submitting ? "opacity-50 cursor-not-allowed" : ""}
                  `}
                >
                  <input
                    type="radio"
                    name="scale"
                    value={s.value}
                    checked={scale === s.value}
                    onChange={() => setScale(s.value)}
                    disabled={submitting}
                    className="sr-only"
                  />
                  <span
                    className={`text-sm font-medium ${
                      scale === s.value ? "text-teal-400" : "text-[#fafafa]"
                    }`}
                  >
                    {s.label}
                  </span>
                  <span className="text-[#52525b] text-xs">{s.description}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Error message */}
          {error && (
            <div className="flex items-start gap-2.5 p-3 bg-red-500/10 border border-red-500/30 rounded-md">
              <AlertCircle size={16} className="text-red-400 flex-shrink-0 mt-0.5" />
              <p className="text-red-400 text-sm">{error}</p>
            </div>
          )}

          {/* Submit */}
          <div className="flex items-center gap-3 pt-2">
            <button
              type="submit"
              disabled={submitting || !name.trim()}
              className="inline-flex items-center gap-2 px-5 py-2 bg-teal-600 hover:bg-teal-700 text-white text-sm font-medium rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {submitting ? (
                <>
                  <Loader2 size={15} className="animate-spin" />
                  Creating…
                </>
              ) : (
                "Create Workspace"
              )}
            </button>
            <Link
              href="/workspaces"
              className="px-5 py-2 text-[#a1a1aa] hover:text-[#fafafa] text-sm font-medium transition-colors"
            >
              Cancel
            </Link>
          </div>
        </div>
      </form>
    </div>
  );
}
