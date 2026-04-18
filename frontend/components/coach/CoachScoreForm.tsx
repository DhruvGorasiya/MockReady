"use client";

import { useState } from "react";
import { submitCoachScore } from "@/lib/api/coach";
import { useAuth } from "@/lib/auth/AuthContext";
import type { QuestionResult } from "@/lib/types/session";

interface Props {
  sessionId: string;
  question: QuestionResult;
  onScoreSubmitted: (updated: QuestionResult) => void;
}

const DIMENSIONS: {
  key: keyof NonNullable<QuestionResult["ai_scores"]>;
  label: string;
}[] = [
  { key: "clarity", label: "Clarity" },
  { key: "depth", label: "Depth" },
  { key: "structure", label: "Structure" },
  { key: "relevance", label: "Relevance" },
  { key: "communication_quality", label: "Communication Quality" },
];

export default function CoachScoreForm({
  sessionId,
  question,
  onScoreSubmitted,
}: Props) {
  const { token } = useAuth();
  const ai = question.ai_scores;

  const [scores, setScores] = useState({
    clarity: ai?.clarity ?? 5,
    depth: ai?.depth ?? 5,
    structure: ai?.structure ?? 5,
    relevance: ai?.relevance ?? 5,
    communication_quality: ai?.communication_quality ?? 5,
  });
  const [justification, setJustification] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (question.coach_scores) {
    return (
      <div className="rounded-lg border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700">
        Coach score submitted
      </div>
    );
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!token) return;
    setError(null);
    setLoading(true);
    try {
      const updated = await submitCoachScore(
        sessionId,
        question.id.toString(),
        { scores, justification: justification || undefined },
        token,
      );
      onScoreSubmitted(updated);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Submission failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        {DIMENSIONS.map(({ key, label }) => (
          <div key={key}>
            <label
              htmlFor={key}
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              {label}
            </label>
            <input
              id={key}
              type="number"
              min={1}
              max={10}
              value={scores[key]}
              onChange={(e) =>
                setScores((prev) => ({
                  ...prev,
                  [key]: Number(e.target.value),
                }))
              }
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>
        ))}
      </div>

      <div>
        <label
          htmlFor="justification"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          Justification (optional)
        </label>
        <textarea
          id="justification"
          rows={3}
          value={justification}
          onChange={(e) => setJustification(e.target.value)}
          placeholder="Explain your score override..."
          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 resize-none"
        />
      </div>

      {error && (
        <p className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
          {error}
        </p>
      )}

      <button
        type="submit"
        disabled={loading}
        className="rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white disabled:opacity-40 hover:bg-indigo-700 transition-colors"
      >
        {loading ? "Submitting…" : "Submit score"}
      </button>
    </form>
  );
}
