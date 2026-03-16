"use client";

import { Shield } from "lucide-react";

export default function AdminApiKeysPage() {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-text-primary flex items-center gap-2"><Shield size={20} /> API Keys (Admin)</h2>
      <div className="card">
        <p className="text-sm text-text-secondary">Manage API keys across all tenants. Keys can be created, viewed, and revoked from this panel.</p>
      </div>
      <div className="card text-center py-8">
        <p className="text-text-secondary">No API keys found across tenants.</p>
      </div>
    </div>
  );
}
