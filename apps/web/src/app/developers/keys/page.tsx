"use client";

import { useState } from "react";
import { Key, Plus, Trash2, Copy } from "lucide-react";

interface MockKey { id: string; name: string; prefix: string; created_at: string; last_used: string; active: boolean }

export default function KeysPage() {
  const [keys, setKeys] = useState<MockKey[]>([
    { id: "1", name: "Development", prefix: "dk_dev_", created_at: "2024-01-15", last_used: "2024-12-01", active: true },
  ]);
  const [newKeyName, setNewKeyName] = useState("");

  const handleCreate = () => {
    if (!newKeyName.trim()) return;
    setKeys((prev) => [...prev, { id: String(prev.length + 1), name: newKeyName, prefix: "dk_" + newKeyName.slice(0, 4).toLowerCase() + "_", created_at: new Date().toISOString().slice(0, 10), last_used: "Never", active: true }]);
    setNewKeyName("");
  };

  return (
    <div className="max-w-3xl space-y-6">
      <h1 className="text-2xl font-bold text-text-primary flex items-center gap-2"><Key size={24} /> API Keys</h1>

      <div className="flex gap-2">
        <input value={newKeyName} onChange={(e) => setNewKeyName(e.target.value)} placeholder="Key name..." className="input-base flex-1" />
        <button onClick={handleCreate} className="btn-primary flex items-center gap-1"><Plus size={14} /> Create Key</button>
      </div>

      <div className="card">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-text-secondary text-left">
              <th className="pb-2">Name</th><th className="pb-2">Prefix</th><th className="pb-2">Created</th><th className="pb-2">Last Used</th><th className="pb-2">Status</th><th className="pb-2"></th>
            </tr>
          </thead>
          <tbody>
            {keys.map((key) => (
              <tr key={key.id} className="border-t border-border">
                <td className="py-2 text-text-primary">{key.name}</td>
                <td className="py-2 font-mono text-text-secondary">{key.prefix}***</td>
                <td className="py-2 text-text-secondary">{key.created_at}</td>
                <td className="py-2 text-text-secondary">{key.last_used}</td>
                <td className="py-2"><span className={`badge ${key.active ? "bg-success/10 text-success" : "bg-danger/10 text-danger"}`}>{key.active ? "Active" : "Revoked"}</span></td>
                <td className="py-2"><button className="btn-ghost p-1 text-danger"><Trash2 size={14} /></button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
