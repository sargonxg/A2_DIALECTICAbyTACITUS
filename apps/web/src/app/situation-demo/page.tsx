import type { Metadata } from "next";
import SyriaDemoConsole from "@/components/graphops/SyriaDemoConsole";

export const metadata: Metadata = {
  title: "Situation Graph Demo | DIALECTICA",
  description: "Live DIALECTICA situation graph reasoning demo for policy, conflict, and book analysis.",
};

export default function SituationDemoPage() {
  return <SyriaDemoConsole />;
}
