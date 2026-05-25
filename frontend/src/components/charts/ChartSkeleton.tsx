export function ChartSkeleton({ className = "h-52" }: { className?: string }) {
  return (
    <div
      className={`${className} w-full animate-pulse rounded-xl bg-slate-800/50`}
      aria-hidden
    />
  );
}
