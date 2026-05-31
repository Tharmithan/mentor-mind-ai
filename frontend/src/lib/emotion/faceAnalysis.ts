/** MediaPipe Face Landmarker helpers — smile, eye contact, FER-style emotion. */

import type { EmotionSnapshot } from "./types";

type BlendMap = Record<string, number>;

const WASM =
  "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/wasm";
const MODEL =
  "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task";

let landmarkerPromise: Promise<import("@mediapipe/tasks-vision").FaceLandmarker> | null =
  null;

export async function loadFaceLandmarker() {
  if (!landmarkerPromise) {
    landmarkerPromise = (async () => {
      const { FaceLandmarker, FilesetResolver } = await import(
        "@mediapipe/tasks-vision"
      );
      const vision = await FilesetResolver.forVisionTasks(WASM);
      return FaceLandmarker.createFromOptions(vision, {
        baseOptions: { modelAssetPath: MODEL, delegate: "GPU" },
        outputFaceBlendshapes: true,
        outputFacialTransformationMatrixes: true,
        runningMode: "VIDEO",
        numFaces: 1,
      });
    })();
  }
  return landmarkerPromise;
}

function bs(map: BlendMap, key: string): number {
  return map[key] ?? 0;
}

/** Map blendshapes → FER-style dominant label. */
export function dominantEmotionFromBlendshapes(map: BlendMap): string {
  const scores: Record<string, number> = {
    happy: (bs(map, "mouthSmileLeft") + bs(map, "mouthSmileRight")) / 2,
    sad: (bs(map, "mouthFrownLeft") + bs(map, "mouthFrownRight")) / 2,
    angry: (bs(map, "browDownLeft") + bs(map, "browDownRight")) / 2,
    fear: bs(map, "browInnerUp") * 0.6 + bs(map, "eyeWideLeft") * 0.4,
    surprise: bs(map, "jawOpen") * 0.5 + bs(map, "browOuterUpLeft") * 0.5,
    disgust: (bs(map, "noseSneerLeft") + bs(map, "noseSneerRight")) / 2,
    neutral: 0.25,
  };
  return Object.entries(scores).sort((a, b) => b[1] - a[1])[0][0];
}

/** Smile score 0–100 from mouth blendshapes. */
export function smileScore(map: BlendMap): number {
  const s = (bs(map, "mouthSmileLeft") + bs(map, "mouthSmileRight")) / 2;
  return Math.round(Math.min(100, s * 140));
}

/** Eye contact proxy: head facing camera (yaw/pitch from landmark symmetry). */
export function eyeContactScore(
  landmarks: { x: number; y: number; z?: number }[]
): number {
  if (landmarks.length < 468) return 50;
  const nose = landmarks[1];
  const leftCheek = landmarks[234];
  const rightCheek = landmarks[454];
  const leftEye = landmarks[33];
  const rightEye = landmarks[263];

  const faceW = Math.abs(rightCheek.x - leftCheek.x) || 0.001;
  const centerX = (leftCheek.x + rightCheek.x) / 2;
  const yaw = Math.abs(nose.x - centerX) / faceW;
  const eyeLine = Math.abs(leftEye.y - rightEye.y);
  const pitch = eyeLine / faceW;

  const centered = Math.max(0, 1 - yaw * 4 - pitch * 3);
  return Math.round(Math.min(100, centered * 100));
}

/** Attention: face centered + eyes open (low blink). */
export function attentionScore(map: BlendMap, eyeContact: number): number {
  const blink = (bs(map, "eyeBlinkLeft") + bs(map, "eyeBlinkRight")) / 2;
  const open = Math.max(0, 1 - blink * 1.2);
  return Math.round(Math.min(100, eyeContact * 0.65 + open * 35));
}

export function stressFromFace(map: BlendMap): number {
  const brow = (bs(map, "browDownLeft") + bs(map, "browDownRight")) / 2;
  const jaw = bs(map, "jawOpen");
  const inner = bs(map, "browInnerUp");
  return Math.round(Math.min(100, brow * 55 + jaw * 25 + inner * 35));
}

export function blendshapesToMap(
  categories: { categoryName: string; score: number }[]
): BlendMap {
  const m: BlendMap = {};
  for (const c of categories) m[c.categoryName] = c.score;
  return m;
}

export function mergeFaceAndVoice(
  face: Partial<EmotionSnapshot>,
  voiceNervousness: number,
  voiceSpeaking: boolean
): EmotionSnapshot {
  const stress = Math.round(
    ((face.stress ?? 30) * 0.7 + voiceNervousness * 0.3)
  );
  const nervousness = Math.round(
    voiceSpeaking ? voiceNervousness * 0.55 + stress * 0.45 : stress * 0.6
  );
  const eyeContact = face.eyeContact ?? 70;
  const smile = face.smile ?? 0;
  const attention = face.attention ?? 75;
  const engagement = face.faceDetected
    ? Math.round(attention * 0.5 + eyeContact * 0.3 + (voiceSpeaking ? 20 : 10))
    : Math.round(voiceSpeaking ? 45 : 35);

  let confidence = Math.round(
    eyeContact * 0.35 +
      smile * 0.15 +
      (100 - stress) * 0.25 +
      (100 - nervousness) * 0.15 +
      attention * 0.1
  );
  confidence = Math.max(15, Math.min(98, confidence));

  return {
    confidence,
    stress,
    nervousness,
    engagement: Math.min(100, engagement),
    eyeContact,
    smile,
    attention,
    dominantEmotion: face.dominantEmotion ?? "neutral",
    faceDetected: face.faceDetected ?? false,
    voiceActive: voiceSpeaking,
    timestamp: Date.now(),
  };
}

/** Exponential smoothing between frames. */
export function smoothEmotion(prev: EmotionSnapshot, next: EmotionSnapshot): EmotionSnapshot {
  const a = 0.28;
  const lerp = (p: number, n: number) => Math.round(p * (1 - a) + n * a);
  return {
    confidence: lerp(prev.confidence, next.confidence),
    stress: lerp(prev.stress, next.stress),
    nervousness: lerp(prev.nervousness, next.nervousness),
    engagement: lerp(prev.engagement, next.engagement),
    eyeContact: lerp(prev.eyeContact, next.eyeContact),
    smile: lerp(prev.smile, next.smile),
    attention: lerp(prev.attention, next.attention),
    dominantEmotion: next.dominantEmotion,
    faceDetected: next.faceDetected,
    voiceActive: next.voiceActive,
    timestamp: next.timestamp,
  };
}
