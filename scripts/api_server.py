"""Unified FastAPI backend for the ViMMRC voice Q&A web application.

Integrates:
- STT: Faster-Whisper (speech-to-text_Luong)
- Retrieval: BM25 Retriever over ViMMRC 2.0 articles (retrieval-model_Huy)
- MRC: fine-tuned ViT5 answer generator (mrc-model_Huy)
- Dialogue: multi-turn conversation layer (dialogue-manager_Huy): small talk, follow-up
  rewriting, comparison / multi-part / yes-no questions, full-sentence answers for TTS
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
    "scripts",  # intent_router; pytest.ini đã thêm, nhưng `uvicorn scripts.api_server:app` thì không
    "dialogue-manager_Huy",
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
from intent_router import ConversationalIntentRouter, polish_answer, rerank_hits
from dialogue import DialogueManager
from llm_assist import LLMAssist

from synthesize import synthesize as tts_synthesize
import stt_server

app = stt_server.app
# LLM_ASSIST=0 tắt; bật mà Ollama không chạy thì tự bỏ qua, hệ thống chạy như cũ
_assist = LLMAssist(enabled=os.getenv("LLM_ASSIST", "1") != "0")
stt_server.POST_PROCESS = _assist.fix_transcript
app.title = "ViMMRC Voice Q&A API"

_service_lock = Lock()
_retriever: Retriever | None = None
_reader = None
_dialogue: DialogueManager | None = None

# Kho kiến thức mẫu (~75 đoạn) dùng khi chưa có data/: đủ để demo hội thoại ngoài hộp.
SEED_KB = ROOT / "dialogue-manager_Huy" / "eval" / "seed_kb.json"


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


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    session_id: str | None = Field(default=None, max_length=100)
    passage: str | None = Field(default=None, max_length=100_000)

    @field_validator("question")
    @classmethod
    def question_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("question must not be blank")
        return value


class ResetRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=100)


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


def find_default_checkpoint() -> str | None:
    """Auto-discover the best trained MRC ViT5 checkpoint if available."""
    candidates = [
        ROOT / "mrc-model_Huy" / "checkpoints" / "vit5-combined-cont",
        ROOT / "mrc-model_Huy" / "checkpoints" / "vit5-combined",
        ROOT / "mrc-model_Huy" / "checkpoints" / "vit5-vimmrc-ft",
        ROOT / "models_and_checkpoints" / "mrc_vit5_combined",
    ]
    for cand in candidates:
        if cand.is_dir() and (cand / "config.json").exists() and any(
            (cand / name).exists() for name in ("model.safetensors", "pytorch_model.bin")
        ):
            return str(cand)
    return None


def get_qa_services() -> tuple[Retriever, object]:
    """Load index and reader with fallbacks and auto-discovery."""
    global _retriever, _reader
    if _retriever is not None and _reader is not None:
        return _retriever, _reader

    with _service_lock:
        if _retriever is None:
            index_path = os.getenv("QA_INDEX")
            kb_index = ROOT / "data" / "kb_index.json"
            default_index = ROOT / "data" / "vimmrc_index.json"
            wiki_dir = os.getenv("KB_WIKI") or (
                str(ROOT / "data" / "kb_wiki_full") if (ROOT / "data" / "kb_wiki_full").is_dir() else None
            )
            ratio = float(os.getenv("KB_WIKI_RATIO", "0.4"))
            reranker = os.getenv("KB_RERANKER") or None

            if index_path and Path(index_path).exists():
                _retriever = load_any(index_path, wiki_dir, ratio, reranker)
            elif kb_index.exists():
                _retriever = load_any(str(kb_index), wiki_dir, ratio, reranker)
            elif default_index.exists():
                _retriever = Retriever.load(str(default_index))
            else:
                import json
                _retriever = Retriever(json.loads(SEED_KB.read_text(encoding="utf-8")))

        if _reader is None:
            checkpoint = os.getenv("MRC_CHECKPOINT")
            if checkpoint and checkpoint.lower() in ("lexical", "baseline", "none"):
                _reader = LexicalBaselineClient()
            elif checkpoint and Path(checkpoint).exists():
                _reader = MRCClient(checkpoint, context_strategy=os.getenv("MRC_CONTEXT_STRATEGY", "question_chunks"))
            else:
                default_ckpt = find_default_checkpoint()
                if default_ckpt:
                    try:
                        _reader = MRCClient(default_ckpt, context_strategy=os.getenv("MRC_CONTEXT_STRATEGY", "question_chunks"))
                    except Exception:
                        _reader = LexicalBaselineClient()
                else:
                    _reader = LexicalBaselineClient()

    return _retriever, _reader


def get_dialogue() -> DialogueManager:
    global _dialogue
    if _dialogue is None:
        retriever, reader = get_qa_services()
        with _service_lock:
            if _dialogue is None:
                _dialogue = DialogueManager(retriever, reader, assist=_assist,
                                            min_support=float(os.getenv("DIALOGUE_MIN_SUPPORT", "0.34")))
    return _dialogue


@app.get("/api/health")
def health() -> dict:
    retriever, reader = get_qa_services()
    if os.getenv("QA_INDEX"):
        index_source = "custom_index"
    elif (ROOT / "data" / "kb_index.json").exists():
        index_source = "kb_corpus"
    elif (ROOT / "data" / "vimmrc_index.json").exists():
        index_source = "vimmrc_corpus"
    else:
        index_source = "demo_corpus"

    is_vit5 = reader.__class__.__name__ == "MRCClient"
    dist_browser = ROOT / "web-interface_Luong" / "dist" / "web-interface" / "browser"
    return {
        "status": "ok",
        "retrieval": index_source,
        "retrieval_passages": len(retriever.passages),
        "reader": "trained_vit5" if is_vit5 else "lexical_baseline",
        "dialogue": True,
        "llm_assist": _assist.available(),
        "tts_engine": os.getenv("TTS_ENGINE", "matcha"),
        "frontend_served": dist_browser.exists() and (dist_browser / "index.html").exists(),
    }


@app.post("/api/retrieve")
def retrieve(request: RetrieveRequest) -> dict:
    conv_resp = ConversationalIntentRouter.get_conversational_response(request.question)
    if conv_resp:
        return {
            "passages": [
                {
                    "id": "intent:conversational",
                    "text": conv_resp,
                    "score": 100.0,
                }
            ]
        }
    retriever, _ = get_qa_services()
    candidate_k = max(request.top_k * 2, 5)
    raw_hits = retriever.search(request.question, top_k=candidate_k)
    hits = rerank_hits(request.question, raw_hits, top_k=request.top_k)
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
    conv_resp = ConversationalIntentRouter.get_conversational_response(request.question)
    if conv_resp:
        return {"answer": conv_resp}
    _, reader = get_qa_services()
    raw_answer = reader.answer_question(request.question, request.passage)
    return {"answer": polish_answer(raw_answer, request.question)}


@app.post("/api/ask")
def ask(request: AskRequest) -> dict:
    """Một lượt hội thoại: xã giao, câu nối tiếp, so sánh, câu ghép, đúng/sai, hỏi đáp thường.

    Giữ ngữ cảnh theo session_id (trả về ở lượt đầu, gửi lại ở các lượt sau)."""
    result = get_dialogue().respond(request.question, request.session_id, request.passage)
    passage = result.get("passage")
    return {
        "answer": result["answer"],
        "kind": result["kind"],
        "intent": result.get("intent"),
        "session_id": result["session_id"],
        "resolved_question": result.get("resolved_question"),
        "passage": {"id": passage.get("id"), "text": passage.get("text"), "score": passage.get("score")} if passage else None,
        "parts": [{"question": p.get("resolved_question"), "answer": p.get("answer"), "kind": p.get("kind")}
                  for p in result.get("parts", [])],
    }


@app.post("/api/ask/reset")
def ask_reset(request: ResetRequest) -> dict:
    get_dialogue().reset(request.session_id)
    return {"status": "ok"}


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
