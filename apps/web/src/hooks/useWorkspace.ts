"use client";

import { create } from "zustand";
import type { Workspace } from "@/types/api";

interface WorkspaceState {
  currentWorkspace: Workspace | null;
  workspaces: Workspace[];
  setCurrentWorkspace: (ws: Workspace | null) => void;
  setWorkspaces: (ws: Workspace[]) => void;
}

export const useWorkspaceStore = create<WorkspaceState>((set) => ({
  currentWorkspace: null,
  workspaces: [],
  setCurrentWorkspace: (ws) => set({ currentWorkspace: ws }),
  setWorkspaces: (ws) => set({ workspaces: ws }),
}));

export function useWorkspace() {
  return useWorkspaceStore();
}
