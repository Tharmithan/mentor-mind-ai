"use client";

import { useEffect, useRef, useState } from "react";

type ChartSize = { width: number; height: number };

export function ChartContainer({
  children,
  className = "h-52 w-full min-h-[13rem]",
}: {
  children: (size: ChartSize) => React.ReactNode;
  className?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [size, setSize] = useState<ChartSize>({ width: 0, height: 0 });

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const update = () => {
      const { width, height } = el.getBoundingClientRect();
      if (width > 0 && height > 0) {
        setSize({
          width: Math.floor(width),
          height: Math.floor(height),
        });
      }
    };

    update();
    const observer = new ResizeObserver(update);
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  return (
    <div ref={ref} className={`min-w-0 ${className}`}>
      {size.width > 0 && size.height > 0 ? children(size) : null}
    </div>
  );
}
