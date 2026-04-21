/**
 * Tests for AuthContext — covers localStorage hydration, login, logout,
 * register, role capture via /auth/me, and auto-logout on 401.
 */
import { render, screen, act, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useAuth } from "@/lib/auth/AuthContext";
import { ApiError } from "@/lib/api/client";

// Mock the auth API
jest.mock("@/lib/api/auth", () => ({
  login: jest.fn(),
  register: jest.fn(),
  getMe: jest.fn(),
}));

import * as authApi from "@/lib/api/auth";

const mockLogin = authApi.login as jest.Mock;
const mockRegister = authApi.register as jest.Mock;
const mockGetMe = authApi.getMe as jest.Mock;

function candidateMe(overrides: Partial<{ id: string; email: string }> = {}) {
  return {
    id: overrides.id ?? "u1",
    email: overrides.email ?? "candidate@test.com",
    role: "candidate",
    created_at: "2026-01-01T00:00:00Z",
  };
}

function coachMe() {
  return {
    id: "c1",
    email: "coach@test.com",
    role: "coach",
    created_at: "2026-01-01T00:00:00Z",
  };
}

// Helper component that exposes auth context values
function AuthConsumer() {
  const auth = useAuth();
  return (
    <div>
      <span data-testid="loading">{String(auth.isLoading)}</span>
      <span data-testid="authenticated">{String(auth.isAuthenticated)}</span>
      <span data-testid="token">{auth.token ?? "null"}</span>
      <span data-testid="role">{auth.user?.role ?? "null"}</span>
      <button onClick={() => auth.login("a@b.com", "Password1")}>login</button>
      <button onClick={() => auth.register("a@b.com", "Password1")}>
        register
      </button>
      <button onClick={() => auth.register("a@b.com", "Password1", "coach")}>
        register-coach
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
    await waitFor(() =>
      expect(screen.getByTestId("loading")).toHaveTextContent("false"),
    );
    expect(screen.getByTestId("authenticated")).toHaveTextContent("false");
    expect(screen.getByTestId("token")).toHaveTextContent("null");
    expect(mockGetMe).not.toHaveBeenCalled();
  });

  it("hydrates token from localStorage and fetches role via /auth/me", async () => {
    localStorage.setItem(TOKEN_KEY, "existing-token");
    mockGetMe.mockResolvedValue(candidateMe());

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
    expect(screen.getByTestId("role")).toHaveTextContent("candidate");
    expect(mockGetMe).toHaveBeenCalledWith("existing-token");
  });

  it("auto-logs out when /auth/me returns 401 during hydration", async () => {
    localStorage.setItem(TOKEN_KEY, "stale-token");
    mockGetMe.mockRejectedValue(new ApiError(401, "Not authenticated"));

    render(
      <AuthProvider>
        <AuthConsumer />
      </AuthProvider>,
    );

    await waitFor(() =>
      expect(screen.getByTestId("loading")).toHaveTextContent("false"),
    );
    expect(screen.getByTestId("authenticated")).toHaveTextContent("false");
    expect(screen.getByTestId("token")).toHaveTextContent("null");
    expect(localStorage.getItem(TOKEN_KEY)).toBeNull();
  });

  it("login stores token, fetches role via /me, and sets isAuthenticated=true", async () => {
    mockLogin.mockResolvedValue({
      access_token: "new-token",
      token_type: "bearer",
    });
    mockGetMe.mockResolvedValue(candidateMe());

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
    expect(screen.getByTestId("role")).toHaveTextContent("candidate");
    expect(mockGetMe).toHaveBeenCalledWith("new-token");
    expect(localStorage.getItem(TOKEN_KEY)).toBe("new-token");
  });

  it("login captures coach role when /me returns coach", async () => {
    mockLogin.mockResolvedValue({
      access_token: "coach-token",
      token_type: "bearer",
    });
    mockGetMe.mockResolvedValue(coachMe());

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

    expect(screen.getByTestId("role")).toHaveTextContent("coach");
  });

  it("logout clears token, user, and localStorage", async () => {
    localStorage.setItem(TOKEN_KEY, "existing-token");
    mockGetMe.mockResolvedValue(candidateMe());

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
    expect(screen.getByTestId("role")).toHaveTextContent("null");
    expect(localStorage.getItem(TOKEN_KEY)).toBeNull();
  });

  it("register forwards role to the API and auto-logs in", async () => {
    mockRegister.mockResolvedValue({
      id: "c1",
      email: "coach@test.com",
      role: "coach",
      created_at: "2026-01-01T00:00:00Z",
    });
    mockLogin.mockResolvedValue({
      access_token: "reg-token",
      token_type: "bearer",
    });
    mockGetMe.mockResolvedValue(coachMe());

    render(
      <AuthProvider>
        <AuthConsumer />
      </AuthProvider>,
    );
    await waitFor(() =>
      expect(screen.getByTestId("loading")).toHaveTextContent("false"),
    );

    await act(async () => {
      await userEvent.click(screen.getByText("register-coach"));
    });

    expect(mockRegister).toHaveBeenCalledWith({
      email: "a@b.com",
      password: "Password1",
      role: "coach",
    });
    expect(mockLogin).toHaveBeenCalledWith({
      email: "a@b.com",
      password: "Password1",
    });
    expect(screen.getByTestId("authenticated")).toHaveTextContent("true");
    expect(screen.getByTestId("role")).toHaveTextContent("coach");
  });

  it("register without role omits role from payload (backwards compat)", async () => {
    mockRegister.mockResolvedValue({
      id: "u1",
      email: "a@b.com",
      role: "candidate",
      created_at: "2026-01-01T00:00:00Z",
    });
    mockLogin.mockResolvedValue({
      access_token: "reg-token",
      token_type: "bearer",
    });
    mockGetMe.mockResolvedValue(candidateMe());

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
      role: undefined,
    });
  });
});
