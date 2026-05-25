"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { ChartContainer } from "./ChartContainer";

export type StudyDay = {
  day: string;
  hours: number;
};

const defaultData: StudyDay[] = [
  { day: "Mon", hours: 2.5 },
  { day: "Tue", hours: 4 },
  { day: "Wed", hours: 3 },
  { day: "Thu", hours: 5 },
  { day: "Fri", hours: 3.5 },
  { day: "Sat", hours: 6 },
  { day: "Sun", hours: 4.5 },
];

export function StudyAnalyticsChart({ data = defaultData }: { data?: StudyDay[] }) {
  return (
    <ChartContainer className="h-52 w-full min-h-[13rem] sm:h-56">
      {(size) => (
        <BarChart
          width={size.width}
          height={size.height}
          data={data}
          margin={{ top: 8, right: 8, left: -20, bottom: 0 }}
        >
          <defs>
            <linearGradient id="studyBarGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#8b5cf6" />
              <stop offset="100%" stopColor="#3b82f6" />
            </linearGradient>
          </defs>
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="rgba(139,92,246,0.1)"
            vertical={false}
          />
          <XAxis
            dataKey="day"
            tick={{ fill: "#94a3b8", fontSize: 12 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: "#94a3b8", fontSize: 12 }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip
            contentStyle={{
              background: "rgba(15, 10, 30, 0.95)",
              border: "1px solid rgba(139, 92, 246, 0.3)",
              borderRadius: "12px",
              color: "#f8fafc",
            }}
            formatter={(value) => [`${value}h`, "Study hours"]}
            cursor={{ fill: "rgba(139, 92, 246, 0.1)" }}
          />
          <Bar
            dataKey="hours"
            fill="url(#studyBarGradient)"
            radius={[6, 6, 0, 0]}
            animationDuration={800}
            animationEasing="ease-out"
          />
        </BarChart>
      )}
    </ChartContainer>
  );
}
