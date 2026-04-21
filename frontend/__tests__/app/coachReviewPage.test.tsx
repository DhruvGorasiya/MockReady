/**
 * Tests for the coach session review page — focuses on cross-question
 * state handling in <CoachScoreForm> as the coach navigates Previous/Next.
 */
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

jest.mock("@/lib/api/coach", () => ({
  getCoachSessionDetail: jest.fn(),
  submitCoachScore: jest.fn(),
}));

jest.mock("@/lib/auth/AuthContext", () => ({
  useAuth: jest.fn(() => ({ token: "coach-token" })),
}));

import * as coachApi from "@/lib/api/coach";
import CoachSessionReviewPage from "@/app/(coach)/review/[sessionId]/page";

const mockGetDetail = coachApi.getCoachSessionDetail as jest.Mock;

function q(id: string, ai: Partial<Record<string, number>>, order = 0) {
  return {
    id,
    question_text: `Question ${id}`,
    candidate_answer: `Answer ${id}`,
    order_index: order,
    ai_scores: {
      clarity: ai.clarity ?? 5,
      depth: ai.depth ?? 5,
      structure: ai.structure ?? 5,
      relevance: ai.relevance ?? 5,
      communication_quality: ai.communication_quality ?? 5,
    },
    coach_scores: null,
    feedback: null,
  };
}

const twoQuestionSession = {
  id: "s1",
  interview_type: "behavioral",
  role: "SWE",
  status: "completed",
  composite_score: 5,
  created_at: "2026-01-01T00:00:00Z",
  questions: [q("q1", { clarity: 7 }, 0), q("q2", { clarity: 3 }, 1)],
};

beforeEach(() => jest.clearAllMocks());

describe("CoachSessionReviewPage", () => {
  it("clears justification and resets scores when Next is clicked", async () => {
    mockGetDetail.mockResolvedValue(twoQuestionSession);

    render(<CoachSessionReviewPage params={{ sessionId: "s1" }} />);

    // Wait for detail to load
    await waitFor(() =>
      expect(screen.getByText("Question q1")).toBeInTheDocument(),
    );

    // Clarity input is pre-filled with Q1's AI score (7)
    expect(screen.getByLabelText(/clarity/i)).toHaveValue(7);

    // Coach types a justification while reviewing Q1
    const justification = screen.getByLabelText(/justification/i);
    await userEvent.type(justification, "Good opening but rushed the middle.");
    expect(justification).toHaveValue("Good opening but rushed the middle.");

    // Coach changes clarity score manually
    const clarityInput = screen.getByLabelText(/clarity/i);
    await userEvent.clear(clarityInput);
    await userEvent.type(clarityInput, "9");
    expect(clarityInput).toHaveValue(9);

    // Move to Q2
    await userEvent.click(screen.getByRole("button", { name: /next/i }));

    // Confirm we're on Q2
    await waitFor(() =>
      expect(screen.getByText("Question q2")).toBeInTheDocument(),
    );

    // Justification must be empty — no bleed from Q1
    expect(screen.getByLabelText(/justification/i)).toHaveValue("");

    // Clarity score must match Q2's AI score (3), NOT the 9 the coach typed for Q1
    expect(screen.getByLabelText(/clarity/i)).toHaveValue(3);
  });
});
