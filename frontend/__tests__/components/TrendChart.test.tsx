import { render, screen } from "@testing-library/react";
import TrendChart from "@/components/session/TrendChart";
import type { TrendPoint } from "@/lib/types/session";

// recharts uses ResizeObserver and SVG — stub both for jsdom
global.ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
};

function makePoint(index: number): TrendPoint {
  return {
    session_id: `session-${index}`,
    created_at: `2026-01-${String(index + 1).padStart(2, "0")}T10:00:00Z`,
    composite_score: 5 + index * 0.5,
    dimension_scores: {
      clarity: 7,
      depth: 7,
      structure: 7,
      relevance: 7,
      communication_quality: 7,
    },
  };
}

describe("TrendChart", () => {
  it("renders without crashing with 0 data points", () => {
    render(<TrendChart points={[]} />);
    expect(screen.getByText(/no data/i)).toBeInTheDocument();
  });

  it("renders a chart container when data points are present", () => {
    const points = Array.from({ length: 10 }, (_, i) => makePoint(i));
    render(<TrendChart points={points} />);
    // ResponsiveContainer doesn't render SVG in jsdom (no layout dimensions),
    // so assert on the named wrapper instead
    expect(screen.getByTestId("trend-chart")).toBeInTheDocument();
  });

  it("renders a heading label", () => {
    const points = [makePoint(0)];
    render(<TrendChart points={points} />);
    expect(screen.getByText(/composite score/i)).toBeInTheDocument();
  });
});
