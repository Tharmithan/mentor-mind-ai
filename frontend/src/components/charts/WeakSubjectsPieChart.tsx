"use client";

import { Cell, Pie, PieChart, Tooltip, Legend } from "recharts";
import { ChartContainer } from "./ChartContainer";

export type SubjectSlice = {
  label: string;
  value: number;
};

const COLORS = ["#8b5cf6", "#6366f1", "#3b82f6", "#22d3ee", "#f59e0b", "#f43f5e"];

const defaultData: SubjectSlice[] = [
  { label: "Mathematics", value: 91 },
  { label: "Programming", value: 78 },
  { label: "Data Structures", value: 62 },
];

export function WeakSubjectsPieChart({
  data = defaultData,
}: {
  data?: SubjectSlice[];
}) {
  return (
    <ChartContainer className="h-52 w-full min-h-[13rem] sm:h-56">
      {(size) => (
        <PieChart width={size.width} height={size.height}>
          <Pie
            data={data}
            dataKey="value"
            nameKey="label"
            cx="50%"
            cy="45%"
            innerRadius={48}
            outerRadius={72}
            paddingAngle={3}
            animationDuration={800}
          >
            {data.map((_, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              background: "rgba(15, 10, 30, 0.95)",
              border: "1px solid rgba(139, 92, 246, 0.3)",
              borderRadius: "12px",
              color: "#f8fafc",
            }}
            formatter={(value, name) => [`${value}%`, name]}
          />
          <Legend
            verticalAlign="bottom"
            iconType="circle"
            iconSize={8}
            formatter={(value) => (
              <span className="text-xs text-slate-400">{value}</span>
            )}
          />
        </PieChart>
      )}
    </ChartContainer>
  );
}
