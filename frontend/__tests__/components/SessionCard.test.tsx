import { render, screen } from "@testing-library/react";
import SessionCard from "@/components/session/SessionCard";
import type { SessionSummary } from "@/lib/types/session";

const base: SessionSummary = {
  id: "abc-123",
  interview_type: "behavioral",
  role: "SWE",
  status: "completed",
  composite_score: 7.5,
  created_at: "2026-01-15T10:00:00Z",
};

describe("SessionCard", () => {
  it("renders the interview type", () => {
    render(<SessionCard session={base} />);
    expect(screen.getByText(/behavioral/i)).toBeInTheDocument();
  });

  it("renders the role", () => {
    render(<SessionCard session={base} />);
    expect(screen.getByText(/SWE/i)).toBeInTheDocument();
  });

  it("renders the composite score", () => {
    render(<SessionCard session={base} />);
    expect(screen.getByText(/7\.5/)).toBeInTheDocument();
  });

  it("renders the session date", () => {
    render(<SessionCard session={base} />);
    // Jan 15, 2026 in any locale-aware format
    expect(screen.getByText(/jan/i)).toBeInTheDocument();
  });

  it("shows 'Pending' when composite_score is null", () => {
    render(<SessionCard session={{ ...base, composite_score: null }} />);
    expect(screen.getByText(/pending/i)).toBeInTheDocument();
  });

  it("shows the session status", () => {
    render(<SessionCard session={base} />);
    expect(screen.getByText(/completed/i)).toBeInTheDocument();
  });
});
