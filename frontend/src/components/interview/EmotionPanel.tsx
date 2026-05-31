"use client";

import { Eye, Smile, Brain, Zap, Activity, type LucideIcon } from "lucide-react";
import { ConfidenceMeter } from "@/components/ui/ConfidenceMeter";
import type { EmotionSnapshot } from "@/lib/emotion/types";

type EmotionPanelProps = {
  snapshot: EmotionSnapshot;
  ready: boolean;
  live?: boolean;
};

function MiniBar({
  label,
  value,
  icon: Icon,
  invert = false,
}: {
  label: string;
  value: number;
  icon: LucideIcon;
  invert?: boolean;
}) {
  const v = invert ? 100 - value : value;
  const color =
    v >= 70 ? "bg-emerald-500" : v >= 40 ? "bg-amber-500" : "bg-rose-500";
  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-[10px]">
        <span className="flex items-center gap-1 text-slate-400">
          <Icon className="h-3 w-3" />
          {label}
        </span>
        <span className="font-medium text-slate-300">{value}%</span>
      </div>
      <div className="h-1.5 overflow-hidden rounded-full bg-slate-800">
        <div className={`h-full rounded-full ${color} transition-all duration-300`} style={{ width: `${value}%` }} />
      </div>
    </div>
  );
}

export function EmotionPanel({ snapshot, ready, live = true }: EmotionPanelProps) {
  const emotionColors: Record<string, string> = {
    happy: "text-emerald-400",
    neutral: "text-slate-400",
    sad: "text-blue-400",
    angry: "text-red-400",
    fear: "text-purple-400",
    surprise: "text-amber-400",
    disgust: "text-lime-400",
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <ConfidenceMeter value={snapshot.confidence} label={live ? "Live confidence" : "Confidence"} />
        {live && (
          <span
            className={`ml-2 shrink-0 rounded-full px-2 py-0.5 text-[10px] ${
              ready && snapshot.faceDetected
                ? "bg-emerald-500/20 text-emerald-400"
                : "bg-slate-700 text-slate-400"
            }`}
          >
            {ready ? (snapshot.faceDetected ? "Tracking" : "No face") : "Loading…"}
          </span>
        )}
      </div>

      <div className="grid grid-cols-2 gap-3">
        <MiniBar label="Stress" value={snapshot.stress} icon={Zap} invert />
        <MiniBar label="Nervousness" value={snapshot.nervousness} icon={Activity} invert />
        <MiniBar label="Engagement" value={snapshot.engagement} icon={Brain} />
        <MiniBar label="Attention" value={snapshot.attention} icon={Eye} />
      </div>

      <div className="flex flex-wrap gap-2 text-[10px]">
        <span
          className={`rounded-full bg-white/5 px-2 py-1 capitalize ${emotionColors[snapshot.dominantEmotion] ?? "text-slate-400"}`}
        >
          {snapshot.dominantEmotion}
        </span>
        <span className="rounded-full bg-white/5 px-2 py-1 text-slate-400">
          <Eye className="mr-1 inline h-3 w-3" />
          Eye contact {snapshot.eyeContact}%
        </span>
        <span
          className={`rounded-full px-2 py-1 ${
            snapshot.smile > 40 ? "bg-emerald-500/15 text-emerald-400" : "bg-white/5 text-slate-400"
          }`}
        >
          <Smile className="mr-1 inline h-3 w-3" />
          {snapshot.smile > 40 ? "Smiling" : "Neutral face"}
        </span>
        {snapshot.voiceActive && (
          <span className="rounded-full bg-violet-500/15 px-2 py-1 text-violet-300">Voice active</span>
        )}
      </div>
    </div>
  );
}
