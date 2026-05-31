"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Mic, MicOff, Loader2 } from "lucide-react";
import { transcribeInterviewAudio } from "@/lib/api";

type SpeechRecognitionCtor = new () => SpeechRecognitionInstance;

interface SpeechRecognitionInstance extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start(): void;
  stop(): void;
  onresult: ((ev: SpeechRecognitionEvent) => void) | null;
  onerror: ((ev: Event) => void) | null;
  onend: (() => void) | null;
}

interface SpeechRecognitionEvent {
  resultIndex: number;
  results: SpeechRecognitionResultList;
}

interface SpeechRecognitionResultList {
  length: number;
  [index: number]: SpeechRecognitionResult;
}

interface SpeechRecognitionResult {
  isFinal: boolean;
  [index: number]: { transcript: string };
}

declare global {
  interface Window {
    webkitSpeechRecognition?: SpeechRecognitionCtor;
    SpeechRecognition?: SpeechRecognitionCtor;
  }
}

interface VoiceRecorderProps {
  active: boolean;
  onActiveChange: (active: boolean) => void;
  onTranscript: (text: string) => void;
  onLiveTranscript?: (text: string) => void;
  onAudioStream?: (stream: MediaStream | null) => void;
  className?: string;
}

export function VoiceRecorder({
  active,
  onActiveChange,
  onTranscript,
  onLiveTranscript,
  onAudioStream,
  className = "",
}: VoiceRecorderProps) {
  const [liveText, setLiveText] = useState("");
  const [refining, setRefining] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(false);

  const recognitionRef = useRef<SpeechRecognitionInstance | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const finalBufferRef = useRef("");

  useEffect(() => {
    const Ctor = window.SpeechRecognition || window.webkitSpeechRecognition;
    setSpeechSupported(Boolean(Ctor));
  }, []);

  const stopAll = useCallback(async () => {
    recognitionRef.current?.stop();
    recognitionRef.current = null;

    const recorder = mediaRecorderRef.current;
    mediaRecorderRef.current = null;

    if (recorder && recorder.state !== "inactive") {
      await new Promise<void>((resolve) => {
        recorder.onstop = () => resolve();
        recorder.stop();
      });
    }

    const chunks = chunksRef.current;
    chunksRef.current = [];

    const live = [finalBufferRef.current, liveText].filter(Boolean).join(" ").trim();
    finalBufferRef.current = "";

    if (chunks.length > 0) {
      setRefining(true);
      try {
        const blob = new Blob(chunks, { type: "audio/webm" });
        const res = await transcribeInterviewAudio(blob);
        const whisper = res.text?.trim();
        const merged = whisper && whisper.length > live.length * 0.5 ? whisper : live || whisper;
        if (merged) {
          onTranscript(merged);
          setLiveText("");
          onLiveTranscript?.("");
        }
      } catch {
        if (live) onTranscript(live);
      } finally {
        setRefining(false);
      }
    } else if (live) {
      onTranscript(live);
      setLiveText("");
      onLiveTranscript?.("");
    }
  }, [liveText, onLiveTranscript, onTranscript]);

  const startAll = useCallback(async () => {
    setLiveText("");
    finalBufferRef.current = "";
    chunksRef.current = [];

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream, { mimeType: "audio/webm" });
      chunksRef.current = [];
      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };
      recorder.onstop = () => stream.getTracks().forEach((t) => t.stop());
      recorder.start(250);
      mediaRecorderRef.current = recorder;
      onAudioStream?.(stream);
    } catch {
      onAudioStream?.(null);
      /* mic denied — live speech may still work in some browsers */
    }

    const Ctor = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Ctor) return;

    const recognition = new Ctor();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      let interim = "";
      let final = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const t = event.results[i][0].transcript;
        if (event.results[i].isFinal) final += t;
        else interim += t;
      }
      if (final) {
        finalBufferRef.current = `${finalBufferRef.current} ${final}`.trim();
      }
      const display = `${finalBufferRef.current} ${interim}`.trim();
      setLiveText(display);
      onLiveTranscript?.(display);
    };

    recognition.onend = () => {
      if (mediaRecorderRef.current?.state === "recording") {
        try {
          recognition.start();
        } catch {
          /* ignore restart errors */
        }
      }
    };

    recognition.start();
    recognitionRef.current = recognition;
  }, [onLiveTranscript]);

  useEffect(() => {
    if (active) {
      startAll();
    } else if (recognitionRef.current || mediaRecorderRef.current) {
      stopAll();
    }
    return () => {
      recognitionRef.current?.stop();
      if (mediaRecorderRef.current?.state === "recording") {
        mediaRecorderRef.current.stop();
      }
      onAudioStream?.(null);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [active]);

  return (
    <div className={`flex flex-col items-center gap-2 ${className}`}>
      <button
        type="button"
        onClick={() => !refining && onActiveChange(!active)}
        disabled={refining}
        className={`flex h-12 w-12 items-center justify-center rounded-full transition ${
          active
            ? "bg-gradient-to-r from-violet-600 to-blue-600 text-white ring-2 ring-violet-400/50"
            : "bg-slate-800/90 text-slate-400"
        }`}
        title={active ? "Stop recording" : "Live transcription"}
      >
        {refining ? (
          <Loader2 className="h-5 w-5 animate-spin" />
        ) : active ? (
          <Mic className="h-5 w-5" />
        ) : (
          <MicOff className="h-5 w-5" />
        )}
      </button>
      {active && (
        <p className="max-w-[140px] text-center text-[10px] text-emerald-400/90">
          {speechSupported ? "Live transcription…" : "Recording…"}
        </p>
      )}
      {active && liveText && (
        <p className="max-h-16 max-w-[160px] overflow-y-auto rounded-lg bg-black/40 px-2 py-1 text-[10px] leading-snug text-slate-300">
          {liveText}
        </p>
      )}
    </div>
  );
}
