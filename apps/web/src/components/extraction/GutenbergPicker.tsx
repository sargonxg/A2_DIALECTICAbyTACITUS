"use client";

import { useEffect, useMemo, useState } from "react";
import { BookOpen, Search } from "lucide-react";
import { api } from "@/lib/api";
import OntologyTierSelector from "@/components/workspace/OntologyTierSelector";
import type { OntologyTier } from "@/types/ontology";

export interface GutenbergBook {
  book_id: string;
  title: string;
  author: string;
  domain: string;
  subdomain: string;
  summary: string;
  estimated_words: number;
  recommended_tier: string;
}

interface Props {
  onIngest: (params: {
    book_id: string;
    title: string;
    tier: OntologyTier;
    max_chars: number;
  }) => void;
}

const DEFAULT_MAX_CHARS = 60_000;

const DOMAIN_LABEL: Record<string, string> = {
  human_friction: "Human Friction",
  conflict_warfare: "Conflict & Warfare",
};

export default function GutenbergPicker({ onIngest }: Props) {
  const [books, setBooks] = useState<GutenbergBook[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [tier, setTier] = useState<OntologyTier>("standard");
  const [maxChars, setMaxChars] = useState(DEFAULT_MAX_CHARS);
  const [customId, setCustomId] = useState("");
  const [filter, setFilter] = useState<"all" | "human_friction" | "conflict_warfare">("all");

  useEffect(() => {
    let cancelled = false;
    api
      .listGutenbergCatalog()
      .then((res) => {
        if (!cancelled) setBooks(res.books);
      })
      .catch((e: unknown) => {
        if (!cancelled) setError(e instanceof Error ? e.message : "Catalog unavailable");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const visibleBooks = useMemo(
    () => (filter === "all" ? books : books.filter((b) => b.domain === filter)),
    [books, filter],
  );

  const selected = useMemo(
    () => books.find((b) => b.book_id === selectedId) ?? null,
    [books, selectedId],
  );

  const submit = () => {
    if (selected) {
      onIngest({
        book_id: selected.book_id,
        title: selected.title,
        tier,
        max_chars: maxChars,
      });
      return;
    }
    if (customId.trim()) {
      onIngest({
        book_id: customId.trim(),
        title: `Gutenberg #${customId.trim()}`,
        tier,
        max_chars: maxChars,
      });
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-text-primary flex items-center gap-2">
            <BookOpen size={16} /> Project Gutenberg
          </h3>
          <p className="text-xs text-text-secondary">
            One-click ingest of public-domain conflict primary sources.
          </p>
        </div>
        <div className="flex gap-1 text-xs">
          {(["all", "human_friction", "conflict_warfare"] as const).map((d) => (
            <button
              key={d}
              onClick={() => setFilter(d)}
              className={`px-2 py-1 rounded ${
                filter === d
                  ? "bg-accent text-white"
                  : "bg-surface text-text-secondary hover:text-text-primary"
              }`}
            >
              {d === "all" ? "All" : DOMAIN_LABEL[d]}
            </button>
          ))}
        </div>
      </div>

      {loading && <div className="text-xs text-text-secondary">Loading catalog…</div>}
      {error && (
        <div className="text-xs text-red-400">Could not load Gutenberg catalog: {error}</div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {visibleBooks.map((book) => (
          <button
            key={book.book_id}
            onClick={() => {
              setSelectedId(book.book_id);
              setTier((book.recommended_tier as OntologyTier) ?? "standard");
              setCustomId("");
            }}
            className={`text-left card p-3 border transition-colors ${
              selectedId === book.book_id
                ? "border-accent bg-accent/5"
                : "border-border hover:border-accent/40"
            }`}
          >
            <div className="flex items-baseline justify-between gap-2">
              <span className="text-sm font-semibold text-text-primary">{book.title}</span>
              <span className="text-[10px] uppercase tracking-wide text-text-secondary">
                #{book.book_id}
              </span>
            </div>
            <div className="text-xs text-text-secondary">{book.author}</div>
            <div className="mt-1 text-xs text-text-secondary leading-snug line-clamp-3">
              {book.summary}
            </div>
            <div className="mt-2 flex flex-wrap gap-2 text-[10px] text-text-secondary">
              <span className="px-1.5 py-0.5 rounded bg-surface">
                {DOMAIN_LABEL[book.domain] ?? book.domain}
              </span>
              <span className="px-1.5 py-0.5 rounded bg-surface">{book.subdomain}</span>
              <span className="px-1.5 py-0.5 rounded bg-surface">
                ~{Math.round(book.estimated_words / 1000)}k words
              </span>
            </div>
          </button>
        ))}
      </div>

      <div className="card p-3 space-y-2">
        <label className="text-xs text-text-secondary flex items-center gap-2">
          <Search size={12} /> Or fetch any Gutenberg book by ID
        </label>
        <input
          value={customId}
          onChange={(e) => {
            setCustomId(e.target.value);
            if (e.target.value) setSelectedId(null);
          }}
          placeholder="e.g. 1342 (Pride and Prejudice)"
          className="input-base w-full text-sm"
        />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div>
          <label className="text-xs text-text-secondary block mb-1">Extraction Tier</label>
          <OntologyTierSelector value={tier} onChange={setTier} />
        </div>
        <div>
          <label className="text-xs text-text-secondary block mb-1">
            Max characters (truncate for speed)
          </label>
          <select
            value={maxChars}
            onChange={(e) => setMaxChars(parseInt(e.target.value, 10))}
            className="input-base w-full text-sm"
          >
            <option value={20_000}>20k chars (quick demo)</option>
            <option value={60_000}>60k chars (balanced)</option>
            <option value={150_000}>150k chars (deeper)</option>
            <option value={500_000}>500k chars (full, slow)</option>
          </select>
        </div>
      </div>

      <button
        onClick={submit}
        disabled={!selected && !customId.trim()}
        className="btn-primary w-full"
      >
        {selected
          ? `Ingest "${selected.title}"`
          : customId.trim()
            ? `Ingest Gutenberg #${customId.trim()}`
            : "Select a book"}
      </button>
    </div>
  );
}
