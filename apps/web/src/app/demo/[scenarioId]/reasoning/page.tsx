import Link from "next/link";

export default async function DemoReasoningStub({
  params,
}: {
  params: Promise<{ scenarioId: string }>;
}) {
  const { scenarioId } = await params;
  return (
    <main className="min-h-screen bg-background p-6">
      <section className="mx-auto flex min-h-[calc(100vh-3rem)] max-w-4xl flex-col justify-center rounded-lg border border-border bg-surface p-6">
        <p className="text-xs font-semibold uppercase tracking-wide text-accent">Prompt 02 handoff</p>
        <h1 className="mt-4 text-4xl font-semibold text-text-primary">
          Reasoning theatre coming online for {scenarioId}.
        </h1>
        <p className="mt-4 max-w-2xl text-sm leading-6 text-text-secondary">
          Prompt 1 now hands off here after graph materialization. Prompt 2 will replace this stub with the
          deterministic reasoning theatre.
        </p>
        <Link href="/demo" className="btn-primary mt-8 w-fit">
          Back to ingestion theatre
        </Link>
      </section>
    </main>
  );
}
