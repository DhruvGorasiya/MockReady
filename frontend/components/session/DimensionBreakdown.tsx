import type { DimensionScores } from "@/lib/types/session";

interface Props {
  aiScores: DimensionScores;
  coachScores: DimensionScores | null;
}

const DIMENSIONS: { key: keyof DimensionScores; label: string }[] = [
  { key: "clarity", label: "Clarity" },
  { key: "depth", label: "Depth" },
  { key: "structure", label: "Structure" },
  { key: "relevance", label: "Relevance" },
  { key: "communication_quality", label: "Communication" },
];

function ScoreBar({ value }: { value: number }) {
  const pct = (value / 10) * 100;
  const color =
    value >= 8 ? "bg-green-500" : value >= 5 ? "bg-indigo-400" : "bg-red-400";
  return (
    <div className="flex items-center gap-2">
      <div className="h-2 w-32 overflow-hidden rounded-full bg-gray-200">
        <div
          className={`h-full rounded-full ${color}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="w-4 text-right text-sm font-semibold text-gray-800">
        {value}
      </span>
    </div>
  );
}

export default function DimensionBreakdown({ aiScores, coachScores }: Props) {
  const hasCoach = coachScores !== null;

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-5">
      {hasCoach && (
        <div className="mb-3 flex items-center gap-2">
          <span className="rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-medium text-blue-800">
            Coach override — scores below are authoritative
          </span>
        </div>
      )}
      <div className="space-y-3">
        {DIMENSIONS.map(({ key, label }) => {
          const authoritative = hasCoach ? coachScores![key] : aiScores[key];
          return (
            <div key={key} className="flex items-center justify-between">
              <span className="w-36 text-sm text-gray-600">{label}</span>
              <div className="flex items-center gap-4">
                {hasCoach && (
                  <span className="text-xs text-gray-400 line-through">
                    {aiScores[key]}
                  </span>
                )}
                <ScoreBar value={authoritative} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
