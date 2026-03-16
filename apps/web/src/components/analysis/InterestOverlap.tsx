"use client";

interface InterestItem {
  actor: string;
  interest: string;
  salience: number;
}

interface Props {
  interests: InterestItem[];
  actors: string[];
}

export default function InterestOverlap({ interests, actors }: Props) {
  const byInterest = interests.reduce<Record<string, InterestItem[]>>((acc, i) => {
    (acc[i.interest] = acc[i.interest] || []).push(i);
    return acc;
  }, {});

  const shared = Object.entries(byInterest).filter(([, items]) => items.length > 1);
  const unique = Object.entries(byInterest).filter(([, items]) => items.length === 1);

  return (
    <div className="card">
      <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wider mb-3">Interest Overlap</h3>
      {shared.length > 0 && (
        <div className="mb-3">
          <p className="text-xs text-success font-semibold mb-1">Shared Interests</p>
          {shared.map(([interest, items]) => (
            <div key={interest} className="flex items-center gap-2 text-sm mb-1">
              <span className="text-text-primary">{interest}</span>
              <span className="text-xs text-text-secondary">({items.map((i) => i.actor).join(", ")})</span>
            </div>
          ))}
        </div>
      )}
      {unique.length > 0 && (
        <div>
          <p className="text-xs text-warning font-semibold mb-1">Unique Interests</p>
          {unique.map(([interest, items]) => (
            <div key={interest} className="flex items-center gap-2 text-sm mb-1">
              <span className="text-text-primary">{interest}</span>
              <span className="text-xs text-text-secondary">({items[0].actor})</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
