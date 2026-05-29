# Week 5 · Day 2 — Speech-to-Text

Convert voice → text for the AI Interview Coach using **OpenAI Whisper** plus browser **live transcription**.

## Backend

### Install

```bash
cd backend
pip install -r requirements-interview.txt
brew install ffmpeg   # required by Whisper
```

### Modules

- `app/interview/transcription.py` — lazy-loads Whisper `base` model, transcribes uploaded audio
- `POST /api/interview/transcribe` — multipart audio upload → `{ text, language, duration_sec }`
- `GET /api/interview/transcribe/status` — whether Whisper is installed

Supported formats: `.webm`, `.wav`, `.mp3`, `.m4a`, `.ogg`

## Frontend

### `VoiceRecorder.tsx`

1. **Live transcription** — Web Speech API (`webkitSpeechRecognition`) shows words as the user speaks
2. **Microphone recording** — `MediaRecorder` captures audio while the mic is on
3. **Whisper refine** — on stop, audio is uploaded to `/api/interview/transcribe` for a higher-accuracy transcript merged into the answer field

### Usage

On `/interview`, tap the mic under the webcam preview. Speak, watch the live caption bar, stop the mic, then edit or submit.

## Flow

```
User speaks → browser live text (interim)
           → stop mic → audio blob → Whisper API → final text in answer box
           → Submit → Day 3 AI evaluation
```
