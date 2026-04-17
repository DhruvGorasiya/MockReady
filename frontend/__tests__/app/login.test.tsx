/**
 * Tests for the Login page — form rendering, submission, error display.
 */
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

jest.mock("next/navigation", () => ({
  useRouter: jest.fn(() => ({ push: jest.fn(), replace: jest.fn() })),
}));

jest.mock("@/lib/auth/AuthContext", () => ({
  useAuth: jest.fn(),
}));

import { useAuth } from "@/lib/auth/AuthContext";
import LoginPage from "@/app/login/page";

const mockUseAuth = useAuth as jest.Mock;

beforeEach(() => {
  jest.clearAllMocks();
  mockUseAuth.mockReturnValue({
    isAuthenticated: false,
    isLoading: false,
    login: jest.fn(),
    register: jest.fn(),
    logout: jest.fn(),
    token: null,
  });
});

describe("LoginPage", () => {
  it("renders email and password fields", () => {
    render(<LoginPage />);
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
  });

  it("renders a submit button", () => {
    render(<LoginPage />);
    expect(screen.getByRole("button", { name: /log in/i })).toBeInTheDocument();
  });

  it("renders a link to the register page", () => {
    render(<LoginPage />);
    expect(screen.getByRole("link", { name: /create an account/i })).toBeInTheDocument();
  });

  it("calls login with email and password on submit", async () => {
    const mockLogin = jest.fn().mockResolvedValue(undefined);
    mockUseAuth.mockReturnValue({
      isAuthenticated: false,
      isLoading: false,
      login: mockLogin,
      register: jest.fn(),
      logout: jest.fn(),
      token: null,
    });

    render(<LoginPage />);

    await userEvent.type(screen.getByLabelText(/email/i), "user@test.com");
    await userEvent.type(screen.getByLabelText(/password/i), "Password1");
    await userEvent.click(screen.getByRole("button", { name: /log in/i }));

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith("user@test.com", "Password1");
    });
  });

  it("shows an error message when login throws", async () => {
    const mockLogin = jest.fn().mockRejectedValue(new Error("Invalid credentials"));
    mockUseAuth.mockReturnValue({
      isAuthenticated: false,
      isLoading: false,
      login: mockLogin,
      register: jest.fn(),
      logout: jest.fn(),
      token: null,
    });

    render(<LoginPage />);

    await userEvent.type(screen.getByLabelText(/email/i), "user@test.com");
    await userEvent.type(screen.getByLabelText(/password/i), "wrongpass");
    await userEvent.click(screen.getByRole("button", { name: /log in/i }));

    await waitFor(() => {
      expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
    });
  });
});
