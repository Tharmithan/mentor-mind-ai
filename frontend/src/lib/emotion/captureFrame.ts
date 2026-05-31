/** Capture a JPEG frame from a live video element. */

export function captureVideoFrame(
  video: HTMLVideoElement,
  quality = 0.85
): Promise<Blob | null> {
  if (video.videoWidth === 0 || video.videoHeight === 0) {
    return Promise.resolve(null);
  }
  const canvas = document.createElement("canvas");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext("2d");
  if (!ctx) return Promise.resolve(null);
  ctx.drawImage(video, 0, 0);
  return new Promise((resolve) => {
    canvas.toBlob((blob) => resolve(blob), "image/jpeg", quality);
  });
}

/** Blend client-side MediaPipe metrics with server FER result. */
export function mergeEmotionMetrics(
  client: {
    confidence: number;
    stress: number;
    nervousness: number;
    engagement: number;
    eye_contact: number;
    smile: number;
    attention: number;
    dominant_emotion: string;
    samples: number;
  },
  server: {
    confidence: number;
    stress: number;
    nervousness: number;
    engagement: number;
    eye_contact: number;
    smile: number;
    attention: number;
    dominant_emotion: string;
    face_detected: boolean;
  } | null
) {
  if (!server?.face_detected) return client;
  const w = 0.45;
  const blend = (a: number, b: number) => Math.round(a * (1 - w) + b * w);
  return {
    confidence: blend(client.confidence, server.confidence),
    stress: blend(client.stress, server.stress),
    nervousness: blend(client.nervousness, server.nervousness),
    engagement: blend(client.engagement, server.engagement),
    eye_contact: client.eye_contact,
    smile: blend(client.smile, server.smile),
    attention: blend(client.attention, server.attention),
    dominant_emotion: server.dominant_emotion,
    samples: client.samples,
  };
}
