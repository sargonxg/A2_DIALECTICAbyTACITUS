"use client";

import { Upload, Download, Database } from "lucide-react";

export default function DataImportExport() {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card-hover text-center space-y-2">
          <Upload size={24} className="mx-auto text-accent" />
          <h3 className="font-semibold text-text-primary">Import Data</h3>
          <p className="text-sm text-text-secondary">Upload JSON or CSV data files</p>
          <button className="btn-primary w-full">Import</button>
        </div>
        <div className="card-hover text-center space-y-2">
          <Download size={24} className="mx-auto text-accent" />
          <h3 className="font-semibold text-text-primary">Export Data</h3>
          <p className="text-sm text-text-secondary">Export workspace graphs as JSON</p>
          <button className="btn-secondary w-full">Export</button>
        </div>
        <div className="card-hover text-center space-y-2">
          <Database size={24} className="mx-auto text-accent" />
          <h3 className="font-semibold text-text-primary">Seed Data</h3>
          <p className="text-sm text-text-secondary">Load sample conflicts</p>
          <button className="btn-secondary w-full">Seed</button>
        </div>
      </div>
    </div>
  );
}
