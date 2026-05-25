"use client";

import { Area, AreaChart, Tooltip, XAxis, YAxis } from "recharts";
import { ChartContainer } from "./ChartContainer";

const trendData = [
  { week: "W1", score: 68 },
  { week: "W2", score: 72 },
  { week: "W3", score: 75 },
  { week: "W4", score: 78 },
  { week: "W5", score: 82 },
];

export function PerformanceTrendChart() {
  return (
    <ChartContainer className="h-32 w-full min-h-[8rem]">
      {(size) => (
        <AreaChart
          width={size.width}
          height={size.height}
          data={trendData}
          margin={{ top: 4, right: 4, left: -25, bottom: 0 }}
        >
          <defs>
            <linearGradient id="performanceAreaGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#8b5cf6" stopOpacity={0.4} />
              <stop offset="100%" stopColor="#3b82f6" stopOpacity={0} />
            </linearGradient>
          </defs>
          <XAxis
            dataKey="week"
            tick={{ fill: "#64748b", fontSize: 10 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis hide domain={[60, 90]} />
          <Tooltip
            contentStyle={{
              background: "rgba(15, 10, 30, 0.95)",
              border: "1px solid rgba(139, 92, 246, 0.3)",
              borderRadius: "8px",
              fontSize: "12px",
            }}
            formatter={(value) => [`${value}%`, "Score"]}
          />
          <Area
            type="monotone"
            dataKey="score"
            stroke="#8b5cf6"
            strokeWidth={2}
            fill="url(#performanceAreaGradient)"
            animationDuration={1000}
          />
        </AreaChart>
      )}
    </ChartContainer>
  );
}
