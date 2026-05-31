/** Real-time emotion + delivery metrics (Week 5 · Day 5). */

export type EmotionSnapshot = {
  confidence: number;
  stress: number;
  nervousness: number;
  engagement: number;
  eyeContact: number;
  smile: number;
  attention: number;
  dominantEmotion: string;
  faceDetected: boolean;
  voiceActive: boolean;
  timestamp: number;
};

export type EmotionMetricsPayload = {
  confidence: number;
  stress: number;
  nervousness: number;
  engagement: number;
  eye_contact: number;
  smile: number;
  attention: number;
  dominant_emotion: string;
  samples: number;
};

export const DEFAULT_EMOTION: EmotionSnapshot = {
  confidence: 72,
  stress: 28,
  nervousness: 32,
  engagement: 65,
  eyeContact: 70,
  smile: 0,
  attention: 75,
  dominantEmotion: "neutral",
  faceDetected: false,
  voiceActive: false,
  timestamp: 0,
};
