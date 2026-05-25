"use client";

import dynamic from "next/dynamic";
import { ChartSkeleton } from "@/components/charts/ChartSkeleton";
import type { TrendPoint } from "@/components/charts/PerformanceLineChart";
import type { StudyDay } from "@/components/charts/StudyAnalyticsChart";
import type { SubjectSlice } from "@/components/charts/WeakSubjectsPieChart";

const PerformanceLineChart = dynamic(
  () =>
    import("@/components/charts/PerformanceLineChart").then(
      (m) => m.PerformanceLineChart
    ),
  { ssr: false, loading: () => <ChartSkeleton /> }
);

const StudyAnalyticsChart = dynamic(
  () =>
    import("@/components/charts/StudyAnalyticsChart").then(
      (m) => m.StudyAnalyticsChart
    ),
  { ssr: false, loading: () => <ChartSkeleton /> }
);

const WeakSubjectsPieChart = dynamic(
  () =>
    import("@/components/charts/WeakSubjectsPieChart").then(
      (m) => m.WeakSubjectsPieChart
    ),
  { ssr: false, loading: () => <ChartSkeleton /> }
);

export function LineChartCard({ data }: { data: TrendPoint[] }) {
  return <PerformanceLineChart data={data} />;
}

export function BarChartCard({ data }: { data: StudyDay[] }) {
  return <StudyAnalyticsChart data={data} />;
}

export function PieChartCard({ data }: { data: SubjectSlice[] }) {
  return <WeakSubjectsPieChart data={data} />;
}

/** @deprecated Use LineChartCard */
export function PerformanceChart() {
  return <PerformanceLineChart />;
}

/** @deprecated Use BarChartCard */
export function StudyChart() {
  return <StudyAnalyticsChart />;
}
