"use client";

import { useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/Button";
import { GlassCard } from "@/components/ui/GlassCard";
import { ConfidenceMeter } from "@/components/ui/ConfidenceMeter";
import { AnimatedSection } from "@/components/ui/AnimatedSection";
import { Video, Mic, MicOff, Send, Bot, User } from "lucide-react";

type Message = {
  role: "ai" | "user";
  text: string;
};

const INITIAL_MESSAGES: Message[] = [
  {
    role: "ai",
    text: "Welcome to your mock interview! I'm your AI interviewer. Tell me about yourself and a project you're proud of.",
  },
];

export function InterviewRoom() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [micOn, setMicOn] = useState(false);
  const [cameraOn, setCameraOn] = useState(false);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [confidence, setConfidence] = useState(72);
  const [messages, setMessages] = useState<Message[]>(INITIAL_MESSAGES);
  const [input, setInput] = useState("");

  useEffect(() => {
    let stream: MediaStream | null = null;

    async function startCamera() {
      if (!cameraOn) return;
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: false,
        });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
        setCameraError(null);
      } catch {
        setCameraError("Camera access denied — enable permissions to use webcam.");
        setCameraOn(false);
      }
    }

    startCamera();
    return () => stream?.getTracks().forEach((t) => t.stop());
  }, [cameraOn]);

  useEffect(() => {
    if (!micOn) return;
    const interval = setInterval(() => {
      setConfidence((c) =>
        Math.min(95, Math.max(35, c + (Math.random() > 0.5 ? 3 : -2)))
      );
    }, 2000);
    return () => clearInterval(interval);
  }, [micOn]);

  function handleSend() {
    if (!input.trim()) return;
    setMessages((m) => [
      ...m,
      { role: "user", text: input.trim() },
      {
        role: "ai",
        text: "Great answer! You structured your response well. Can you elaborate on the technical challenges you faced?",
      },
    ]);
    setInput("");
  }

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      <AnimatedSection className="space-y-4 lg:col-span-1">
        <GlassCard className="overflow-hidden p-0" hover={false}>
          <div className="relative aspect-[4/3] bg-slate-900">
            {cameraOn && !cameraError ? (
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="h-full w-full object-cover"
              />
            ) : (
              <div className="flex h-full flex-col items-center justify-center gap-3 p-6 text-center">
                <div className="flex h-20 w-20 items-center justify-center rounded-full bg-violet-500/20 ring-2 ring-violet-500/30">
                  <Video className="h-10 w-10 text-violet-400" />
                </div>
                <p className="text-sm text-slate-400">
                  {cameraError ?? "Webcam preview — turn on camera to start"}
                </p>
              </div>
            )}
            <div className="absolute bottom-3 left-0 right-0 flex items-center justify-center gap-4">
              <button
                type="button"
                onClick={() => setCameraOn(!cameraOn)}
                className={`flex h-12 w-12 items-center justify-center rounded-full transition-all duration-200 ${
                  cameraOn
                    ? "bg-violet-600 text-white shadow-lg shadow-violet-500/40"
                    : "bg-slate-800/90 text-slate-400 hover:bg-slate-700"
                }`}
                aria-label="Toggle camera"
              >
                <Video className="h-5 w-5" />
              </button>
              <button
                type="button"
                onClick={() => setMicOn(!micOn)}
                className={`flex h-14 w-14 items-center justify-center rounded-full transition-all duration-200 ${
                  micOn
                    ? "animate-pulse-glow bg-gradient-to-r from-violet-600 to-blue-600 text-white"
                    : "bg-slate-800/90 text-slate-400 hover:bg-slate-700"
                }`}
                aria-label="Toggle microphone"
              >
                {micOn ? <Mic className="h-6 w-6" /> : <MicOff className="h-6 w-6" />}
              </button>
            </div>
          </div>
        </GlassCard>

        <GlassCard className="p-5">
          <ConfidenceMeter value={confidence} label="Live Confidence" />
          <p className="mt-3 text-xs text-slate-500">
            {micOn
              ? "Analyzing speech & facial cues (demo)"
              : "Enable mic for live confidence tracking"}
          </p>
        </GlassCard>

        <div className="grid grid-cols-2 gap-3">
          {[
            { label: "Communication", value: "4.2" },
            { label: "Technical", value: "3.8" },
          ].map((s) => (
            <GlassCard key={s.label} className="p-4 text-center" hover={false}>
              <p className="text-xs text-slate-500">{s.label}</p>
              <p className="text-lg font-bold text-white">{s.value}</p>
            </GlassCard>
          ))}
        </div>
      </AnimatedSection>

      <AnimatedSection delay={150} className="lg:col-span-2">
        <GlassCard className="flex min-h-[520px] flex-col overflow-hidden p-0" hover={false}>
          <div className="flex items-center justify-between border-b border-violet-500/10 px-5 py-4">
            <div>
              <h2 className="font-semibold text-white">AI Interviewer</h2>
              <p className="text-xs text-slate-500">Technical · Behavioral mode</p>
            </div>
            <span className="flex items-center gap-1.5 rounded-full bg-emerald-500/10 px-3 py-1 text-xs text-emerald-400 ring-1 ring-emerald-500/20">
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-400" />
              Live
            </span>
          </div>

          <div className="max-h-[380px] flex-1 space-y-4 overflow-y-auto p-5">
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`flex gap-2 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                {msg.role === "ai" && (
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-violet-500/20">
                    <Bot className="h-4 w-4 text-violet-400" />
                  </div>
                )}
                <div
                  className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm transition-all duration-300 ${
                    msg.role === "ai"
                      ? "bg-violet-500/10 text-slate-200 ring-1 ring-violet-500/20"
                      : "bg-blue-600/20 text-white ring-1 ring-blue-500/20"
                  }`}
                >
                  {msg.text}
                </div>
                {msg.role === "user" && (
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-blue-500/20">
                    <User className="h-4 w-4 text-blue-400" />
                  </div>
                )}
              </div>
            ))}
          </div>

          <div className="border-t border-violet-500/10 p-4">
            <div className="flex gap-3">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSend()}
                placeholder="Type your answer or use the mic..."
                className="flex-1 rounded-xl border border-violet-500/20 bg-slate-900/80 px-4 py-3 text-sm text-white placeholder:text-slate-500 transition focus:border-violet-500/50 focus:outline-none focus:ring-1 focus:ring-violet-500/30"
              />
              <Button variant="gradient" onClick={handleSend}>
                <Send className="h-4 w-4" />
                Send
              </Button>
            </div>
          </div>
        </GlassCard>
      </AnimatedSection>
    </div>
  );
}
