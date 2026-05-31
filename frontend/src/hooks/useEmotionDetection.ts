"use client";

import { useEffect, useRef, useState } from "react";
import type { RefObject } from "react";
import {
  attentionScore,
  blendshapesToMap,
  dominantEmotionFromBlendshapes,
  eyeContactScore,
  loadFaceLandmarker,
  mergeFaceAndVoice,
  smileScore,
  smoothEmotion,
  stressFromFace,
} from "@/lib/emotion/faceAnalysis";
import { DEFAULT_EMOTION, type EmotionSnapshot } from "@/lib/emotion/types";
import { VoiceAnalyzer } from "@/lib/emotion/voiceAnalysis";

type Options = {
  videoRef: RefObject<HTMLVideoElement | null>;
  active: boolean;
  audioStream?: MediaStream | null;
};

export function useEmotionDetection({ videoRef, active, audioStream }: Options) {
  const [snapshot, setSnapshot] = useState<EmotionSnapshot>(DEFAULT_EMOTION);
  const [ready, setReady] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const rafRef = useRef<number>(0);
  const lastVideoTimeRef = useRef(-1);
  const smoothRef = useRef<EmotionSnapshot>(DEFAULT_EMOTION);
  const voiceRef = useRef(new VoiceAnalyzer());
  const samplesRef = useRef<EmotionSnapshot[]>([]);

  useEffect(() => {
    if (audioStream) voiceRef.current.connect(audioStream);
    else voiceRef.current.disconnect();
    return () => voiceRef.current.disconnect();
  }, [audioStream]);

  useEffect(() => {
    if (!active) {
      cancelAnimationFrame(rafRef.current);
      setReady(false);
      return;
    }

    let cancelled = false;

    async function loop() {
      try {
        const landmarker = await loadFaceLandmarker();
        if (cancelled) return;
        setReady(true);
        setError(null);

        const tick = () => {
          if (cancelled) return;
          const video = videoRef.current;
          const voice = voiceRef.current.sample();

          let facePartial: Partial<EmotionSnapshot> = {
            faceDetected: false,
            dominantEmotion: "neutral",
            stress: 35,
            eyeContact: 65,
            smile: 0,
            attention: 70,
          };

          if (video && video.readyState >= 2 && !video.paused) {
            if (video.currentTime !== lastVideoTimeRef.current) {
              lastVideoTimeRef.current = video.currentTime;
              const result = landmarker.detectForVideo(video, performance.now());
              if (result.faceBlendshapes?.length) {
                const map = blendshapesToMap(
                  result.faceBlendshapes[0].categories.map((c) => ({
                    categoryName: c.categoryName,
                    score: c.score,
                  }))
                );
                const lm = result.faceLandmarks[0];
                const eye = eyeContactScore(lm);
                facePartial = {
                  faceDetected: true,
                  dominantEmotion: dominantEmotionFromBlendshapes(map),
                  stress: stressFromFace(map),
                  eyeContact: eye,
                  smile: smileScore(map),
                  attention: attentionScore(map, eye),
                };
              }
            }
          }

          const merged = mergeFaceAndVoice(facePartial, voice.nervousness, voice.speaking);
          smoothRef.current = smoothEmotion(smoothRef.current, merged);
          setSnapshot(smoothRef.current);
          samplesRef.current.push(smoothRef.current);
          if (samplesRef.current.length > 120) samplesRef.current.shift();

          rafRef.current = requestAnimationFrame(tick);
        };

        rafRef.current = requestAnimationFrame(tick);
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : "Emotion model failed to load");
          setReady(false);
        }
      }
    }

    void loop();
    return () => {
      cancelled = true;
      cancelAnimationFrame(rafRef.current);
    };
  }, [active, videoRef]);

  function getSessionAverage(): EmotionSnapshot {
    const s = samplesRef.current;
    if (!s.length) return snapshot;
    const n = s.length;
    const avg = (k: keyof EmotionSnapshot) =>
      Math.round(
        s.reduce((a, x) => a + (typeof x[k] === "number" ? (x[k] as number) : 0), 0) / n
      );
    const emotions = s.map((x) => x.dominantEmotion);
    const dominant =
      emotions.sort(
        (a, b) =>
          emotions.filter((e) => e === b).length - emotions.filter((e) => e === a).length
      )[0] ?? "neutral";
    return {
      confidence: avg("confidence"),
      stress: avg("stress"),
      nervousness: avg("nervousness"),
      engagement: avg("engagement"),
      eyeContact: avg("eyeContact"),
      smile: avg("smile"),
      attention: avg("attention"),
      dominantEmotion: dominant,
      faceDetected: s.some((x) => x.faceDetected),
      voiceActive: s.some((x) => x.voiceActive),
      timestamp: Date.now(),
      sampleCount: n,
    } as EmotionSnapshot & { sampleCount: number };
  }

  function resetSamples() {
    samplesRef.current = [];
    smoothRef.current = DEFAULT_EMOTION;
    setSnapshot(DEFAULT_EMOTION);
  }

  return { snapshot, ready, error, getSessionAverage, resetSamples };
}
