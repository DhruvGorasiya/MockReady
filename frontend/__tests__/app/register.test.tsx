/**
 * Tests for the Register page — form rendering, validation, submission.
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
import RegisterPage from "@/app/register/page";

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

describe("RegisterPage", () => {
  it("renders email, password, and confirm password fields", () => {
    render(<RegisterPage />);
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^password/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument();
  });

  it("renders a submit button", () => {
    render(<RegisterPage />);
    expect(screen.getByRole("button", { name: /create account/i })).toBeInTheDocument();
  });

  it("renders a link to the login page", () => {
    render(<RegisterPage />);
    expect(screen.getByRole("link", { name: /log in/i })).toBeInTheDocument();
  });

  it("shows client-side error when passwords do not match", async () => {
    render(<RegisterPage />);

    await userEvent.type(screen.getByLabelText(/email/i), "user@test.com");
    await userEvent.type(screen.getByLabelText(/^password/i), "Password1");
    await userEvent.type(screen.getByLabelText(/confirm password/i), "Different1");
    await userEvent.click(screen.getByRole("button", { name: /create account/i }));

    await waitFor(() => {
      expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument();
    });
  });

  it("calls register with email and password on valid submit", async () => {
    const mockRegister = jest.fn().mockResolvedValue(undefined);
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
    await userEvent.type(screen.getByLabelText(/confirm password/i), "Password1");
    await userEvent.click(screen.getByRole("button", { name: /create account/i }));

    await waitFor(() => {
      expect(mockRegister).toHaveBeenCalledWith("user@test.com", "Password1");
    });
  });

  it("shows an error message when register throws", async () => {
    const mockRegister = jest.fn().mockRejectedValue(new Error("Email already registered"));
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
    await userEvent.type(screen.getByLabelText(/confirm password/i), "Password1");
    await userEvent.click(screen.getByRole("button", { name: /create account/i }));

    await waitFor(() => {
      expect(screen.getByText(/email already registered/i)).toBeInTheDocument();
    });
  });
});
