"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const tooltipStyle = {
  background: "#0a1224",
  border: "1px solid #1a2744",
  borderRadius: 8,
  fontSize: 12,
};

export function TrendsDualLine({
  brand,
  transactional,
}: {
  brand: Array<{ date: string; interest: number }>;
  transactional: Array<{ date: string; interest: number }>;
}) {
  const byDate = new Map<string, { date: string; brand?: number; transactional?: number }>();
  for (const p of brand) {
    byDate.set(p.date, { date: p.date, brand: p.interest, ...(byDate.get(p.date) || {}) });
  }
  for (const p of transactional) {
    const cur = byDate.get(p.date) || { date: p.date };
    cur.transactional = p.interest;
    byDate.set(p.date, cur);
  }
  const data = Array.from(byDate.values()).sort((a, b) => a.date.localeCompare(b.date));
  if (!data.length) {
    return <p className="text-sm text-ink-muted">No interest series yet.</p>;
  }
  return (
    <div className="h-56 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid stroke="#1a2744" strokeDasharray="3 3" />
          <XAxis dataKey="date" hide />
          <YAxis domain={[0, 100]} tick={{ fill: "#8b9aab", fontSize: 10 }} width={36} />
          <Tooltip contentStyle={tooltipStyle} />
          <Legend />
          <Line type="monotone" dataKey="brand" name="Brand" stroke="#3dff9a" strokeWidth={2} dot={false} />
          <Line
            type="monotone"
            dataKey="transactional"
            name="Transactional"
            stroke="#22d3ee"
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
      <p className="mt-1 text-[10px] text-ink-faint">Relative 0–100 index within shared window — not absolute volume.</p>
    </div>
  );
}

export function RegionHeatBars({
  regions,
}: {
  regions: Array<{ region: string; interest: number }>;
}) {
  if (!regions?.length) {
    return <p className="text-sm text-ink-muted">No regional data.</p>;
  }
  const data = regions.slice(0, 12);
  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="vertical" margin={{ left: 8, right: 8 }}>
          <XAxis type="number" domain={[0, 100]} tick={{ fill: "#8b9aab", fontSize: 10 }} />
          <YAxis
            type="category"
            dataKey="region"
            width={110}
            tick={{ fill: "#8b9dc3", fontSize: 10 }}
          />
          <Tooltip contentStyle={tooltipStyle} />
          <Bar dataKey="interest" name="Relative interest" fill="#22d3ee" radius={[0, 4, 4, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function ComponentBars({
  components,
}: {
  components: Record<string, number>;
}) {
  const data = Object.entries(components).map(([k, v]) => ({
    name: k.replace(/_/g, " "),
    value: Math.round(Number(v) * 100),
  }));
  return (
    <div className="h-48 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <XAxis dataKey="name" tick={{ fill: "#8b9aab", fontSize: 9 }} interval={0} angle={-20} textAnchor="end" height={50} />
          <YAxis domain={[0, 100]} tick={{ fill: "#8b9aab", fontSize: 10 }} width={32} />
          <Tooltip contentStyle={tooltipStyle} />
          <Bar dataKey="value" fill="#3dff9a" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
