import type { Metadata } from "next";
import GraphOpsConsole from "@/components/graphops/GraphOpsConsole";

export const metadata: Metadata = {
  title: "Graph Operations",
  description: "Password-protected TACITUS graph operations console for DIALECTICA.",
};

export default function GraphOpsPage() {
  return <GraphOpsConsole />;
}
