/**
 * Tests for SessionDetailClient — client component for the session detail page.
 */
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import SessionDetailClient from "@/components/session/SessionDetailClient";

jest.mock("@/lib/api/sessions", () => ({
  getSessionDetail: jest.fn(),
}));

jest.mock("@/lib/auth/AuthContext", () => ({
  useAuth: jest.fn(() => ({
    token: "test-token",
    isAuthenticated: true,
    isLoading: false,
  })),
}));

import * as sessionsApi from "@/lib/api/sessions";

const mockGetSessionDetail = sessionsApi.getSessionDetail as jest.Mock;

const dimScores = {
  clarity: 7,
  depth: 6,
  structure: 8,
  relevance: 7,
  communication_quality: 5,
};

const baseDetail = {
  id: "s1",
  interview_type: "behavioral" as const,
  role: "SWE" as const,
  status: "completed" as const,
  composite_score: 6.6,
  created_at: "2026-01-15T10:00:00Z",
  questions: [
    {
      id: "q1",
      question_text: "Tell me about a time you led a project.",
      candidate_answer: "I led a team of five engineers...",
      order_index: 0,
      ai_scores: dimScores,
      coach_scores: null,
      feedback: { clarity: "Good opening structure." },
    },
    {
      id: "q2",
      question_text: "Describe a technical challenge you overcame.",
      candidate_answer: "We had a scaling issue...",
      order_index: 1,
      ai_scores: dimScores,
      coach_scores: null,
      feedback: null,
    },
  ],
};

beforeEach(() => {
  jest.clearAllMocks();
});

describe("SessionDetailClient", () => {
  it("shows a loading state while fetching", () => {
    mockGetSessionDetail.mockReturnValue(new Promise(() => {}));
    render(<SessionDetailClient sessionId="s1" />);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it("renders the first question text after load", async () => {
    mockGetSessionDetail.mockResolvedValue(baseDetail);
    render(<SessionDetailClient sessionId="s1" />);
    await waitFor(() =>
      expect(
        screen.getByText(/tell me about a time you led a project/i),
      ).toBeInTheDocument(),
    );
  });

  it("renders DimensionBreakdown for the current question", async () => {
    mockGetSessionDetail.mockResolvedValue(baseDetail);
    render(<SessionDetailClient sessionId="s1" />);
    await waitFor(() =>
      expect(screen.getByText(/clarity/i)).toBeInTheDocument(),
    );
  });

  it("navigates to the next question", async () => {
    mockGetSessionDetail.mockResolvedValue(baseDetail);
    render(<SessionDetailClient sessionId="s1" />);

    await waitFor(() =>
      expect(screen.getByText(/tell me about a time/i)).toBeInTheDocument(),
    );

    await userEvent.click(screen.getByRole("button", { name: /next/i }));

    expect(
      screen.getByText(/describe a technical challenge/i),
    ).toBeInTheDocument();
  });

  it("shows coach scores as authoritative when present", async () => {
    const coachScores = {
      clarity: 9,
      depth: 9,
      structure: 9,
      relevance: 9,
      communication_quality: 9,
    };
    const detailWithCoach = {
      ...baseDetail,
      questions: [
        { ...baseDetail.questions[0], coach_scores: coachScores },
        baseDetail.questions[1],
      ],
    };
    mockGetSessionDetail.mockResolvedValue(detailWithCoach);
    render(<SessionDetailClient sessionId="s1" />);

    await waitFor(() => expect(screen.getByText(/coach/i)).toBeInTheDocument());
  });

  it("shows an error message on API failure", async () => {
    mockGetSessionDetail.mockRejectedValue(new Error("Not found"));
    render(<SessionDetailClient sessionId="s1" />);
    await waitFor(() =>
      expect(screen.getByText(/something went wrong/i)).toBeInTheDocument(),
    );
  });
});
