type CardProps = {
  title: string;
  description: string;
  icon?: React.ReactNode;
  className?: string;
};

export function Card({ title, description, icon, className = "" }: CardProps) {
  return (
    <div
      className={`rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur transition hover:border-indigo-500/40 hover:bg-slate-900 ${className}`}
    >
      {icon && (
        <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-500/20 text-indigo-400">
          {icon}
        </div>
      )}
      <h3 className="text-lg font-semibold text-white">{title}</h3>
      <p className="mt-2 text-sm leading-relaxed text-slate-400">{description}</p>
    </div>
  );
}

export function StatCard({
  label,
  value,
  sub,
}: {
  label: string;
  value: string;
  sub?: string;
}) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5">
      <p className="text-sm text-slate-400">{label}</p>
      <p className="mt-1 text-2xl font-bold text-white">{value}</p>
      {sub && <p className="mt-1 text-xs text-emerald-400">{sub}</p>}
    </div>
  );
}
