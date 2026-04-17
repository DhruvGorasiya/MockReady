"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth/AuthContext";
import { getSessionDetail } from "@/lib/api/sessions";
import CoachScoreForm from "@/components/coach/CoachScoreForm";
import type { QuestionResult, SessionDetail } from "@/lib/types/session";

interface Props {
  params: { sessionId: string };
}

type State =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "ok"; detail: SessionDetail };

export default function CoachSessionReviewPage({ params }: Props) {
  const { token } = useAuth();
  const { sessionId } = params;
  const [state, setState] = useState<State>({ status: "loading" });
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (!token) return;
    getSessionDetail(sessionId, token)
      .then((detail) => setState({ status: "ok", detail }))
      .catch((err: unknown) =>
        setState({
          status: "error",
          message: err instanceof Error ? err.message : "Failed to load",
        }),
      );
  }, [sessionId, token]);

  function handleScoreSubmitted(updated: QuestionResult) {
    if (state.status !== "ok") return;
    const updatedQuestions = state.detail.questions.map((q) =>
      q.id === updated.id ? updated : q,
    );
    setState({
      ...state,
      detail: { ...state.detail, questions: updatedQuestions },
    });
  }

  if (state.status === "loading") {
    return <p className="text-sm text-gray-500">Loading session…</p>;
  }

  if (state.status === "error") {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-center">
        <p className="font-medium text-red-700">Something went wrong</p>
        <p className="mt-1 text-sm text-red-500">{state.message}</p>
      </div>
    );
  }

  const sorted = [...state.detail.questions].sort(
    (a, b) => a.order_index - b.order_index,
  );
  const total = sorted.length;
  const question = sorted[currentIndex];

  if (!question) return <p className="text-gray-500">No questions found.</p>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500 capitalize">
            {state.detail.interview_type.replace("_", " ")} ·{" "}
            {state.detail.role}
          </p>
          <h1 className="mt-1 text-xl font-bold text-gray-900">Coach Review</h1>
        </div>
        <span className="text-sm text-gray-400">
          Question {currentIndex + 1} of {total}
        </span>
      </div>

      {/* Question */}
      <div className="rounded-lg border border-gray-200 bg-white p-5">
        <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 mb-2">
          Question
        </p>
        <p className="text-gray-900">{question.question_text}</p>
      </div>

      {/* Candidate answer */}
      {question.candidate_answer && (
        <div className="rounded-lg border border-gray-200 bg-white p-5">
          <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 mb-2">
            Candidate Answer
          </p>
          <p className="text-sm text-gray-700 whitespace-pre-wrap">
            {question.candidate_answer}
          </p>
        </div>
      )}

      {/* AI scores reference */}
      {question.ai_scores && (
        <div className="rounded-lg border border-gray-200 bg-white p-5">
          <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 mb-3">
            AI Scores
          </p>
          <div className="grid grid-cols-5 gap-2">
            {(
              [
                "clarity",
                "depth",
                "structure",
                "relevance",
                "communication_quality",
              ] as const
            ).map((dim) => (
              <div key={dim} className="text-center">
                <p className="text-xs text-gray-500 capitalize mb-1">
                  {dim.replace("_", " ")}
                </p>
                <p className="text-lg font-bold text-indigo-600">
                  {question.ai_scores![dim]}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Coach score form */}
      <div className="rounded-lg border border-gray-200 bg-white p-5">
        <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 mb-4">
          Override Scores
        </p>
        <CoachScoreForm
          sessionId={sessionId}
          question={question}
          onScoreSubmitted={handleScoreSubmitted}
        />
      </div>

      {/* Navigation */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => setCurrentIndex((i) => Math.max(0, i - 1))}
          disabled={currentIndex === 0}
          className="rounded-md border border-gray-300 px-4 py-2 text-sm text-gray-700 disabled:opacity-40"
        >
          Previous
        </button>
        <a href="/review" className="text-sm text-indigo-600 hover:underline">
          Back to review queue
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
