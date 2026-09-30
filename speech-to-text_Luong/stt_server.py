"""Whisper STT server: POST /api/stt (multipart 'file') -> {"text": "..."}.

Run: uvicorn stt_server:app --port 8001
"""
import os
import tempfile

from fastapi import FastAPI, HTTPException, UploadFile
from faster_whisper import WhisperModel

MODEL_SIZE = os.getenv("WHISPER_MODEL", "small")
DEVICE = os.getenv("WHISPER_DEVICE", "auto")
MAX_UPLOAD_BYTES = 25 * 1024 * 1024

app = FastAPI(title="speech-to-text")
model = WhisperModel(MODEL_SIZE, device=DEVICE, compute_type="auto")


def transcribe(audio_path: str) -> str:
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
        return {"text": transcribe(tmp_path)}
    finally:
        os.remove(tmp_path)
