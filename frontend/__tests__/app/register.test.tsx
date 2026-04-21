/**
 * Tests for the Register page — form rendering, validation, submission.
 */
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

const mockSearchParams = new URLSearchParams();
jest.mock("next/navigation", () => ({
  useRouter: jest.fn(() => ({ push: jest.fn(), replace: jest.fn() })),
  useSearchParams: jest.fn(() => mockSearchParams),
}));

jest.mock("@/lib/auth/AuthContext", () => ({
  useAuth: jest.fn(),
}));

import { useAuth } from "@/lib/auth/AuthContext";
import RegisterPage from "@/app/register/page";

const mockUseAuth = useAuth as jest.Mock;

function setSearchParam(key: string, value: string | null) {
  // URLSearchParams doesn't have a "clear" — rebuild in place.
  for (const k of Array.from(mockSearchParams.keys())) {
    mockSearchParams.delete(k);
  }
  if (value !== null) mockSearchParams.set(key, value);
}

beforeEach(() => {
  jest.clearAllMocks();
  setSearchParam("role", null);
  mockUseAuth.mockReturnValue({
    isAuthenticated: false,
    isLoading: false,
    login: jest.fn(),
    register: jest.fn(),
    logout: jest.fn(),
    token: null,
  });
});

describe("RegisterPage", () => {
  it("renders email, password, and confirm password fields", () => {
    render(<RegisterPage />);
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^password/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument();
  });

  it("renders a submit button", () => {
    render(<RegisterPage />);
    expect(
      screen.getByRole("button", { name: /create account/i }),
    ).toBeInTheDocument();
  });

  it("renders a link to the login page", () => {
    render(<RegisterPage />);
    expect(screen.getByRole("link", { name: /log in/i })).toBeInTheDocument();
  });

  it("shows client-side error when passwords do not match", async () => {
    render(<RegisterPage />);

    await userEvent.type(screen.getByLabelText(/email/i), "user@test.com");
    await userEvent.type(screen.getByLabelText(/^password/i), "Password1");
    await userEvent.type(
      screen.getByLabelText(/confirm password/i),
      "Different1",
    );
    await userEvent.click(
      screen.getByRole("button", { name: /create account/i }),
    );

    await waitFor(() => {
      expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument();
    });
  });

  it("calls register with candidate role by default", async () => {
    const mockRegister = jest.fn().mockResolvedValue({
      id: "u1",
      email: "user@test.com",
      role: "candidate",
      created_at: "2026-01-01T00:00:00Z",
    });
    mockUseAuth.mockReturnValue({
      isAuthenticated: false,
      isLoading: false,
      login: jest.fn(),
      register: mockRegister,
      logout: jest.fn(),
      token: null,
    });

    render(<RegisterPage />);

    await userEvent.type(screen.getByLabelText(/email/i), "user@test.com");
    await userEvent.type(screen.getByLabelText(/^password/i), "Password1");
    await userEvent.type(
      screen.getByLabelText(/confirm password/i),
      "Password1",
    );
    await userEvent.click(
      screen.getByRole("button", { name: /create account/i }),
    );

    await waitFor(() => {
      expect(mockRegister).toHaveBeenCalledWith(
        "user@test.com",
        "Password1",
        "candidate",
      );
    });
  });

  it("shows the coach badge when the role query param is coach", () => {
    setSearchParam("role", "coach");
    render(<RegisterPage />);
    expect(screen.getByTestId("coach-role-badge")).toHaveTextContent(
      /registering as coach/i,
    );
  });

  it("does not show the coach badge for default candidate role", () => {
    render(<RegisterPage />);
    expect(screen.queryByTestId("coach-role-badge")).not.toBeInTheDocument();
  });

  it("ignores unknown role values and falls back to candidate", () => {
    setSearchParam("role", "admin");
    render(<RegisterPage />);
    expect(screen.queryByTestId("coach-role-badge")).not.toBeInTheDocument();
  });

  it("passes coach role to register() when ?role=coach", async () => {
    setSearchParam("role", "coach");
    const mockRegister = jest.fn().mockResolvedValue({
      id: "c1",
      email: "coach@test.com",
      role: "coach",
      created_at: "2026-01-01T00:00:00Z",
    });
    mockUseAuth.mockReturnValue({
      isAuthenticated: false,
      isLoading: false,
      login: jest.fn(),
      register: mockRegister,
      logout: jest.fn(),
      token: null,
    });

    render(<RegisterPage />);

    await userEvent.type(screen.getByLabelText(/email/i), "coach@test.com");
    await userEvent.type(screen.getByLabelText(/^password/i), "Password1");
    await userEvent.type(
      screen.getByLabelText(/confirm password/i),
      "Password1",
    );
    await userEvent.click(
      screen.getByRole("button", { name: /create account/i }),
    );

    await waitFor(() => {
      expect(mockRegister).toHaveBeenCalledWith(
        "coach@test.com",
        "Password1",
        "coach",
      );
    });
  });

  it("redirects coach to /review after successful registration", async () => {
    setSearchParam("role", "coach");
    const mockPush = jest.fn();
    (
      jest.requireMock("next/navigation").useRouter as jest.Mock
    ).mockReturnValue({ push: mockPush, replace: jest.fn() });
    const mockRegister = jest.fn().mockResolvedValue({
      id: "c1",
      email: "coach@test.com",
      role: "coach",
      created_at: "2026-01-01T00:00:00Z",
    });
    mockUseAuth.mockReturnValue({
      isAuthenticated: false,
      isLoading: false,
      login: jest.fn(),
      register: mockRegister,
      logout: jest.fn(),
      token: null,
    });

    render(<RegisterPage />);

    await userEvent.type(screen.getByLabelText(/email/i), "coach@test.com");
    await userEvent.type(screen.getByLabelText(/^password/i), "Password1");
    await userEvent.type(
      screen.getByLabelText(/confirm password/i),
      "Password1",
    );
    await userEvent.click(
      screen.getByRole("button", { name: /create account/i }),
    );

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith("/review");
    });
  });

  it("shows an error message when register throws", async () => {
    const mockRegister = jest
      .fn()
      .mockRejectedValue(new Error("Email already registered"));
    mockUseAuth.mockReturnValue({
      isAuthenticated: false,
      isLoading: false,
      login: jest.fn(),
      register: mockRegister,
      logout: jest.fn(),
      token: null,
    });

    render(<RegisterPage />);

    await userEvent.type(screen.getByLabelText(/email/i), "user@test.com");
    await userEvent.type(screen.getByLabelText(/^password/i), "Password1");
    await userEvent.type(
      screen.getByLabelText(/confirm password/i),
      "Password1",
    );
    await userEvent.click(
      screen.getByRole("button", { name: /create account/i }),
    );

    await waitFor(() => {
      expect(screen.getByText(/email already registered/i)).toBeInTheDocument();
    });
  });
});
