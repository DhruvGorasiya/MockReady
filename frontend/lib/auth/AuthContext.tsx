"use client";

import { createContext, useContext, useEffect, useState } from "react";
import {
  login as apiLogin,
  register as apiRegister,
  getMe,
  type UserResponse,
  type UserRole,
} from "@/lib/api/auth";
import { ApiError } from "@/lib/api/client";

const TOKEN_KEY = "mockready_access_token";

interface AuthContextValue {
  token: string | null;
  user: UserResponse | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<UserResponse>;
  register: (
    email: string,
    password: string,
    role?: UserRole,
  ) => Promise<UserResponse>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<UserResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Hydrate from localStorage on mount. If a token is present, validate it
  // with /auth/me and capture the user's role; auto-logout on 401 so a stale
  // token can't leave the UI stuck in a half-authenticated state.
  useEffect(() => {
    const stored = localStorage.getItem(TOKEN_KEY);
    if (!stored) {
      setIsLoading(false);
      return;
    }

    let cancelled = false;
    (async () => {
      try {
        const me = await getMe(stored);
        if (cancelled) return;
        setToken(stored);
        setUser(me);
      } catch (err) {
        if (cancelled) return;
        if (err instanceof ApiError && err.status === 401) {
          localStorage.removeItem(TOKEN_KEY);
        }
        // Any other error leaves us unauthenticated; the router guards will
        // bounce the user to /login.
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, []);

  async function login(email: string, password: string) {
    const { access_token } = await apiLogin({ email, password });
    localStorage.setItem(TOKEN_KEY, access_token);
    const me = await getMe(access_token);
    setToken(access_token);
    setUser(me);
    return me;
  }

  async function register(email: string, password: string, role?: UserRole) {
    await apiRegister({ email, password, role });
    // Auto-login so the caller has a valid session + role
    return login(email, password);
  }

  function logout() {
    localStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setUser(null);
  }

  return (
    <AuthContext.Provider
      value={{
        token,
        user,
        isAuthenticated: token !== null,
        isLoading,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}
