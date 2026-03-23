import { render, screen } from "@testing-library/react";
import DimensionBreakdown from "@/components/session/DimensionBreakdown";
import type { DimensionScores } from "@/lib/types/session";

const aiScores: DimensionScores = {
  clarity: 6,
  depth: 7,
  structure: 5,
  relevance: 8,
  communication_quality: 4,
};

const coachScores: DimensionScores = {
  clarity: 9,
  depth: 8,
  structure: 7,
  relevance: 9,
  communication_quality: 8,
};

describe("DimensionBreakdown", () => {
  it("renders all 5 dimension labels", () => {
    render(<DimensionBreakdown aiScores={aiScores} coachScores={null} />);
    expect(screen.getByText(/clarity/i)).toBeInTheDocument();
    expect(screen.getByText(/depth/i)).toBeInTheDocument();
    expect(screen.getByText(/structure/i)).toBeInTheDocument();
    expect(screen.getByText(/relevance/i)).toBeInTheDocument();
    expect(screen.getByText(/communication/i)).toBeInTheDocument();
  });

  it("renders all 5 AI dimension scores", () => {
    render(<DimensionBreakdown aiScores={aiScores} coachScores={null} />);
    expect(screen.getByText("6")).toBeInTheDocument(); // clarity
    expect(screen.getByText("7")).toBeInTheDocument(); // depth
    expect(screen.getByText("5")).toBeInTheDocument(); // structure
    expect(screen.getByText("8")).toBeInTheDocument(); // relevance
    expect(screen.getByText("4")).toBeInTheDocument(); // communication_quality
  });

  it("shows coach scores when present", () => {
    render(
      <DimensionBreakdown aiScores={aiScores} coachScores={coachScores} />,
    );
    // Coach scores include 9 for clarity and relevance — at least one should appear
    const nines = screen.getAllByText("9");
    expect(nines.length).toBeGreaterThan(0);
  });

  it("marks coach score as authoritative with a label", () => {
    render(
      <DimensionBreakdown aiScores={aiScores} coachScores={coachScores} />,
    );
    expect(screen.getByText(/coach/i)).toBeInTheDocument();
  });

  it("does not show coach label when coach scores are absent", () => {
    render(<DimensionBreakdown aiScores={aiScores} coachScores={null} />);
    expect(screen.queryByText(/coach/i)).not.toBeInTheDocument();
  });
});
