"use client";

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from "chart.js";
import { Line } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
);

export type ConfidencePoint = { label: string; value: number };

const defaultData: ConfidencePoint[] = [
  { label: "W1", value: 62 },
  { label: "W2", value: 68 },
  { label: "W3", value: 72 },
  { label: "W4", value: 78 },
  { label: "W5", value: 85 },
];

export function ConfidenceTrendChart({ data = defaultData }: { data?: ConfidencePoint[] }) {
  const chartData = {
    labels: data.map((d) => d.label),
    datasets: [
      {
        label: "Model confidence",
        data: data.map((d) => d.value),
        borderColor: "#22d3ee",
        backgroundColor: "rgba(34, 211, 238, 0.12)",
        fill: true,
        tension: 0.35,
        pointRadius: 4,
        pointBackgroundColor: "#22d3ee",
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
        borderColor: "rgba(34, 211, 238, 0.3)",
        borderWidth: 1,
      },
    },
    scales: {
      x: {
        grid: { display: false },
        ticks: { color: "#94a3b8" },
      },
      y: {
        min: 50,
        max: 100,
        grid: { color: "rgba(34, 211, 238, 0.08)" },
        ticks: { color: "#94a3b8", callback: (v: number | string) => `${v}%` },
      },
    },
  };

  return (
    <div className="h-52 w-full min-h-[13rem] sm:h-56">
      <Line data={chartData} options={options} />
    </div>
  );
}
