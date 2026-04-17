/**
 * Tests for CoachScoreForm — the per-question score override form.
 */
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

jest.mock("@/lib/api/coach", () => ({
  submitCoachScore: jest.fn(),
}));

jest.mock("@/lib/auth/AuthContext", () => ({
  useAuth: jest.fn(() => ({ token: "coach-token" })),
}));

import * as coachApi from "@/lib/api/coach";
import CoachScoreForm from "@/components/coach/CoachScoreForm";

const mockSubmit = coachApi.submitCoachScore as jest.Mock;

const baseQuestion = {
  id: "q1",
  question_text: "Tell me about a project.",
  candidate_answer: "I led a team of five engineers...",
  order_index: 0,
  ai_scores: { clarity: 7, depth: 6, structure: 7, relevance: 8, communication_quality: 6 },
  coach_scores: null,
  feedback: null,
};

const updatedQuestion = {
  ...baseQuestion,
  coach_scores: { clarity: 9, depth: 8, structure: 9, relevance: 9, communication_quality: 8 },
};

beforeEach(() => jest.clearAllMocks());

describe("CoachScoreForm", () => {
  it("renders score inputs for all 5 dimensions", () => {
    render(
      <CoachScoreForm
        sessionId="s1"
        question={baseQuestion as never}
        onScoreSubmitted={jest.fn()}
      />,
    );
    expect(screen.getByLabelText(/clarity/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/depth/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/structure/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/relevance/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/communication/i)).toBeInTheDocument();
  });

  it("renders a submit button", () => {
    render(
      <CoachScoreForm
        sessionId="s1"
        question={baseQuestion as never}
        onScoreSubmitted={jest.fn()}
      />,
    );
    expect(screen.getByRole("button", { name: /submit score/i })).toBeInTheDocument();
  });

  it("pre-fills inputs with AI scores", () => {
    render(
      <CoachScoreForm
        sessionId="s1"
        question={baseQuestion as never}
        onScoreSubmitted={jest.fn()}
      />,
    );
    expect(screen.getByLabelText(/clarity/i)).toHaveValue(7);
  });

  it("calls submitCoachScore and onScoreSubmitted on submit", async () => {
    mockSubmit.mockResolvedValue(updatedQuestion);
    const onScoreSubmitted = jest.fn();

    render(
      <CoachScoreForm
        sessionId="s1"
        question={baseQuestion as never}
        onScoreSubmitted={onScoreSubmitted}
      />,
    );

    await userEvent.click(screen.getByRole("button", { name: /submit score/i }));

    await waitFor(() => {
      expect(mockSubmit).toHaveBeenCalledWith(
        "s1",
        "q1",
        expect.objectContaining({ scores: expect.any(Object) }),
        "coach-token",
      );
      expect(onScoreSubmitted).toHaveBeenCalledWith(updatedQuestion);
    });
  });

  it("shows error message when submission fails", async () => {
    mockSubmit.mockRejectedValue(new Error("Server error"));

    render(
      <CoachScoreForm
        sessionId="s1"
        question={baseQuestion as never}
        onScoreSubmitted={jest.fn()}
      />,
    );

    await userEvent.click(screen.getByRole("button", { name: /submit score/i }));

    await waitFor(() => {
      expect(screen.getByText(/server error/i)).toBeInTheDocument();
    });
  });

  it("shows already-scored state when coach_scores present", () => {
    render(
      <CoachScoreForm
        sessionId="s1"
        question={updatedQuestion as never}
        onScoreSubmitted={jest.fn()}
      />,
    );
    expect(screen.getByText(/coach score submitted/i)).toBeInTheDocument();
  });
});
