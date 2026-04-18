import { API_BASE } from "@/lib/api/config";

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

/**
 * Base fetch wrapper. Attaches the Bearer token from the environment/session
 * and converts non-2xx responses into thrown ApiErrors.
 *
 * Components never call fetch directly — they use functions from lib/api/*.
 */
export async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
  token?: string,
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      const raw = body?.detail ?? detail;
      detail = typeof raw === "string" ? raw : JSON.stringify(raw);
    } catch {
      // leave detail as statusText
    }
    throw new ApiError(response.status, detail);
  }

  return response.json() as Promise<T>;
}
