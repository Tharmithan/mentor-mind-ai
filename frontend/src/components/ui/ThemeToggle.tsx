"use client";

import { Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import { useEffect, useState } from "react";

export function ThemeToggle({ compact = false }: { compact?: boolean }) {
  const { theme, setTheme, resolvedTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);

  if (!mounted) {
    return (
      <button
        type="button"
        aria-label="Toggle theme"
        className="rounded-lg p-2 text-slate-400"
        disabled
      />
    );
  }

  const isDark = (theme === "system" ? resolvedTheme : theme) !== "light";

  return (
    <button
      type="button"
      aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
      onClick={() => setTheme(isDark ? "light" : "dark")}
      className={`rounded-lg border border-violet-500/20 bg-background/50 text-slate-400 transition hover:border-violet-500/40 hover:text-violet-300 ${
        compact ? "p-2" : "flex items-center gap-2 px-3 py-2 text-sm"
      }`}
    >
      {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
      {!compact && <span>{isDark ? "Light" : "Dark"}</span>}
    </button>
  );
}
