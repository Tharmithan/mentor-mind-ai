"use client";

import dynamic from "next/dynamic";
import { ChartSkeleton } from "@/components/charts/ChartSkeleton";

const StudyAnalyticsChart = dynamic(
  () =>
    import("@/components/charts/StudyAnalyticsChart").then(
      (m) => m.StudyAnalyticsChart
    ),
  { ssr: false, loading: () => <ChartSkeleton /> }
);

const PerformanceTrendChart = dynamic(
  () =>
    import("@/components/charts/PerformanceTrendChart").then(
      (m) => m.PerformanceTrendChart
    ),
  { ssr: false, loading: () => <ChartSkeleton className="h-32" /> }
);

export function StudyChart() {
  return <StudyAnalyticsChart />;
}

export function PerformanceChart() {
  return <PerformanceTrendChart />;
}
