"""Unified FastAPI backend for the ViMMRC voice Q&A web application.

Run from the repository root with ``uvicorn scripts.api_server:app --port 8000``.
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path
from threading import Lock

from fastapi import HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, field_validator
from starlette.background import BackgroundTask

ROOT = Path(__file__).resolve().parents[1]
for folder in (
    "retrieval-model_Huy",
    "mrc-model_Huy",
    "speech-to-text_Luong",
    "text-to-speech_Duy/src",
):
    sys.path.insert(0, str(ROOT / folder))

from retrieval_client import Retriever
from mrc_client import LexicalBaselineClient, MRCClient
from tts_engine import get_tts_engine
import stt_server

app = stt_server.app
app.title = "ViMMRC Voice Q&A API"

_service_lock = Lock()
_retriever: Retriever | None = None
_reader = None
_tts_engine = None

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

    @field_validator("text")
    @classmethod
    def text_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("text must not be blank")
        return value


def get_qa_services() -> tuple[Retriever, object]:
    """Load the index and reader once, using a clearly identified demo fallback."""
    global _retriever, _reader
    if _retriever is not None and _reader is not None:
        return _retriever, _reader

    with _service_lock:
        if _retriever is None:
            index_path = os.getenv("QA_INDEX")
            _retriever = (
                Retriever.load(index_path)
                if index_path
                else Retriever(DEMO_PASSAGES)
            )
        if _reader is None:
            checkpoint = os.getenv("MRC_CHECKPOINT")
            _reader = MRCClient(checkpoint) if checkpoint else LexicalBaselineClient()
    return _retriever, _reader


def get_speech_engine():
    global _tts_engine
    if _tts_engine is None:
        with _service_lock:
            if _tts_engine is None:
                engine_name = os.getenv("TTS_ENGINE", "edge")
                try:
                    _tts_engine = get_tts_engine(engine_name)
                except ValueError as exc:
                    raise HTTPException(status_code=503, detail=str(exc)) from exc
    return _tts_engine


@app.get("/api/health")
def health() -> dict:
    return {
        "status": "ok",
        "retrieval": "configured" if os.getenv("QA_INDEX") else "demo_corpus",
        "reader": "trained" if os.getenv("MRC_CHECKPOINT") else "lexical_baseline",
        "tts_engine": os.getenv("TTS_ENGINE", "edge"),
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
def synthesize(request: TTSRequest) -> FileResponse:
    engine = get_speech_engine()
    temp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    output_path = temp.name
    temp.close()
    try:
        engine.synthesize(request.text.strip(), output_path)
    except Exception as exc:
        Path(output_path).unlink(missing_ok=True)
        raise HTTPException(status_code=502, detail=f"TTS synthesis failed: {exc}") from exc
    return FileResponse(
        output_path,
        media_type="audio/mpeg",
        filename="answer.mp3",
        background=BackgroundTask(Path(output_path).unlink, missing_ok=True),
    )
