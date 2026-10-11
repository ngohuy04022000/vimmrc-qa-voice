"""Whisper STT server: POST /api/stt (multipart 'file') -> {"text": "..."}.

Run standalone with: uvicorn stt_server:app --port 8001
For the full application, use scripts.api_server on port 8000.
"""
import os
import tempfile

from fastapi import FastAPI, HTTPException, UploadFile
from starlette.concurrency import run_in_threadpool
from faster_whisper import WhisperModel

from threading import Lock

MODEL_SIZE = os.getenv("WHISPER_MODEL", "small")
DEVICE = os.getenv("WHISPER_DEVICE", "auto")
MAX_UPLOAD_BYTES = 25 * 1024 * 1024

app = FastAPI(title="ViMMRC Voice Q&A API")
_model_lock = Lock()
_whisper_model: WhisperModel | None = None


def get_whisper_model() -> WhisperModel:
    global _whisper_model
    if _whisper_model is None:
        with _model_lock:
            if _whisper_model is None:
                _whisper_model = WhisperModel(MODEL_SIZE, device=DEVICE, compute_type="auto")
    return _whisper_model


def transcribe(audio_path: str) -> str:
    model = get_whisper_model()
    segments, _ = model.transcribe(audio_path, language="vi", vad_filter=True)
    return " ".join(seg.text.strip() for seg in segments).strip()


@app.post("/api/stt")
async def stt(file: UploadFile) -> dict:
    data = await file.read(MAX_UPLOAD_BYTES + 1)
    if not data:
        raise HTTPException(status_code=400, detail="Empty audio")
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Audio too large")

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(data)
        tmp_path = tmp.name
    try:
        return {"text": await run_in_threadpool(transcribe, tmp_path)}
    finally:
        os.remove(tmp_path)
