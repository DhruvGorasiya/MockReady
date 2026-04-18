import { apiFetch } from "@/lib/api/client";
import type {
  QuestionResult,
  SessionHistoryResponse,
} from "@/lib/types/session";

const BASE = "/api/v1/coach";

export interface CoachScoreRequest {
  scores: {
    clarity: number;
    depth: number;
    structure: number;
    relevance: number;
    communication_quality: number;
  };
  justification?: string;
}

export async function getSessionsForReview(
  token: string,
): Promise<SessionHistoryResponse> {
  return apiFetch<SessionHistoryResponse>(`${BASE}/sessions`, {}, token);
}

export async function submitCoachScore(
  sessionId: string,
  questionId: string,
  body: CoachScoreRequest,
  token: string,
): Promise<QuestionResult> {
  return apiFetch<QuestionResult>(
    `${BASE}/sessions/${sessionId}/questions/${questionId}/score`,
    { method: "POST", body: JSON.stringify(body) },
    token,
  );
}
