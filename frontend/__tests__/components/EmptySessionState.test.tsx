import { render, screen } from "@testing-library/react";
import EmptySessionState from "@/components/session/EmptySessionState";

describe("EmptySessionState", () => {
  it("renders a call-to-action to start the first session", () => {
    render(<EmptySessionState />);
    expect(screen.getByText(/no sessions yet/i)).toBeInTheDocument();
  });

  it("renders a start session button or link", () => {
    render(<EmptySessionState />);
    expect(screen.getByRole("link", { name: /start/i })).toBeInTheDocument();
  });

  it("renders a descriptive message", () => {
    render(<EmptySessionState />);
    expect(screen.getByText(/practice/i)).toBeInTheDocument();
  });
});
