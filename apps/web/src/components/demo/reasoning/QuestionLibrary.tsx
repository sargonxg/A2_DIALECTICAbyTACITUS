import type { CuratedReasoningQuestion } from "./types";
import { QuestionCard } from "./QuestionCard";

interface Props {
  questions: CuratedReasoningQuestion[];
  activeId: string;
  onSelect: (id: string) => void;
}

export function QuestionLibrary({ questions, activeId, onSelect }: Props) {
  return (
    <aside className="flex min-h-0 flex-col border-r border-border bg-background/80 lg:w-[360px]">
      <div className="border-b border-border p-4">
        <p className="text-xs font-semibold uppercase tracking-wide text-accent">Move A</p>
        <h2 className="mt-1 text-xl font-semibold text-text-primary">Question Library</h2>
        <p className="mt-2 text-sm leading-6 text-text-secondary">
          Each card is anchored to a theory framework and routed through symbolic rules before synthesis.
        </p>
      </div>
      <div className="flex gap-2 overflow-x-auto p-3 lg:block lg:space-y-2 lg:overflow-y-auto">
        {questions.map((question) => (
          <div key={question.id} className="w-[280px] shrink-0 lg:w-auto">
            <QuestionCard
              question={question}
              active={question.id === activeId}
              onSelect={() => onSelect(question.id)}
            />
          </div>
        ))}
      </div>
    </aside>
  );
}
