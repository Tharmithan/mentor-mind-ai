"""OpenCV face detection + FER+ ONNX emotion model (Week 5 · Day 5).

Uses:
  - OpenCV Haar cascade for face crop
  - FER+ 8-class ONNX model (emotion-ferplus-8.onnx)

Model downloads on first use into ``backend/models/emotion/``.
"""

from __future__ import annotations

import urllib.request
from pathlib import Path

import numpy as np

MODEL_DIR = Path(__file__).resolve().parents[2] / "models" / "emotion"
MODEL_PATH = MODEL_DIR / "emotion-ferplus-8.onnx"
MODEL_URL = (
    "https://huggingface.co/onnxmodelzoo/emotion-ferplus-8/resolve/main/emotion-ferplus-8.onnx"
)
MIN_MODEL_BYTES = 1_000_000

# FER+ label order (ONNX model zoo)
FER_LABELS = [
    "neutral",
    "happy",
    "surprise",
    "sad",
    "angry",
    "disgust",
    "fear",
    "contempt",
]

_net = None
_cascade = None


def opencv_available() -> bool:
    try:
        import cv2  # noqa: F401
        return True
    except ImportError:
        return False


def fer_model_available() -> bool:
    return opencv_available() and (_ensure_model() is not None or MODEL_PATH.exists())


def _ensure_model() -> Path | None:
    if MODEL_PATH.exists() and MODEL_PATH.stat().st_size >= MIN_MODEL_BYTES:
        return MODEL_PATH
    try:
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(MODEL_URL, headers={"User-Agent": "MentorMindAI/1.0"})
        with urllib.request.urlopen(req, timeout=120) as resp, open(MODEL_PATH, "wb") as f:
            f.write(resp.read())
        if MODEL_PATH.exists() and MODEL_PATH.stat().st_size >= MIN_MODEL_BYTES:
            return MODEL_PATH
        MODEL_PATH.unlink(missing_ok=True)
        return None
    except Exception:
        MODEL_PATH.unlink(missing_ok=True)
        return None


def _load_net():
    global _net, _cascade
    if _net is not None:
        return _net
    import cv2

    path = _ensure_model()
    if not path:
        raise RuntimeError(
            "FER model not available. Install opencv-python-headless and ensure network "
            "access to download emotion-ferplus-8.onnx"
        )
    _net = cv2.dnn.readNetFromONNX(str(path))
    cascade_file = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    _cascade = cv2.CascadeClassifier(cascade_file)
    return _net


def _decode_image(content: bytes):
    import cv2

    arr = np.frombuffer(content, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode image — use JPEG or PNG")
    return img


def _largest_face(gray, cascade):
    faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(48, 48))
    if len(faces) == 0:
        return None
    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
    return int(x), int(y), int(w), int(h)


def _preprocess_face(face_bgr) -> np.ndarray:
    import cv2

    gray = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, (64, 64))
    blob = gray.astype(np.float32)
    blob = np.expand_dims(blob, axis=0)
    blob = np.expand_dims(blob, axis=0)
    return blob


def _scores_to_metrics(probs: dict[str, float]) -> dict:
    """Map FER probabilities → interview delivery metrics."""
    happy = probs.get("happy", 0)
    neutral = probs.get("neutral", 0)
    stress_emotions = probs.get("angry", 0) + probs.get("fear", 0) + probs.get("sad", 0)
    surprise = probs.get("surprise", 0)

    dominant = max(probs, key=probs.get)
    confidence = int(min(98, max(20, happy * 100 + neutral * 40 + (1 - stress_emotions) * 35)))
    stress = int(min(100, stress_emotions * 100))
    nervousness = int(min(100, (probs.get("fear", 0) + surprise * 0.5) * 100))
    engagement = int(min(100, (neutral + happy + surprise) * 80))
    smile = int(min(100, happy * 120))
    attention = int(min(100, 55 + neutral * 25 + happy * 20))

    return {
        "dominant_emotion": dominant,
        "confidence": confidence,
        "stress": stress,
        "nervousness": nervousness,
        "engagement": engagement,
        "smile": smile,
        "attention": attention,
        "eye_contact": 70,
        "emotions": probs,
        "face_detected": True,
        "model": "ferplus-onnx",
    }


def analyze_frame_bytes(content: bytes) -> dict:
    """Detect face + FER emotion from image bytes."""
    if not opencv_available():
        raise RuntimeError(
            "OpenCV not installed. Run: pip install -r requirements-interview.txt"
        )

    import cv2

    net = _load_net()
    img = _decode_image(content)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    box = _largest_face(gray, _cascade)
    if box is None:
        return {
            "face_detected": False,
            "dominant_emotion": "neutral",
            "confidence": 50,
            "stress": 40,
            "nervousness": 40,
            "engagement": 40,
            "smile": 0,
            "attention": 50,
            "eye_contact": 50,
            "emotions": {},
            "model": "ferplus-onnx",
            "note": "No face detected in frame",
        }

    x, y, w, h = box
    pad = int(w * 0.08)
    x0 = max(0, x - pad)
    y0 = max(0, y - pad)
    x1 = min(img.shape[1], x + w + pad)
    y1 = min(img.shape[0], y + h + pad)
    face = img[y0:y1, x0:x1]

    blob = _preprocess_face(face)
    net.setInput(blob)
    out = net.forward()
    probs_arr = out.flatten()
    if probs_arr.sum() > 0:
        probs_arr = probs_arr / probs_arr.sum()

    probs = {FER_LABELS[i]: float(probs_arr[i]) for i in range(min(len(FER_LABELS), len(probs_arr)))}
    result = _scores_to_metrics(probs)
    result["face_box"] = {"x": x, "y": y, "w": w, "h": h}
    return result
