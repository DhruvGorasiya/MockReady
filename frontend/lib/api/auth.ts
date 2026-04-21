import { API_BASE } from "@/lib/api/config";
import { ApiError } from "@/lib/api/client";

export interface LoginRequest {
  email: string;
  password: string;
}

export type UserRole = "candidate" | "coach" | "admin";

export interface RegisterRequest {
  email: string;
  password: string;
  role?: UserRole;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface UserResponse {
  id: string;
  email: string;
  role: string;
  created_at: string;
}

async function authFetch<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const json = await response.json();
      const raw = json?.detail ?? detail;
      detail = typeof raw === "string" ? raw : JSON.stringify(raw);
    } catch {
      // leave as statusText
    }
    throw new ApiError(response.status, detail);
  }

  return response.json() as Promise<T>;
}

export function login(body: LoginRequest): Promise<TokenResponse> {
  return authFetch<TokenResponse>("/api/v1/auth/login", body);
}

export function register(body: RegisterRequest): Promise<UserResponse> {
  return authFetch<UserResponse>("/api/v1/auth/register", body);
}

export async function getMe(token: string): Promise<UserResponse> {
  const response = await fetch(`${API_BASE}/api/v1/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const json = await response.json();
      const raw = json?.detail ?? detail;
      detail = typeof raw === "string" ? raw : JSON.stringify(raw);
    } catch {
      // leave as statusText
    }
    throw new ApiError(response.status, detail);
  }

  return response.json() as Promise<UserResponse>;
}
