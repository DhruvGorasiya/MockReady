/**
 * Tests for DashboardClient — the client component that owns fetching
 * and all render states. API calls are mocked at the module level.
 */
import { render, screen, waitFor } from "@testing-library/react";
import DashboardClient from "@/components/session/DashboardClient";

// recharts uses ResizeObserver internally — stub it for jsdom
global.ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
};

jest.mock("@/lib/api/sessions", () => ({
  getSessionHistory: jest.fn(),
  getScoreTrends: jest.fn(),
}));

jest.mock("@/lib/auth/AuthContext", () => ({
  useAuth: jest.fn(() => ({
    token: "test-token",
    isAuthenticated: true,
    isLoading: false,
  })),
}));

import * as sessionsApi from "@/lib/api/sessions";

const mockGetSessionHistory = sessionsApi.getSessionHistory as jest.Mock;
const mockGetScoreTrends = sessionsApi.getScoreTrends as jest.Mock;

const baseSession = {
  id: "s1",
  interview_type: "behavioral" as const,
  role: "SWE" as const,
  status: "completed" as const,
  composite_score: 7.5,
  created_at: "2026-01-15T10:00:00Z",
};

const baseTrendPoint = {
  session_id: "s1",
  created_at: "2026-01-15T10:00:00Z",
  composite_score: 7.5,
  dimension_scores: {
    clarity: 7,
    depth: 7,
    structure: 7,
    relevance: 7,
    communication_quality: 7,
  },
};

beforeEach(() => {
  jest.clearAllMocks();
});

describe("DashboardClient", () => {
  it("shows a loading state while fetching", async () => {
    // Never resolves during this assertion
    mockGetSessionHistory.mockReturnValue(new Promise(() => {}));
    mockGetScoreTrends.mockReturnValue(new Promise(() => {}));

    render(<DashboardClient />);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it("shows empty state when API returns 0 sessions", async () => {
    mockGetSessionHistory.mockResolvedValue({ sessions: [], total: 0 });
    mockGetScoreTrends.mockResolvedValue({ points: [] });

    render(<DashboardClient />);
    await waitFor(() =>
      expect(screen.getByText(/no sessions yet/i)).toBeInTheDocument(),
    );
  });

  it("renders a SessionCard for each session", async () => {
    mockGetSessionHistory.mockResolvedValue({
      sessions: [baseSession, { ...baseSession, id: "s2" }],
      total: 2,
    });
    mockGetScoreTrends.mockResolvedValue({ points: [] });

    render(<DashboardClient />);
    await waitFor(() => {
      const cards = screen.getAllByText(/behavioral/i);
      expect(cards.length).toBeGreaterThanOrEqual(2);
    });
  });

  it("renders the TrendChart when trend data is present", async () => {
    mockGetSessionHistory.mockResolvedValue({
      sessions: [baseSession],
      total: 1,
    });
    mockGetScoreTrends.mockResolvedValue({ points: [baseTrendPoint] });

    render(<DashboardClient />);
    await waitFor(() =>
      expect(screen.getByTestId("trend-chart")).toBeInTheDocument(),
    );
  });

  it("shows an error message on API failure", async () => {
    mockGetSessionHistory.mockRejectedValue(new Error("Network error"));
    mockGetScoreTrends.mockRejectedValue(new Error("Network error"));

    render(<DashboardClient />);
    await waitFor(() =>
      expect(screen.getByText(/something went wrong/i)).toBeInTheDocument(),
    );
  });
});
