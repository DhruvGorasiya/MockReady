"use client";

import { useEffect, useState } from "react";
import { getSessionDetail } from "@/lib/api/sessions";
import type { QuestionResult, SessionDetail } from "@/lib/types/session";
import DimensionBreakdown from "@/components/session/DimensionBreakdown";

interface Props {
  sessionId: string;
}

type State =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "ok"; detail: SessionDetail };

export default function SessionDetailClient({ sessionId }: Props) {
  const [state, setState] = useState<State>({ status: "loading" });
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const token = process.env.NEXT_PUBLIC_API_TOKEN ?? "";
    getSessionDetail(sessionId, token)
      .then((detail) => setState({ status: "ok", detail }))
      .catch((err: unknown) => {
        setState({
          status: "error",
          message: err instanceof Error ? err.message : "Unknown error",
        });
      });
  }, [sessionId]);

  if (state.status === "loading") {
    return (
      <div className="flex min-h-[200px] items-center justify-center">
        <p className="text-sm text-gray-500">Loading session…</p>
      </div>
    );
  }

  if (state.status === "error") {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-center">
        <p className="font-medium text-red-700">Something went wrong</p>
        <p className="mt-1 text-sm text-red-500">{state.message}</p>
      </div>
    );
  }

  const { detail } = state;
  const sorted = [...detail.questions].sort((a, b) => a.order_index - b.order_index);
  const total = sorted.length;
  const question: QuestionResult | undefined = sorted[currentIndex];

  if (!question) {
    return <p className="text-gray-500">No questions found for this session.</p>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <span className="text-sm font-medium capitalize text-gray-500">
            {detail.interview_type.replace("_", " ")} · {detail.role}
          </span>
          <h1 className="mt-1 text-xl font-bold text-gray-900">Session Review</h1>
        </div>
        <span className="text-sm text-gray-400">
          Question {currentIndex + 1} of {total}
        </span>
      </div>

      {/* Question */}
      <div className="rounded-lg border border-gray-200 bg-white p-5">
        <p className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">
          Question
        </p>
        <p className="text-gray-900">{question.question_text}</p>
      </div>

      {/* Answer */}
      {question.candidate_answer && (
        <div className="rounded-lg border border-gray-200 bg-white p-5">
          <p className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">
            Your Answer
          </p>
          <p className="text-gray-700 whitespace-pre-wrap">{question.candidate_answer}</p>
        </div>
      )}

      {/* Scores */}
      {question.ai_scores && (
        <DimensionBreakdown
          aiScores={question.ai_scores}
          coachScores={question.coach_scores}
        />
      )}

      {/* Navigation */}
      <div className="flex items-center justify-between pt-2">
        <button
          onClick={() => setCurrentIndex((i) => Math.max(0, i - 1))}
          disabled={currentIndex === 0}
          className="rounded-md border border-gray-300 px-4 py-2 text-sm text-gray-700 disabled:opacity-40"
        >
          Previous
        </button>
        <a
          href="/dashboard"
          className="text-sm text-indigo-600 hover:underline"
        >
          Back to dashboard
        </a>
        <button
          onClick={() => setCurrentIndex((i) => Math.min(total - 1, i + 1))}
          disabled={currentIndex === total - 1}
          className="rounded-md bg-indigo-600 px-4 py-2 text-sm text-white disabled:opacity-40"
        >
          Next
        </button>
      </div>
    </div>
  );
}
