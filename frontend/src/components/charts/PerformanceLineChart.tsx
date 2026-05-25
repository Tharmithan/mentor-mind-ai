"use client";

import {
  CartesianGrid,
  Line,
  LineChart,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { ChartContainer } from "./ChartContainer";

export type TrendPoint = {
  label: string;
  value: number;
};

const defaultData: TrendPoint[] = [
  { label: "W1", value: 68 },
  { label: "W2", value: 72 },
  { label: "W3", value: 75 },
  { label: "W4", value: 78 },
  { label: "W5", value: 82 },
];

export function PerformanceLineChart({
  data = defaultData,
}: {
  data?: TrendPoint[];
}) {
  return (
    <ChartContainer className="h-52 w-full min-h-[13rem] sm:h-56">
      {(size) => (
        <LineChart
          width={size.width}
          height={size.height}
          data={data}
          margin={{ top: 8, right: 12, left: -16, bottom: 0 }}
        >
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="rgba(139,92,246,0.1)"
            vertical={false}
          />
          <XAxis
            dataKey="label"
            tick={{ fill: "#94a3b8", fontSize: 12 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            domain={["dataMin - 5", "dataMax + 5"]}
            tick={{ fill: "#94a3b8", fontSize: 12 }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v) => `${v}%`}
          />
          <Tooltip
            contentStyle={{
              background: "rgba(15, 10, 30, 0.95)",
              border: "1px solid rgba(139, 92, 246, 0.3)",
              borderRadius: "12px",
              color: "#f8fafc",
            }}
            formatter={(value) => [`${value}%`, "Performance"]}
          />
          <Line
            type="monotone"
            dataKey="value"
            stroke="#8b5cf6"
            strokeWidth={2.5}
            dot={{ fill: "#8b5cf6", r: 4, strokeWidth: 0 }}
            activeDot={{ r: 6, fill: "#a78bfa" }}
            animationDuration={800}
          />
        </LineChart>
      )}
    </ChartContainer>
  );
}
