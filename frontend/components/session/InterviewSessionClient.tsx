"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { getSessionDetail, submitAnswer } from "@/lib/api/sessions";
import type {
  AnswerFeedbackResponse,
  QuestionInSession,
  SessionCreatedResponse,
} from "@/lib/types/session";

interface Props {
  sessionId: string;
}

type Phase =
  | { stage: "loading" }
  | { stage: "error"; message: string }
  | { stage: "answering"; question: QuestionInSession; index: number; total: number }
  | { stage: "feedback"; feedback: AnswerFeedbackResponse; question: QuestionInSession; index: number; total: number }
  | { stage: "complete" };

const TIMER_SECONDS = 120;

export default function InterviewSessionClient({ sessionId }: Props) {
  const router = useRouter();
  const [phase, setPhase] = useState<Phase>({ stage: "loading" });
  const [questions, setQuestions] = useState<QuestionInSession[]>([]);
  const [answer, setAnswer] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [timeLeft, setTimeLeft] = useState(TIMER_SECONDS);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const token = process.env.NEXT_PUBLIC_API_TOKEN ?? "";

  useEffect(() => {
    getSessionDetail(sessionId, token)
      .then((detail) => {
        const sorted = [...detail.questions].sort((a, b) => a.order_index - b.order_index);
        setQuestions(sorted);
        if (sorted.length === 0) {
          setPhase({ stage: "error", message: "No questions found for this session." });
        } else {
          setPhase({ stage: "answering", question: sorted[0], index: 0, total: sorted.length });
          startTimer();
        }
      })
      .catch((err: unknown) => {
        setPhase({
          stage: "error",
          message: err instanceof Error ? err.message : "Failed to load session",
        });
      });

    return () => clearTimer();
  }, [sessionId]);

  function startTimer() {
    setTimeLeft(TIMER_SECONDS);
    clearTimer();
    timerRef.current = setInterval(() => {
      setTimeLeft((t) => {
        if (t <= 1) {
          clearTimer();
          return 0;
        }
        return t - 1;
      });
    }, 1000);
  }

  function clearTimer() {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }

  async function handleSubmit() {
    if (phase.stage !== "answering" || !answer.trim()) return;
    clearTimer();
    setSubmitting(true);
    try {
      const feedback = await submitAnswer(
        sessionId,
        phase.question.id,
        { answer: answer.trim() },
        token,
      );
      setPhase({ stage: "feedback", feedback, question: phase.question, index: phase.index, total: phase.total });
    } catch (err: unknown) {
      setPhase({
        stage: "error",
        message: err instanceof Error ? err.message : "Failed to submit answer",
      });
    } finally {
      setSubmitting(false);
    }
  }

  function handleNext() {
    if (phase.stage !== "feedback") return;
    if (phase.feedback.is_session_complete) {
      setPhase({ stage: "complete" });
      return;
    }
    const nextIndex = phase.index + 1;
    const nextQuestion = questions[nextIndex];
    if (!nextQuestion) {
      setPhase({ stage: "complete" });
      return;
    }
    setAnswer("");
    setPhase({ stage: "answering", question: nextQuestion, index: nextIndex, total: phase.total });
    startTimer();
  }

  const timerColor =
    timeLeft <= 30 ? "text-red-500" : timeLeft <= 60 ? "text-amber-500" : "text-gray-500";

  if (phase.stage === "loading") {
    return (
      <div className="flex min-h-[300px] items-center justify-center">
        <p className="text-sm text-gray-500">Loading session…</p>
      </div>
    );
  }

  if (phase.stage === "error") {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-center">
        <p className="font-medium text-red-700">Something went wrong</p>
        <p className="mt-1 text-sm text-red-500">{phase.message}</p>
      </div>
    );
  }

  if (phase.stage === "complete") {
    return (
      <div className="mx-auto max-w-lg py-20 text-center">
        <div className="text-5xl mb-4">🎉</div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Session Complete!</h1>
        <p className="text-gray-500 mb-8 text-sm">
          Your answers have been evaluated. View your scores on the dashboard.
        </p>
        <button
          onClick={() => router.push("/dashboard")}
          className="rounded-lg bg-indigo-600 px-6 py-3 text-sm font-semibold text-white hover:bg-indigo-700"
        >
          View Dashboard
        </button>
      </div>
    );
  }

  if (phase.stage === "feedback") {
    const { feedback, index, total } = phase;
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-gray-900">Feedback</h2>
          <span className="text-sm text-gray-400">Question {index + 1} of {total}</span>
        </div>

        {/* Composite score */}
        <div className="rounded-lg border border-indigo-100 bg-indigo-50 p-5 text-center">
          <p className="text-sm text-indigo-600 font-medium">Composite Score</p>
          <p className="text-4xl font-bold text-indigo-700 mt-1">
            {feedback.composite_score.toFixed(1)}
            <span className="text-lg font-normal text-indigo-400">/10</span>
          </p>
        </div>

        {/* Summary */}
        <div className="rounded-lg border border-gray-200 bg-white p-5">
          <p className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">Summary</p>
          <p className="text-gray-700 text-sm leading-relaxed">{feedback.feedback_summary}</p>
        </div>

        {/* Dimension scores */}
        <div className="rounded-lg border border-gray-200 bg-white p-5 space-y-3">
          <p className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-1">Scores</p>
          {(
            [
              ["Clarity", feedback.ai_scores.clarity, feedback.dimension_feedback.clarity],
              ["Depth", feedback.ai_scores.depth, feedback.dimension_feedback.depth],
              ["Structure", feedback.ai_scores.structure, feedback.dimension_feedback.structure],
              ["Relevance", feedback.ai_scores.relevance, feedback.dimension_feedback.relevance],
              ["Communication", feedback.ai_scores.communication_quality, feedback.dimension_feedback.communication_quality],
            ] as [string, number, string][]
          ).map(([label, score, fb]) => (
            <div key={label}>
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm text-gray-700">{label}</span>
                <span className="text-sm font-semibold text-gray-900">{score}/10</span>
              </div>
              <div className="h-1.5 rounded-full bg-gray-100 mb-1">
                <div
                  className="h-1.5 rounded-full bg-indigo-500"
                  style={{ width: `${score * 10}%` }}
                />
              </div>
              <p className="text-xs text-gray-500">{fb}</p>
            </div>
          ))}
        </div>

        {/* Improvement suggestion */}
        <div className="rounded-lg border border-amber-100 bg-amber-50 p-4">
          <p className="text-xs font-semibold text-amber-700 uppercase tracking-wide mb-1">
            Improvement Tip
          </p>
          <p className="text-sm text-amber-800">{feedback.improvement_suggestion}</p>
        </div>

        <button
          onClick={handleNext}
          className="w-full rounded-lg bg-indigo-600 px-6 py-3 text-sm font-semibold text-white hover:bg-indigo-700"
        >
          {feedback.is_session_complete ? "View Dashboard" : "Next Question →"}
        </button>
      </div>
    );
  }

  // answering stage
  const { question, index, total } = phase;
  const minutes = Math.floor(timeLeft / 60);
  const seconds = timeLeft % 60;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-gray-500">
          Question {index + 1} of {total}
        </span>
        <span className={`text-sm font-mono font-semibold ${timerColor}`}>
          {minutes}:{String(seconds).padStart(2, "0")}
        </span>
      </div>

      <div className="rounded-lg border border-gray-200 bg-white p-5">
        <p className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">Question</p>
        <p className="text-gray-900 leading-relaxed">{question.question_text}</p>
      </div>

      <div>
        <label className="block text-sm font-semibold text-gray-700 mb-2">Your Answer</label>
        <textarea
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
          rows={8}
          placeholder="Type your answer here…"
          className="w-full rounded-lg border border-gray-300 px-4 py-3 text-sm text-gray-900 placeholder-gray-400 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 resize-none"
        />
      </div>

      <button
        onClick={handleSubmit}
        disabled={!answer.trim() || submitting}
        className="w-full rounded-lg bg-indigo-600 px-6 py-3 text-sm font-semibold text-white disabled:opacity-40 hover:bg-indigo-700 transition-colors"
      >
        {submitting ? "Evaluating…" : "Submit Answer"}
      </button>
    </div>
  );
}
