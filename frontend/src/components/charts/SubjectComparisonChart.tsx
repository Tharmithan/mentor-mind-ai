"use client";

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Legend,
} from "chart.js";
import { Bar } from "react-chartjs-2";

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

export type SubjectPoint = { label: string; value: number };

const defaultData: SubjectPoint[] = [
  { label: "Mathematics", value: 91 },
  { label: "Programming", value: 78 },
  { label: "Data Structures", value: 62 },
];

export function SubjectComparisonChart({ data = defaultData }: { data?: SubjectPoint[] }) {
  const chartData = {
    labels: data.map((d) => d.label),
    datasets: [
      {
        label: "Score %",
        data: data.map((d) => d.value),
        backgroundColor: data.map((_, i) =>
          i === 0 ? "rgba(139, 92, 246, 0.85)" : "rgba(99, 102, 241, 0.55)"
        ),
        borderRadius: 8,
        borderSkipped: false,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: "rgba(15, 10, 30, 0.95)",
        borderColor: "rgba(139, 92, 246, 0.3)",
        borderWidth: 1,
        titleColor: "#f8fafc",
        bodyColor: "#cbd5e1",
      },
    },
    scales: {
      x: {
        grid: { display: false },
        ticks: { color: "#94a3b8", font: { size: 11 } },
      },
      y: {
        max: 100,
        grid: { color: "rgba(139, 92, 246, 0.08)" },
        ticks: { color: "#94a3b8", callback: (v: number | string) => `${v}%` },
      },
    },
  };

  return (
    <div className="h-52 w-full min-h-[13rem] sm:h-56">
      <Bar data={chartData} options={options} />
    </div>
  );
}
