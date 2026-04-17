/**
 * Tests for AuthContext — covers localStorage hydration, login, logout, register.
 */
import { render, screen, act, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useAuth } from "@/lib/auth/AuthContext";

// Mock the auth API
jest.mock("@/lib/api/auth", () => ({
  login: jest.fn(),
  register: jest.fn(),
}));

import * as authApi from "@/lib/api/auth";

const mockLogin = authApi.login as jest.Mock;
const mockRegister = authApi.register as jest.Mock;

// Helper component that exposes auth context values
function AuthConsumer() {
  const auth = useAuth();
  return (
    <div>
      <span data-testid="loading">{String(auth.isLoading)}</span>
      <span data-testid="authenticated">{String(auth.isAuthenticated)}</span>
      <span data-testid="token">{auth.token ?? "null"}</span>
      <button onClick={() => auth.login("a@b.com", "Password1")}>login</button>
      <button onClick={() => auth.register("a@b.com", "Password1")}>
        register
      </button>
      <button onClick={auth.logout}>logout</button>
    </div>
  );
}

// Wrap in AuthProvider — imported after mocks are registered
let AuthProvider: React.ComponentType<{ children: React.ReactNode }>;
beforeAll(async () => {
  const mod = await import("@/lib/auth/AuthContext");
  AuthProvider = mod.AuthProvider;
});

const TOKEN_KEY = "mockready_access_token";

beforeEach(() => {
  localStorage.clear();
  jest.clearAllMocks();
});

describe("AuthContext", () => {
  it("starts with isLoading=true then settles to false with no stored token", async () => {
    render(
      <AuthProvider>
        <AuthConsumer />
      </AuthProvider>,
    );
    // After hydration settles
    await waitFor(() =>
      expect(screen.getByTestId("loading")).toHaveTextContent("false"),
    );
    expect(screen.getByTestId("authenticated")).toHaveTextContent("false");
    expect(screen.getByTestId("token")).toHaveTextContent("null");
  });

  it("hydrates token from localStorage on mount", async () => {
    localStorage.setItem(TOKEN_KEY, "existing-token");

    render(
      <AuthProvider>
        <AuthConsumer />
      </AuthProvider>,
    );

    await waitFor(() =>
      expect(screen.getByTestId("loading")).toHaveTextContent("false"),
    );
    expect(screen.getByTestId("authenticated")).toHaveTextContent("true");
    expect(screen.getByTestId("token")).toHaveTextContent("existing-token");
  });

  it("login stores token and sets isAuthenticated=true", async () => {
    mockLogin.mockResolvedValue({
      access_token: "new-token",
      token_type: "bearer",
    });

    render(
      <AuthProvider>
        <AuthConsumer />
      </AuthProvider>,
    );
    await waitFor(() =>
      expect(screen.getByTestId("loading")).toHaveTextContent("false"),
    );

    await act(async () => {
      await userEvent.click(screen.getByText("login"));
    });

    expect(screen.getByTestId("authenticated")).toHaveTextContent("true");
    expect(screen.getByTestId("token")).toHaveTextContent("new-token");
    expect(localStorage.getItem(TOKEN_KEY)).toBe("new-token");
  });

  it("logout clears token and sets isAuthenticated=false", async () => {
    localStorage.setItem(TOKEN_KEY, "existing-token");

    render(
      <AuthProvider>
        <AuthConsumer />
      </AuthProvider>,
    );
    await waitFor(() =>
      expect(screen.getByTestId("authenticated")).toHaveTextContent("true"),
    );

    await act(async () => {
      await userEvent.click(screen.getByText("logout"));
    });

    expect(screen.getByTestId("authenticated")).toHaveTextContent("false");
    expect(screen.getByTestId("token")).toHaveTextContent("null");
    expect(localStorage.getItem(TOKEN_KEY)).toBeNull();
  });

  it("register calls register API then auto-logs in", async () => {
    mockRegister.mockResolvedValue({
      id: "u1",
      email: "a@b.com",
      role: "candidate",
    });
    mockLogin.mockResolvedValue({
      access_token: "reg-token",
      token_type: "bearer",
    });

    render(
      <AuthProvider>
        <AuthConsumer />
      </AuthProvider>,
    );
    await waitFor(() =>
      expect(screen.getByTestId("loading")).toHaveTextContent("false"),
    );

    await act(async () => {
      await userEvent.click(screen.getByText("register"));
    });

    expect(mockRegister).toHaveBeenCalledWith({
      email: "a@b.com",
      password: "Password1",
    });
    expect(mockLogin).toHaveBeenCalledWith({
      email: "a@b.com",
      password: "Password1",
    });
    expect(screen.getByTestId("authenticated")).toHaveTextContent("true");
  });
});
