import { ReasoningConductor } from "@/components/demo/reasoning/ReasoningConductor";

export default async function DemoReasoningPage({
  params,
}: {
  params: Promise<{ scenarioId: string }>;
}) {
  const { scenarioId } = await params;
  return <ReasoningConductor scenarioId={scenarioId} />;
}
