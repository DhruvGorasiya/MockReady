"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { login as apiLogin, register as apiRegister } from "@/lib/api/auth";

const TOKEN_KEY = "mockready_access_token";

interface AuthContextValue {
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Hydrate from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem(TOKEN_KEY);
    if (stored) setToken(stored);
    setIsLoading(false);
  }, []);

  async function login(email: string, password: string) {
    const { access_token } = await apiLogin({ email, password });
    localStorage.setItem(TOKEN_KEY, access_token);
    setToken(access_token);
  }

  async function register(email: string, password: string) {
    await apiRegister({ email, password });
    // Auto-login after successful registration
    await login(email, password);
  }

  function logout() {
    localStorage.removeItem(TOKEN_KEY);
    setToken(null);
  }

  return (
    <AuthContext.Provider
      value={{
        token,
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
