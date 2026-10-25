"""Vietnamese Whisper API: POST /api/stt with a multipart audio file."""
import os
import tempfile
from functools import lru_cache
from pathlib import Path
from threading import Lock

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from faster_whisper import WhisperModel

MODEL_DIR = Path(__file__).parent / "models"
LOCAL_MODELS = (
    MODEL_DIR / "whisper-small-vi-50h-ct2",
    MODEL_DIR / "whisper-small-vi-ct2",
)
DEFAULT_MODEL = str(next((model for model in LOCAL_MODELS if model.is_dir()), "small"))
MODEL_SIZE = os.getenv("WHISPER_MODEL", DEFAULT_MODEL)
DEVICE = os.getenv("WHISPER_DEVICE", "cpu")
COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE_TYPE", "int8")
MAX_UPLOAD_BYTES = 25 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {
    "audio/flac",
    "audio/m4a",
    "audio/mpeg",
    "audio/mp4",
    "audio/ogg",
    "audio/wav",
    "audio/x-wav",
    "audio/webm",
    "video/webm",
}
MODEL_LOCK = Lock()

app = FastAPI(title="speech-to-text")


@app.get("/")
def root() -> dict:
    return {
        "service": "Vietnamese Speech-to-Text",
        "status": "ok",
        "health": "/health",
        "docs": "/docs",
        "transcribe": "POST /api/stt",
    }


@lru_cache(maxsize=1)
def get_model() -> WhisperModel:
    return WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE)


def transcribe(audio_path: str) -> str:
    with MODEL_LOCK:
        segments, _ = get_model().transcribe(
            audio_path,
            language="vi",
            vad_filter=True,
            beam_size=5,
            condition_on_previous_text=False,
        )
        return " ".join(seg.text.strip() for seg in segments).strip()


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "model": MODEL_SIZE,
        "device": DEVICE,
        "model_loaded": get_model.cache_info().currsize > 0,
    }


@app.post("/api/stt")
async def stt(file: UploadFile = File(...)) -> dict:
    content_type = (file.content_type or "").lower()
    if content_type and content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=415, detail="Unsupported audio format")

    suffix = Path(file.filename or "audio.wav").suffix or ".wav"
    tmp_path = ""
    try:
        data = await file.read(MAX_UPLOAD_BYTES + 1)
        if not data:
            raise HTTPException(status_code=400, detail="Empty audio")
        if len(data) > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail="Audio too large")

        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(data)
            tmp_path = tmp.name

        text = await run_in_threadpool(transcribe, tmp_path)
        if not text:
            raise HTTPException(status_code=422, detail="No speech detected")
        return {"text": text}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Transcription failed") from exc
    finally:
        await file.close()
        if tmp_path:
            Path(tmp_path).unlink(missing_ok=True)
