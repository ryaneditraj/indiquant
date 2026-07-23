"use client";

import {
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export function EquityChart({
  data,
}: {
  data: Array<{ ts?: string; equity: number }>;
}) {
  if (!data?.length) {
    return <p className="text-sm text-ink-muted">No equity curve yet.</p>;
  }
  const chartData = data.map((d, i) => ({
    i,
    equity: Number(d.equity),
    ts: d.ts ? String(d.ts).slice(0, 10) : String(i),
  }));

  return (
    <div className="h-56 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <XAxis dataKey="ts" hide />
          <YAxis
            domain={["auto", "auto"]}
            tick={{ fill: "#8b9aab", fontSize: 10 }}
            width={64}
          />
          <Tooltip
            contentStyle={{
              background: "#121820",
              border: "1px solid #1e2a36",
              borderRadius: 8,
              fontSize: 12,
            }}
          />
          <Line
            type="monotone"
            dataKey="equity"
            stroke="#3d9bfd"
            strokeWidth={2}
            dot={false}
            isAnimationActive
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
