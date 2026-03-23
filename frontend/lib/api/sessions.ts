import { apiFetch } from "@/lib/api/client";
import type {
  AnswerFeedbackResponse,
  CreateSessionRequest,
  SessionCreatedResponse,
  SessionDetail,
  SessionHistoryResponse,
  SubmitAnswerRequest,
  TrendResponse,
} from "@/lib/types/session";

const BASE = "/api/v1/sessions";

export async function getSessionHistory(
  token: string,
): Promise<SessionHistoryResponse> {
  return apiFetch<SessionHistoryResponse>(`${BASE}/history`, {}, token);
}

export async function getSessionDetail(
  id: string,
  token: string,
): Promise<SessionDetail> {
  return apiFetch<SessionDetail>(`${BASE}/${id}`, {}, token);
}

export async function getScoreTrends(token: string): Promise<TrendResponse> {
  return apiFetch<TrendResponse>(`${BASE}/trends`, {}, token);
}

export async function createSession(
  request: CreateSessionRequest,
  token: string,
): Promise<SessionCreatedResponse> {
  return apiFetch<SessionCreatedResponse>(
    BASE,
    { method: "POST", body: JSON.stringify(request) },
    token,
  );
}

export async function submitAnswer(
  sessionId: string,
  questionId: string,
  body: SubmitAnswerRequest,
  token: string,
): Promise<AnswerFeedbackResponse> {
  return apiFetch<AnswerFeedbackResponse>(
    `${BASE}/${sessionId}/questions/${questionId}/answer`,
    { method: "POST", body: JSON.stringify(body) },
    token,
  );
}
