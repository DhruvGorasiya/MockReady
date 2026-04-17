"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getSessionsForReview } from "@/lib/api/coach";
import { useAuth } from "@/lib/auth/AuthContext";
import type { SessionHistoryResponse } from "@/lib/types/session";

type State =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "ok"; data: SessionHistoryResponse };

export default function CoachReviewPage() {
  const { token } = useAuth();
  const [state, setState] = useState<State>({ status: "loading" });

  useEffect(() => {
    if (!token) return;
    getSessionsForReview(token)
      .then((data) => setState({ status: "ok", data }))
      .catch((err: unknown) =>
        setState({ status: "error", message: err instanceof Error ? err.message : "Failed to load" }),
      );
  }, [token]);

  if (state.status === "loading") {
    return <p className="text-sm text-gray-500">Loading sessions…</p>;
  }

  if (state.status === "error") {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-center">
        <p className="font-medium text-red-700">Something went wrong</p>
        <p className="mt-1 text-sm text-red-500">{state.message}</p>
      </div>
    );
  }

  const { sessions, total } = state.data;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Sessions to Review</h1>
        <p className="mt-1 text-sm text-gray-500">{total} session{total !== 1 ? "s" : ""} awaiting coach review</p>
      </div>

      {total === 0 ? (
        <div className="rounded-lg border border-gray-200 bg-white p-8 text-center">
          <p className="text-gray-500">All sessions have been reviewed.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {sessions.map((session) => (
            <Link
              key={session.id.toString()}
              href={`/review/${session.id}`}
              className="block rounded-lg border border-gray-200 bg-white p-4 hover:border-indigo-300 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-gray-900 capitalize">
                    {session.interview_type.replace("_", " ")} · {session.role}
                  </p>
                  <p className="mt-0.5 text-sm text-gray-500">
                    {new Date(session.created_at).toLocaleDateString()}
                  </p>
                </div>
                <div className="text-right">
                  {session.composite_score != null && (
                    <p className="text-lg font-semibold text-indigo-600">
                      {session.composite_score.toFixed(1)}
                      <span className="text-sm font-normal text-gray-400">/10</span>
                    </p>
                  )}
                  <span className="text-xs text-amber-600 font-medium">Needs review →</span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
