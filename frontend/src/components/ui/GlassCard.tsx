type GlassCardProps = {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
};

export function GlassCard({
  children,
  className = "",
  hover = true,
}: GlassCardProps) {
  return (
    <div
      className={`glass rounded-2xl ${
        hover
          ? "transition duration-300 hover:border-violet-500/30 hover:shadow-lg hover:shadow-violet-500/5"
          : ""
      } ${className}`}
    >
      {children}
    </div>
  );
}
