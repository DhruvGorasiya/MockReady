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
        <p className="text-sm text-gray-400">No data yet — complete a session to see your trend.</p>
      </div>
    );
  }

  const data = points.map((p) => ({
    date: new Date(p.created_at).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    }),
    score: p.composite_score,
  }));

  return (
    <div data-testid="trend-chart" className="rounded-lg border border-gray-200 bg-white p-5">
      <h3 className="mb-4 text-sm font-semibold text-gray-700">
        Composite Score over time
      </h3>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={data} margin={{ top: 4, right: 8, bottom: 0, left: -16 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="date" tick={{ fontSize: 12 }} />
          <YAxis domain={[0, 10]} tick={{ fontSize: 12 }} />
          <Tooltip formatter={(value: number) => [value.toFixed(1), "Score"]} />
          <Line
            type="monotone"
            dataKey="score"
            stroke="#6366f1"
            strokeWidth={2}
            dot={{ r: 4 }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
