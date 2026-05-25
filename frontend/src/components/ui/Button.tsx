import Link from "next/link";

type ButtonVariant = "primary" | "secondary" | "ghost";

const variants: Record<ButtonVariant, string> = {
  primary:
    "bg-indigo-500 hover:bg-indigo-600 text-white shadow-lg shadow-indigo-500/25",
  secondary:
    "border border-slate-700 bg-slate-900 hover:bg-slate-800 text-slate-100",
  ghost: "text-slate-300 hover:text-white hover:bg-slate-800/50",
};

type ButtonProps = {
  children: React.ReactNode;
  variant?: ButtonVariant;
  href?: string;
  className?: string;
  onClick?: () => void;
};

export function Button({
  children,
  variant = "primary",
  href,
  className = "",
  onClick,
}: ButtonProps) {
  const base =
    "inline-flex items-center justify-center rounded-lg px-5 py-2.5 text-sm font-medium transition-colors";

  const classes = `${base} ${variants[variant]} ${className}`;

  if (href) {
    return (
      <Link href={href} className={classes}>
        {children}
      </Link>
    );
  }

  return (
    <button type="button" onClick={onClick} className={classes}>
      {children}
    </button>
  );
}
