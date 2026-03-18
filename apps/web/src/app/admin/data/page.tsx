"use client";

import DataImportExport from "@/components/admin/DataImportExport";

export default function DataPage() {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-text-primary">Data Management</h2>
      <DataImportExport />
    </div>
  );
}
