"use client";

import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { TrendPoint } from "@/lib/types/session";

interface Props {
  points: TrendPoint[];
}

export default function TrendChart({ points }: Props) {
  if (points.length === 0) {
    return (
      <div className="flex h-48 items-center justify-center rounded-lg border border-gray-200 bg-white">
        <p className="text-sm text-gray-400">
          No data yet — complete a session to see your trend.
        </p>
      </div>
    );
  }

  const data = points.map((p) => ({
    date: new Date(p.created_at).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    }),
    score: p.composite_score,
    clarity: p.dimension_scores.clarity,
    depth: p.dimension_scores.depth,
    structure: p.dimension_scores.structure,
    relevance: p.dimension_scores.relevance,
    communication: p.dimension_scores.communication_quality,
  }));

  const DIMENSIONS = [
    { key: "clarity", label: "Clarity", color: "#10b981" },
    { key: "depth", label: "Depth", color: "#f59e0b" },
    { key: "structure", label: "Structure", color: "#ef4444" },
    { key: "relevance", label: "Relevance", color: "#8b5cf6" },
    { key: "communication", label: "Communication", color: "#06b6d4" },
  ] as const;

  return (
    <div
      data-testid="trend-chart"
      className="rounded-lg border border-gray-200 bg-white p-5"
    >
      <h3 className="mb-3 text-sm font-semibold text-gray-700">
        Composite Score over time
      </h3>
      {/* Static legend — readable in jsdom tests and visually consistent */}
      <div className="mb-4 flex flex-wrap gap-x-4 gap-y-1">
        <span className="flex items-center gap-1 text-xs text-gray-600">
          <span
            className="inline-block h-2 w-4 rounded"
            style={{ backgroundColor: "#6366f1" }}
          />
          Composite Score
        </span>
        {DIMENSIONS.map((d) => (
          <span
            key={d.key}
            className="flex items-center gap-1 text-xs text-gray-500"
          >
            <span
              className="inline-block h-px w-4"
              style={{
                backgroundColor: d.color,
                borderTop: `2px dashed ${d.color}`,
              }}
            />
            {d.label}
          </span>
        ))}
      </div>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart
          data={data}
          margin={{ top: 4, right: 8, bottom: 0, left: -16 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="date" tick={{ fontSize: 12 }} />
          <YAxis domain={[0, 10]} tick={{ fontSize: 12 }} />
          <Tooltip formatter={(value: number) => [value.toFixed(1), ""]} />
          <Line
            type="monotone"
            dataKey="score"
            stroke="#6366f1"
            strokeWidth={2}
            dot={{ r: 3 }}
            activeDot={{ r: 5 }}
          />
          {DIMENSIONS.map((d) => (
            <Line
              key={d.key}
              type="monotone"
              dataKey={d.key}
              stroke={d.color}
              strokeWidth={1}
              dot={false}
              strokeDasharray="4 2"
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
