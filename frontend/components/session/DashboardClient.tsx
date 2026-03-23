"use client";

import { useEffect, useState } from "react";
import { getScoreTrends, getSessionHistory } from "@/lib/api/sessions";
import type {
  SessionHistoryResponse,
  TrendResponse,
} from "@/lib/types/session";
import EmptySessionState from "@/components/session/EmptySessionState";
import SessionCard from "@/components/session/SessionCard";
import TrendChart from "@/components/session/TrendChart";

type State =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "ok"; history: SessionHistoryResponse; trends: TrendResponse };

export default function DashboardClient() {
  const [state, setState] = useState<State>({ status: "loading" });

  useEffect(() => {
    // Token is sourced from the session cookie/storage in a real auth flow.
    // For now, read from env so the component stays testable without auth.
    const token = process.env.NEXT_PUBLIC_API_TOKEN ?? "";

    Promise.all([getSessionHistory(token), getScoreTrends(token)])
      .then(([history, trends]) => {
        setState({ status: "ok", history, trends });
      })
      .catch((err: unknown) => {
        const message = err instanceof Error ? err.message : "Unknown error";
        setState({ status: "error", message });
      });
  }, []);

  if (state.status === "loading") {
    return (
      <div className="flex min-h-[200px] items-center justify-center">
        <p className="text-sm text-gray-500">Loading your sessions…</p>
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

  const { history, trends } = state;

  if (history.total === 0) {
    return <EmptySessionState />;
  }

  return (
    <div className="space-y-8">
      <section>
        <h2 className="mb-4 text-lg font-semibold text-gray-800">
          Score Trend
        </h2>
        <TrendChart points={trends.points} />
      </section>

      <section>
        <h2 className="mb-4 text-lg font-semibold text-gray-800">
          Past Sessions{" "}
          <span className="text-sm font-normal text-gray-500">
            ({history.total})
          </span>
        </h2>
        <div className="space-y-3">
          {history.sessions.map((session) => (
            <a key={session.id} href={`/sessions/${session.id}`}>
              <SessionCard session={session} />
            </a>
          ))}
        </div>
      </section>
    </div>
  );
}
