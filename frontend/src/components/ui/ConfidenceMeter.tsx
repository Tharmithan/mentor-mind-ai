type ConfidenceMeterProps = {
  value: number;
  label?: string;
};

export function ConfidenceMeter({
  value,
  label = "Confidence",
}: ConfidenceMeterProps) {
  const color =
    value >= 70
      ? "from-emerald-500 to-teal-400"
      : value >= 40
        ? "from-amber-500 to-orange-400"
        : "from-rose-500 to-red-400";

  return (
    <div className="w-full">
      <div className="mb-2 flex items-center justify-between">
        <span className="text-sm font-medium text-slate-300">{label}</span>
        <span className="text-sm font-bold text-white">{value}%</span>
      </div>
      <div className="h-3 overflow-hidden rounded-full bg-slate-800">
        <div
          className={`h-full rounded-full bg-gradient-to-r ${color} transition-all duration-500 shadow-lg`}
          style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
        />
      </div>
      <div className="mt-1 flex justify-between text-[10px] text-slate-500">
        <span>Low</span>
        <span>Medium</span>
        <span>High</span>
      </div>
    </div>
  );
}
