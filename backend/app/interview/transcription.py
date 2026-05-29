"""Speech-to-text via OpenAI Whisper (Week 5 · Day 2).

Accepts uploaded audio (webm, wav, mp3, m4a), returns transcript text.
Model loads lazily on first use (``base`` — good balance of speed and accuracy).
"""

from __future__ import annotations

import tempfile
from pathlib import Path

AUDIO_DIR = Path(__file__).resolve().parents[2] / "uploads" / "audio"
ALLOWED_SUFFIXES = {".webm", ".wav", ".mp3", ".m4a", ".ogg", ".mpeg", ".mpga"}
DEFAULT_MODEL = "base"

_model = None
_model_name: str | None = None


def whisper_available() -> bool:
    try:
        import whisper  # noqa: F401
        return True
    except ImportError:
        return False


def _load_model(name: str = DEFAULT_MODEL):
    global _model, _model_name
    if _model is not None and _model_name == name:
        return _model
    import whisper
    _model = whisper.load_model(name)
    _model_name = name
    return _model


def transcribe_file(file_path: Path, model_name: str = DEFAULT_MODEL) -> dict:
    """Transcribe an audio file. Returns {text, language, duration_sec}."""
    if not whisper_available():
        raise RuntimeError(
            "Whisper is not installed. Run: pip install -r requirements-interview.txt "
            "and ensure ffmpeg is on your PATH (brew install ffmpeg)."
        )
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(str(path))

    model = _load_model(model_name)
    result = model.transcribe(str(path), fp16=False)
    text = (result.get("text") or "").strip()
    return {
        "text": text,
        "language": result.get("language"),
        "duration_sec": round(result.get("duration") or 0, 2),
    }


def transcribe_bytes(content: bytes, suffix: str = ".webm", model_name: str = DEFAULT_MODEL) -> dict:
    """Save bytes to a temp file, transcribe, delete temp file."""
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    suffix = suffix if suffix.startswith(".") else f".{suffix}"
    if suffix.lower() not in ALLOWED_SUFFIXES:
        suffix = ".webm"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False, dir=AUDIO_DIR) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)
    try:
        return transcribe_file(tmp_path, model_name=model_name)
    finally:
        tmp_path.unlink(missing_ok=True)
