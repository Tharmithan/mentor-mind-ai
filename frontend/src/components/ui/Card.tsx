type CardProps = {
  title: string;
  description: string;
  icon?: React.ReactNode;
  className?: string;
};

export function Card({ title, description, icon, className = "" }: CardProps) {
  return (
    <div
      className={`group glass rounded-2xl p-6 transition duration-300 hover:border-violet-500/40 hover:shadow-lg hover:shadow-violet-500/10 ${className}`}
    >
      {icon && (
        <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-violet-600/30 to-blue-600/30 text-violet-300 ring-1 ring-violet-500/20">
          {icon}
        </div>
      )}
      <h3 className="text-lg font-semibold text-white group-hover:text-violet-200 transition-colors">
        {title}
      </h3>
      <p className="mt-2 text-sm leading-relaxed text-slate-400">{description}</p>
    </div>
  );
}

export function StatCard({
  label,
  value,
  sub,
  trend,
  icon,
}: {
  label: string;
  value: string;
  sub?: string;
  trend?: "up" | "down" | "neutral";
  icon?: React.ReactNode;
}) {
  const trendColor =
    trend === "up"
      ? "text-emerald-400"
      : trend === "down"
        ? "text-rose-400"
        : "text-violet-300";

  return (
    <div className="glass rounded-2xl p-5 transition hover:shadow-lg hover:shadow-violet-500/5">
      <div className="flex items-start justify-between">
        <p className="text-sm font-medium text-slate-400">{label}</p>
        {icon && (
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-violet-500/15 text-violet-400">
            {icon}
          </div>
        )}
      </div>
      <p className="mt-2 text-3xl font-bold tracking-tight text-white">{value}</p>
      {sub && <p className={`mt-1 text-xs font-medium ${trendColor}`}>{sub}</p>}
    </div>
  );
}
