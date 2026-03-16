"use client";

import { Globe, Search } from "lucide-react";
import { useState } from "react";

export default function ExplorePage() {
  const [search, setSearch] = useState("");

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-text-primary flex items-center gap-2">
        <Globe size={24} /> Explore
      </h1>
      <p className="text-text-secondary">Browse public conflict graphs and sample workspaces.</p>

      <div className="relative max-w-sm">
        <Search size={14} className="absolute left-3 top-2.5 text-text-secondary" />
        <input type="text" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search public graphs..." className="input-base w-full pl-9" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {[
          { name: "JCPOA Nuclear Deal", domain: "political", nodes: 47 },
          { name: "HR Mediation Case", domain: "workplace", nodes: 23 },
          { name: "Commercial Arbitration", domain: "commercial", nodes: 31 },
        ].map((sample) => (
          <div key={sample.name} className="card-hover">
            <h3 className="font-semibold text-text-primary">{sample.name}</h3>
            <p className="text-xs text-text-secondary capitalize">{sample.domain} &middot; {sample.nodes} nodes</p>
            <button className="btn-secondary text-xs mt-2">Clone to My Workspace</button>
          </div>
        ))}
      </div>
    </div>
  );
}
