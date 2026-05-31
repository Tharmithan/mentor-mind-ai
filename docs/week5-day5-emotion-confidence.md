# Week 5 · Day 5 — Emotion + Confidence Detection

Real-time **confidence meter** during mock interviews using webcam, facial expressions, and voice analysis.

## Detected signals

| Metric | Source |
|--------|--------|
| **Confidence** | Composite: eye contact, smile, low stress, attention |
| **Stress** | Brow tension, jaw open (MediaPipe blendshapes) |
| **Nervousness** | Voice volume variance + facial stress |
| **Engagement** | Face present + attention + speaking |
| **Eye contact** | Head pose / face centering vs camera |
| **Smile** | `mouthSmileLeft` + `mouthSmileRight` blendshapes |
| **Attention** | Eye contact + eyes open (blink rate) |
| **Dominant emotion** | FER-style mapping (happy, neutral, fear, …) |

## Technologies

### Browser (real-time)

- **MediaPipe Face Landmarker** (`@mediapipe/tasks-vision`) — 468 landmarks + 52 blendshapes
- **Web Audio API** — mic amplitude variance for voice nervousness
- Runs fully client-side (no video uploaded)

### Backend (OpenCV + FER+)

- **OpenCV** — Haar cascade face detection
- **FER+ ONNX** (`emotion-ferplus-8.onnx`) — 8-class emotion model (downloads on first use)
- `GET /api/interview/emotion/status` — availability check
- `POST /api/interview/emotion/analyze` — upload JPEG/PNG frame

On answer submit, a webcam frame is sent to the server and **blended** with client metrics.

## Features

- **Live Confidence Meter** — updates every frame while camera is on
- **Eye contact detection** — head yaw/pitch from landmark geometry
- **Smile detection** — blendshape thresholds
- **Attention tracking** — face in frame + eyes open
- **Voice analysis** — when mic is on, volume variance feeds nervousness score

## API

Submit answer with optional emotion block:

```json
{
  "answer_text": "...",
  "emotion_metrics": {
    "confidence": 78,
    "stress": 32,
    "nervousness": 41,
    "engagement": 72,
    "eye_contact": 81,
    "smile": 45,
    "attention": 76,
    "dominant_emotion": "neutral",
    "samples": 84
  }
}
```

Turn feedback includes `emotion_metrics.delivery_tips` e.g.:

> “Try improving eye contact and reducing filler words.”

## Frontend modules

- `src/hooks/useEmotionDetection.ts`
- `src/lib/emotion/faceAnalysis.ts`
- `src/lib/emotion/voiceAnalysis.ts`
- `src/components/interview/EmotionPanel.tsx`

## Usage

1. Start interview on `/interview` (camera auto-enables)
2. Allow webcam + mic permissions
3. Watch **Live confidence** and emotion badges on the video feed
4. Submit answer — delivery tips appear in feedback
