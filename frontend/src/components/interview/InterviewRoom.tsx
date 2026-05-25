"use client";

import { useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/Button";
import { ConfidenceMeter } from "@/components/ui/ConfidenceMeter";

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

    return () => {
      stream?.getTracks().forEach((t) => t.stop());
    };
  }, [cameraOn]);

  useEffect(() => {
    if (!micOn) return;
    const interval = setInterval(() => {
      setConfidence((c) => Math.min(95, Math.max(35, c + (Math.random() > 0.5 ? 3 : -2))));
    }, 2000);
    return () => clearInterval(interval);
  }, [micOn]);

  function handleSend() {
    if (!input.trim()) return;
    const userText = input.trim();
    setMessages((m) => [
      ...m,
      { role: "user", text: userText },
      {
        role: "ai",
        text: "Great answer! You structured your response well. Can you elaborate on the technical challenges you faced?",
      },
    ]);
    setInput("");
  }

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      {/* Webcam + controls */}
      <div className="lg:col-span-1 space-y-4">
        <div className="glass overflow-hidden rounded-2xl">
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
                  <svg
                    className="h-10 w-10 text-violet-400"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={1.5}
                      d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
                    />
                  </svg>
                </div>
                <p className="text-sm text-slate-400">
                  {cameraError ?? "Webcam preview — turn on camera to start"}
                </p>
              </div>
            )}
            <div className="absolute bottom-3 left-3 right-3 flex items-center justify-center gap-3">
              <button
                type="button"
                onClick={() => setCameraOn(!cameraOn)}
                className={`flex h-12 w-12 items-center justify-center rounded-full transition ${
                  cameraOn
                    ? "bg-violet-600 text-white shadow-lg shadow-violet-500/40"
                    : "bg-slate-800 text-slate-400 hover:bg-slate-700"
                }`}
                aria-label="Toggle camera"
              >
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
              </button>
              <button
                type="button"
                onClick={() => setMicOn(!micOn)}
                className={`flex h-14 w-14 items-center justify-center rounded-full transition ${
                  micOn
                    ? "bg-gradient-to-r from-violet-600 to-blue-600 text-white shadow-xl shadow-violet-500/50 animate-pulse-glow"
                    : "bg-slate-800 text-slate-400 hover:bg-slate-700"
                }`}
                aria-label="Toggle microphone"
              >
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        <div className="glass rounded-2xl p-5">
          <ConfidenceMeter value={confidence} label="Live Confidence" />
          <p className="mt-3 text-xs text-slate-500">
            {micOn
              ? "Analyzing speech patterns & facial cues (demo)"
              : "Enable mic for live confidence tracking"}
          </p>
        </div>

        <div className="grid grid-cols-2 gap-3 text-center">
          <div className="glass rounded-xl p-3">
            <p className="text-xs text-slate-500">Communication</p>
            <p className="text-lg font-bold text-white">4.2</p>
          </div>
          <div className="glass rounded-xl p-3">
            <p className="text-xs text-slate-500">Technical</p>
            <p className="text-lg font-bold text-white">3.8</p>
          </div>
        </div>
      </div>

      {/* AI Chat */}
      <div className="lg:col-span-2 flex flex-col glass rounded-2xl overflow-hidden min-h-[520px]">
        <div className="border-b border-violet-500/10 px-5 py-4 flex items-center justify-between">
          <div>
            <h2 className="font-semibold text-white">AI Interviewer</h2>
            <p className="text-xs text-slate-500">Technical · Behavioral mode</p>
          </div>
          <span className="flex items-center gap-1.5 rounded-full bg-emerald-500/10 px-3 py-1 text-xs text-emerald-400 ring-1 ring-emerald-500/20">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
            Live
          </span>
        </div>

        <div className="flex-1 overflow-y-auto p-5 space-y-4 max-h-[380px]">
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm ${
                  msg.role === "ai"
                    ? "bg-violet-500/10 text-slate-200 ring-1 ring-violet-500/20"
                    : "bg-blue-600/20 text-white ring-1 ring-blue-500/20"
                }`}
              >
                {msg.role === "ai" && (
                  <span className="mb-1 block text-[10px] font-semibold uppercase tracking-wider text-violet-400">
                    AI Interviewer
                  </span>
                )}
                {msg.text}
              </div>
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
              className="flex-1 rounded-xl border border-violet-500/20 bg-slate-900/80 px-4 py-3 text-sm text-white placeholder:text-slate-500 focus:border-violet-500/50 focus:outline-none focus:ring-1 focus:ring-violet-500/30"
            />
            <Button variant="gradient" onClick={handleSend}>
              Send
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
