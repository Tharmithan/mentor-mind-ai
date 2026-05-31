import { ChartSkeleton } from "@/components/charts/ChartSkeleton";

export default function DashboardLoading() {
  return (
    <div className="space-y-6 p-2">
      <ChartSkeleton className="h-32" />
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <ChartSkeleton className="h-24" />
        <ChartSkeleton className="h-24" />
        <ChartSkeleton className="h-24" />
        <ChartSkeleton className="h-24" />
      </div>
      <ChartSkeleton className="h-72" />
    </div>
  );
}
