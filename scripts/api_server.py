"""Unified FastAPI backend for the ViMMRC voice Q&A web application.

Integrates:
- STT: Faster-Whisper (speech-to-text_Luong)
- Retrieval: BM25 Retriever over ViMMRC 2.0 articles (retrieval-model_Huy)
- MRC: fine-tuned ViT5 answer generator (mrc-model_Huy)
- TTS: Multi-engine Vietnamese synthesis with normalizer (text-to-speech_Duy)
- Web UI: Angular static assets mounted directly when built (web-interface_Luong)

Run from the repository root with ``uvicorn scripts.api_server:app --port 8000``.
"""
from __future__ import annotations

import os
import sys
import tempfile
import time
from pathlib import Path
from threading import Lock

from fastapi import HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, field_validator
from starlette.background import BackgroundTask
from starlette.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parents[1]
for folder in (
    "retrieval-model_Huy",
    "mrc-model_Huy",
    "speech-to-text_Luong",
    "text-to-speech_Duy",
    "text-to-speech_Duy/src",
):
    path_str = str(ROOT / folder)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

from retrieval_client import Retriever
from kb_retriever import load_any
from mrc_client import LexicalBaselineClient, MRCClient

from synthesize import synthesize as tts_synthesize
import stt_server

app = stt_server.app
app.title = "ViMMRC Voice Q&A API"

_service_lock = Lock()
_retriever: Retriever | None = None
_reader = None

DEMO_PASSAGES = [
    {
        "id": "demo:capital",
        "passage": "Hà Nội là thủ đô của Việt Nam. Thành phố nằm ở miền Bắc.",
    },
    {
        "id": "demo:river",
        "passage": "Sông Cửu Long chảy qua vùng đồng bằng Nam Bộ.",
    },
]


class RetrieveRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=3, ge=1, le=10)

    @field_validator("question")
    @classmethod
    def question_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("question must not be blank")
        return value


class AnswerRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    passage: str = Field(min_length=1, max_length=100_000)

    @field_validator("question", "passage")
    @classmethod
    def text_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("text must not be blank")
        return value


class TTSRequest(BaseModel):
    text: str = Field(min_length=1, max_length=5000)
    engine: str | None = None
    voice: str | None = None
    rate: str = "+0%"

    @field_validator("text")
    @classmethod
    def text_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("text must not be blank")
        return value


def get_qa_services() -> tuple[Retriever, object]:
    """Load index and reader with fallbacks."""
    global _retriever, _reader
    if _retriever is not None and _reader is not None:
        return _retriever, _reader

    with _service_lock:
        if _retriever is None:
            index_path = os.getenv("QA_INDEX")
            default_index = ROOT / "data" / "vimmrc_index.json"
            if index_path and Path(index_path).exists():
                _retriever = load_any(index_path, os.getenv("KB_WIKI"), float(os.getenv("KB_WIKI_RATIO", "0.5")))
            elif default_index.exists():
                _retriever = Retriever.load(str(default_index))
            else:
                _retriever = Retriever(DEMO_PASSAGES)

        if _reader is None:
            checkpoint = os.getenv("MRC_CHECKPOINT")
            _reader = MRCClient(checkpoint) if checkpoint else LexicalBaselineClient()

    return _retriever, _reader


@app.get("/api/health")
def health() -> dict:
    retriever, _ = get_qa_services()
    index_source = "custom_index" if os.getenv("QA_INDEX") else (
        "vimmrc_corpus" if (ROOT / "data" / "vimmrc_index.json").exists() else "demo_corpus"
    )
    dist_browser = ROOT / "web-interface_Luong" / "dist" / "web-interface" / "browser"
    return {
        "status": "ok",
        "retrieval": index_source,
        "retrieval_passages": len(retriever.passages),
        "reader": "trained_vit5" if os.getenv("MRC_CHECKPOINT") else "lexical_baseline",
        "tts_engine": os.getenv("TTS_ENGINE", "matcha"),
        "frontend_served": dist_browser.exists() and (dist_browser / "index.html").exists(),
    }


@app.post("/api/retrieve")
def retrieve(request: RetrieveRequest) -> dict:
    retriever, _ = get_qa_services()
    hits = retriever.search(request.question, top_k=request.top_k)
    return {
        "passages": [
            {
                "id": hit["id"],
                "text": hit["passage"],
                "score": hit["score"],
            }
            for hit in hits
        ]
    }


@app.post("/api/answer")
def answer(request: AnswerRequest) -> dict:
    _, reader = get_qa_services()
    return {"answer": reader.answer_question(request.question, request.passage)}


@app.post("/api/tts")
def synthesize_endpoint(request: TTSRequest) -> FileResponse:
    engine_name = request.engine or os.getenv("TTS_ENGINE", "matcha")
    voice_name = request.voice or os.getenv("TTS_VOICE", "nu")
    temp_dir = tempfile.gettempdir()
    ext = ".wav" if engine_name in ("matcha", "vits") else ".mp3"
    target_path = os.path.join(temp_dir, f"vimmrc_tts_{int(time.time() * 1000)}{ext}")

    try:
        actual_path = tts_synthesize(
            text=request.text.strip(),
            output_path=target_path,
            voice=voice_name,
            engine=engine_name,
            rate=request.rate,
        )
    except Exception as exc:
        Path(target_path).unlink(missing_ok=True)
        raise HTTPException(status_code=502, detail=f"TTS synthesis failed: {exc}") from exc

    is_wav = str(actual_path).lower().endswith(".wav")
    media_type = "audio/wav" if is_wav else "audio/mpeg"
    filename = "answer.wav" if is_wav else "answer.mp3"

    return FileResponse(
        actual_path,
        media_type=media_type,
        filename=filename,
        background=BackgroundTask(Path(actual_path).unlink, missing_ok=True),
    )


# Mount static Angular web client if built
dist_browser = ROOT / "web-interface_Luong" / "dist" / "web-interface" / "browser"
if dist_browser.exists() and (dist_browser / "index.html").exists():
    # stt_server's GET / info route would shadow the frontend index
    app.router.routes = [r for r in app.router.routes if getattr(r, "path", None) != "/"]
    app.mount("/", StaticFiles(directory=str(dist_browser), html=True), name="static_frontend")
