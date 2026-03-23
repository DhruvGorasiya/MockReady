import { apiFetch } from "@/lib/api/client";
import type {
  SessionDetail,
  SessionHistoryResponse,
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
